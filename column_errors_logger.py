import logging
from datetime import datetime
import atexit

# example usage:
# from column_errors_logger import logger
# logger.debug("long message that should be wrapped in the log according to the autowrap function")
# extra = {'pre_wrapped': "This is a pre-wrapped error message.\nIt has multiple lines already."}
# logger.debug("", extra=extra)

def autowrap(message, width=80):
    import textwrap
    return '\n'.join(textwrap.wrap(message, width))

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Create the header line with standard logging features
        header = super().format(record)
        # Check if the record has a pre-wrapped message
        if hasattr(record, 'pre_wrapped'):
            wrapped_message = record.pre_wrapped
        else:
            # Auto-wrap the message
            wrapped_message = autowrap(record.getMessage())
        # Combine header and wrapped message
        return f"{header}\n{wrapped_message}"

# Create a logger that will be accessible from other modules
logger = logging.getLogger('column_errors_logger')
logger.setLevel(logging.DEBUG)  # Set the logger level

# Create handlers
stream_handler = logging.StreamHandler()

# Create a unique filename with a timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'logfile_{timestamp}.log'
file_handler = logging.FileHandler(log_filename)

# Use the custom formatter
formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# Function to flush and close log handlers
def close_log_handlers():
    for handler in logger.handlers:
        handler.flush()
        handler.close()
    print("Closed log file: ", log_filename)

# Register the function to be called on exit
atexit.register(close_log_handlers)

def example_usage():
    logger.debug('This is a debug message that should be wrapped according to the autowrap function.')
    logger.info('This is an info message that should be wrapped according to the autowrap function.')
    logger.warning('This is a warning message that should be wrapped according to the autowrap function.')
    logger.error('This is an error message that should be wrapped according to the autowrap function.')
    logger.critical('This is a critical message that should be wrapped according to the autowrap function.')

    # Example of logging a pre-wrapped message
    pre_wrapped = "This is a pre-wrapped error message.\nIt has multiple lines already."
    extra = {'pre_wrapped': pre_wrapped}
    logger.error('This is an error message with a pre-wrapped body.', extra=extra)

    # the global column_errors dictionary