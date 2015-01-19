__author__ = 'guilherme'

from tapirus.utils.threading import mp
from tapirus.engine.compute.services.workers import trending

if __name__ == "__main__":
    mp.repeat(60*10, trending.run)
