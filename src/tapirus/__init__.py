import os.path

from tapirus.utils import config
from tapirus.utils.logger import Logger


logging = config.get("logging")

Logger.setup_logging(os.path.join(config.PROJECT_BASE, logging["logconfig"]))
