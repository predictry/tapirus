import threading
import multiprocessing.context


def repeat(interval, worker_function, args=(), wait=True, iterations=0):

    job = multiprocessing.context.Process(target=worker_function, args=args)
    job.start()

    if wait:
        job.join()

    if iterations != 1:
        thread = threading.Timer(interval, repeat, [interval, worker_function, args, 0 if iterations == 0 else iterations-1])
        thread.start()