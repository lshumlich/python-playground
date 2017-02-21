import logging
from io import StringIO


class AppLogger:

    def __init__(self):
        # Starts Logging when class is initiated

        self.stream = StringIO()
        logger = logging.getLogger()
        # logger.level = logging.INFO
        # logger.level = logging.DEBUG
        self.stream_handler = logging.StreamHandler(self.stream)
        logger.addHandler(self.stream_handler)

    def stop_capture(self):

        logger = logging.getLogger()
        logger.removeHandler(self.stream_handler)

        self.stream.flush()
        return self.stream.getvalue()
