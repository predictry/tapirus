__author__ = 'guilherme'

from predictry.utils.log.logger import Logger
from predictry.api.v1.errors import error
from flask_restful import Resource
from flask import request, make_response, jsonify


class BlueprintBase(Resource):

    def __init__(self):

        if request:
            method = str(request.method)
            full_path = str(request.full_path)
            remote_addr = str(request.remote_addr)
            Logger.info(method + " [" + full_path + "] from [" + remote_addr + "]")
        super(BlueprintBase, self).__init__()


def validate_request(args):

    if 'appid' not in args:
        return error('MissingParameter', property='appid')
    if not args['appid']:
        return error('UndefinedParameter', property='appid')
    if 'domain' not in args:
        return error('MissingParameter', property='domain')
    if not args['domain']:
        return error('UndefinedParameter', property='domain')

    return None