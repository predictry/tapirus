__author__ = 'guilherme'

import abc

class ResourceQueryGeneratorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, args):

        return

    @abc.abstractmethod
    def read(self, args):

        return

    @abc.abstractmethod
    def update(self, args):

        return

    @abc.abstractmethod
    def delete(self, args):

        return