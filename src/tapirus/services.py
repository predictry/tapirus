__author__ = 'guilherme'

from tapirus.utils import threads
from tapirus.workers import harvester
from tapirus.utils import config


if __name__ == "__main__":

    conf = config.load_configuration()

    if conf:

        timeout = conf["app"]["intervals"]["harvester"]
        threads.repeat(timeout, harvester.run)
