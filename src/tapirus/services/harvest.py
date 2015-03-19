__author__ = 'guilherme'


from tapirus.utils import multitasking
from tapirus.workers import harvester
from tapirus.utils import config


if __name__ == "__main__":

    conf = config.load_configuration()

    if conf:

        interval = conf["app"]["intervals"]["harvester"]
        multitasking.repeat(interval, harvester.run, wait=True)
