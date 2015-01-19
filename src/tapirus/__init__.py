from tapirus.utils import config
from tapirus.utils.log.logger import Logger

conf = config.load_configuration()
Logger.setup_logging(conf["log_config_file"])