import logging


class LoggerSetup:
    """Handles logging configuration for the gardenlinux library."""

    @staticmethod
    def get_logger(name, level=None):
        """Create and configure a logger.

        Args:
            name: Name for the logger, typically in format 'gardenlinux.module'
            level: Logging level, defaults to INFO if not specified

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Only add handler if none exists to prevent duplicate handlers
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Set default level if specified
            if level is not None:
                logger.setLevel(level)
            else:
                logger.setLevel(logging.INFO)

        return logger
