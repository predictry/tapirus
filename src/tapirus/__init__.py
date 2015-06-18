from tapirus.utils import config
from tapirus.utils.logger import Logger


logging = config.get("logging")

Logger.setup_logging(logging["logconfig"])
