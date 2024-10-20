import logging
from datetime import datetime
import atexit

class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_format = f"{record.levelname}: {record.message}"
        return log_format

class CustomErrorsLogger(logging.Logger):
    def __init__(self, name, level=logging.DEBUG):
        super().__init__(name, level)
        
        # Create handlers
        stream_handler = logging.StreamHandler()

        # Create a unique filename with a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_filename = f'logfile_{timestamp}.log'
        file_handler = logging.FileHandler(self.log_filename)

        # Use the custom formatter
        formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s')
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(stream_handler)
        self.addHandler(file_handler)

        # Register the function to be called on exit
        atexit.register(self.close_log_handlers)

    def flush(self):
        for handler in self.handlers:
            handler.flush()

    def close_log_handlers(self):
        for handler in self.handlers:
            handler.flush()
            handler.close()
        print("Closed log file: ", self.log_filename)

# Set the custom logger class
logging.setLoggerClass(CustomErrorsLogger)

# Create an instance of the custom logger
logger = logging.getLogger("custom_errors_logger")

# Set the logging level
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":

    # Example usage
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Flush the logs
    logger.flush()
