"""Generic queue handler for RabbitMQ or SQS with batching and retries.

This module supports consuming messages from either RabbitMQ or Amazon SQS.
It provides batching, retry logic, graceful shutdown handling, and clean logging
with optional redaction of sensitive values.
"""

import json
import signal
import threading
import time
from collections.abc import Callable

import boto3
import pika
from botocore.exceptions import BotoCoreError, NoCredentialsError
from pika.adapters.blocking_connection import BlockingChannel
from tenacity import retry, stop_after_attempt, wait_exponential

import app.config_shared as config
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)
shutdown_event = threading.Event()

REDACT_SENSITIVE_LOGS = (
    config.get_config_value_cached("REDACT_SENSITIVE_LOGS", "true").lower() == "true"
)


def safe_log(msg: str) -> str:
    """Standardized redacted log message helper.

    Args:
        msg (str): Message to redact if sensitive logging is enabled.

    Returns:
        str: Either the original message or a redacted form.

    """
    return f"{msg}: [REDACTED]" if REDACT_SENSITIVE_LOGS else msg


def consume_messages(callback: Callable[[list[dict]], None]) -> None:
    """Start the message consumer using the configured QUEUE_TYPE.

    This method determines whether to use RabbitMQ or SQS and invokes the
    appropriate listener. It also registers signal handlers for graceful shutdown.

    Args:
        callback (Callable[[list[dict]], None]): Processing function for a batch of messages.

    Raises:
        ValueError: If QUEUE_TYPE is not supported.

    """
    signal.signal(signal.SIGINT, _graceful_shutdown)
    signal.signal(signal.SIGTERM, _graceful_shutdown)

    queue_type = config.get_queue_type().lower()
    if queue_type == "rabbitmq":
        _start_rabbitmq_listener(callback)
    elif queue_type == "sqs":
        _start_sqs_listener(callback)
    else:
        raise ValueError("Unsupported QUEUE_TYPE: [REDACTED]")


def _graceful_shutdown(signum, frame) -> None:
    """Gracefully signal shutdown of the consumer loop.

    Args:
        signum: Signal number.
        frame: Current stack frame.

    """
    logger.info("🛑 Shutdown signal received, stopping listener...")
    shutdown_event.set()


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def _start_rabbitmq_listener(callback: Callable[[list[dict]], None]) -> None:
    """Connect to RabbitMQ and start consuming messages from the configured queue.

    Args:
        callback (Callable[[list[dict]], None]): Handler function for batches of messages.

    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.get_rabbitmq_host(),
            port=config.get_rabbitmq_port(),
            virtual_host=config.get_rabbitmq_vhost(),
            credentials=pika.PlainCredentials(
                config.get_rabbitmq_user(), config.get_rabbitmq_password()
            ),
        )
    )
    channel = connection.channel()
    queue_name = config.get_rabbitmq_queue()
    channel.queue_declare(queue=queue_name, durable=True)

    def on_message(ch: BlockingChannel, method, properties, body: bytes) -> None:
        """Callback invoked for each incoming RabbitMQ message.

        Args:
            ch (BlockingChannel): The channel object.
            method: Delivery method.
            properties: Message properties.
            body (bytes): Raw message body.

        """
        if shutdown_event.is_set():
            ch.stop_consuming()
            return

        try:
            message = json.loads(body)
            callback([message])
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug("✅ RabbitMQ message processed and acknowledged.")
        except Exception:
            logger.error("❌ RabbitMQ message processing failed (details redacted)")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    logger.info(safe_log("🚀 Consuming RabbitMQ messages from queue"))

    try:
        channel.basic_qos(prefetch_count=config.get_batch_size())
        channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=False)

        while not shutdown_event.is_set():
            connection.process_data_events(time_limit=1)
    finally:
        connection.close()
        logger.info("🛑 RabbitMQ listener stopped.")


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def _start_sqs_listener(callback: Callable[[list[dict]], None]) -> None:
    """Connect to AWS SQS and start polling messages.

    Args:
        callback (Callable[[list[dict]], None]): Handler function for a batch of messages.

    """
    sqs = boto3.client("sqs", region_name=config.get_sqs_region())
    queue_url = config.get_sqs_queue_url()

    logger.info(safe_log("🚀 Polling SQS queue"))

    while not shutdown_event.is_set():
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=config.get_batch_size(),
                WaitTimeSeconds=10,
            )
            messages = response.get("Messages", [])
            if not messages:
                continue

            payloads = []
            receipt_handles = []

            for msg in messages:
                try:
                    payload = json.loads(msg["Body"])
                    payloads.append(payload)
                    receipt_handles.append(msg["ReceiptHandle"])
                except Exception:
                    logger.warning("⚠️ Failed to parse SQS message body (redacted)")

            if payloads:
                callback(payloads)
                for handle in receipt_handles:
                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=handle)
                logger.debug("✅ SQS: Processed and deleted %d message(s)", len(payloads))

        except (BotoCoreError, NoCredentialsError):
            logger.error("❌ SQS error encountered (details redacted)")
            time.sleep(5)

    logger.info("🛑 SQS polling stopped.")
