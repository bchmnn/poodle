import logging
from typing import Optional


class Loggable:
    logger: logging.Logger

    def __init__(
        self,
        name: str,
        level: int = logging.ERROR,
        stream_handler: Optional[logging.StreamHandler] = None,
    ):
        self.logger: logging.Logger = logging.getLogger()
        if stream_handler is None:
            stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        stream_handler.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(level)
