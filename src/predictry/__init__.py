from utils.config import config
from utils.log.logger import Logger


Logger.setup_logging(config["log_config_file"])