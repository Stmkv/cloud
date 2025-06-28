import logging

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


def start_logger():
    logger = logging.getLogger("Bot")
    FORMAT = LOG_DEFAULT_FORMAT
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
    )

    return logger
