__author__ = 'guilherme'

from flask_restful import Resource
from flask import request
from predictry.utils.log.logger import Logger


class BlueprintBase(Resource):

    def __init__(self):

        if request:
            method = str(request.method)
            full_path = str(request.full_path)
            remote_addr = str(request.remote_addr)
            Logger.info(method + " [" + full_path + "] from [" + remote_addr + "]")
        super(BlueprintBase, self).__init__()