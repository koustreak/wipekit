from wipekit.logging import get_logger, configure_logger

configure_logger()

logger = get_logger("wipekit.anonymization")
logger.error("Hello world!")

