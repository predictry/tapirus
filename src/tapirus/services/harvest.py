__author__ = 'guilherme'


from tapirus.utils import multitasking
from tapirus.workers import harvester
from tapirus.utils import config


if __name__ == "__main__":

    harv = config.get("harvester")

    interval = int(harv["interval"])
    multitasking.repeat(interval, harvester.run, wait=True)
