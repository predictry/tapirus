from tapirus.utils import config
from tapirus.utils.logger import Logger

conf = config.load_configuration()

if conf:
    Logger.setup_logging(conf["log_config_file"])


#todo: assign a UUID to every entity?
#todo: update flask restful
#todo: create batch endpoints
#todo: centralized logging