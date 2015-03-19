__author__ = 'guilherme'

import threading
import multiprocessing.context


def repeat(interval, worker_function, iterations=0):
    if iterations != 1:
        threading.Timer(interval, repeat, [interval, worker_function, 0 if iterations == 0 else iterations-1]).start()

    job = multiprocessing.context.Process(target=worker_function)
    job.start()