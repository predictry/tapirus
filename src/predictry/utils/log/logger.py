__author__ = 'guilherme'

import os
import json
import logging.config

class Logger:

    @classmethod
    def setup_logging(cls, default_path, default_level=logging.INFO, env_key='LOG_CFG'):
        """Setup logging configuration

        """
        if os.path.exists(default_path):
            path = default_path
            value = os.getenv(env_key, None)
            if value:
                path = value
            if os.path.exists(path):
                with open(path, 'rt') as f:
                    config = json.load(f)
                logging.config.dictConfig(config)
            else:
                logging.basicConfig(level=default_level)

            predictry = logging.getLogger(__name__)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        logger = logging.getLogger('predictry')
        logger.info(msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        logger = logging.getLogger('predictry')
        logger.debug(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        logger = logging.getLogger('predictry')
        logger.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        logger = logging.getLogger('predictry')
        logger.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        logger = logging.getLogger('predictry')
        logger.critical(msg, *args, **kwargs)
