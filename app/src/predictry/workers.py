__author__ = 'guilherme'

from predictry.utils.threading import mp
from predictry.engine.compute.services.workers import trending

if __name__ == "__main__":
    mp.repeat(60*10, trending.run)
