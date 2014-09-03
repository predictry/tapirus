__author__ = 'guilherme'

import threading
from multiprocessing import Pool

def repeat(interval, worker_function, iterations=0):
    if iterations != 1:
        threading.Timer(interval, repeat, [interval, worker_function, 0 if iterations == 0 else iterations-1]).start()

    worker_function()


def run_in_background(processes, worker_function):
    pool = Pool(processes=processes)
    pool.apply_async(worker_function)