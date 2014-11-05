'''
Created on 10 Jul, 2014

@author: frost
'''
import abc

class QueryExecutorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self, query, params):
        
        return