def add_numbers(a, b):
    """Adds two numbers and returns the result."""
    return a + b


def unused_function():
    """This function is intentionally left unused to test Pylint warnings."""
    pass


class ExampleClass:
    """A simple example class."""

    def __init__(self, value):
        self.value = value

    def get_value(self):
        """Returns the value."""
        return self.value
