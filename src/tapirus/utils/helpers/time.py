__author__ = 'guilherme'

import datetime


def unix_time_seconds(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return unix_time_seconds(dt) * 1000.0