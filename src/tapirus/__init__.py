from tapirus.utils import config
from tapirus.utils.logger import Logger

conf = config.load_configuration()
Logger.setup_logging(conf["log_config_file"])


#todo: create models to manage data
#todo: assign a UUID to every entity
#todo: process log file
#todo: update flask restful
#todo: create batch endpoints