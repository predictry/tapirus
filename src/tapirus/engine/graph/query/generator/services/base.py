__author__ = 'guilherme'

import abc


class ProcessQueryGeneratorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self, args):

        return
