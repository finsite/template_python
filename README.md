# Template

## Overview

This is a generic template for a Python application. Please update the details as necessary to fit your project.

## Getting Started

Provide a brief description of the application and its purpose.

### Prerequisites

List any prerequisites needed to run the application.

```markdown
Each script supports error logging by default. This feature is optional and can be enabled for debugging purposes.

Example files are included with each script. Use the command `get-help <scriptname>` to view examples.
```

## Installation

1. Clone the repository.
2. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

   ```

## Environment Variables

Define any necessary environment variables for the application:

- `STOCK_API_TYPE`: Type of stock API to use (e.g., `yfinance`, `alpha_vantage`, `polygon`). Default: `yfinance`.
- `QUEUE_TYPE`: Type of queue for data transfer (`sqs` or `rabbitmq`). Default: `sqs`.
- `SQS_QUEUE_URL`: URL of the SQS queue (required if `QUEUE_TYPE=sqs`).
- `RABBITMQ_HOST`: RabbitMQ server address (default: `localhost`).
- `RABBITMQ_QUEUE_NAME`: Name of the RabbitMQ queue (default: `stock_queue`).

## Example .env File

Provide an example `.env` file to illustrate environment variable configuration.

## Running the Tests

Explain how to execute the tests for the application.

## Deployment

Document the deployment process, including any required parameters and instructions.

## Built With

- [Visual Studio Code](https://code.visualstudio.com/)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for improvements.

## Authors

- **Mark Quinn** - [Mobious999](https://github.com/mobious999)
- **Jason Qualkenbush** - [jasonqualkenbush](https://github.com/jasonqualkenbush)

## License

This project is licensed under the Apache 2.0 License.

## Acknowledgments

Include any references or acknowledgments here.
