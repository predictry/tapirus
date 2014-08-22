__author__ = 'guilherme'

from predictry.api.v1.errors import error
from predictry.utils.log.logger import Logger
import re

domain_regex = "^[a-zA-Z]{1,}([a-zA-Z0-9]{0,})?$"
re.compile(domain_regex)


def validate_request(args):
    if 'appid' not in args:
        return error('MissingParameter', property='appid')
    if not args['appid']:
        return error('UndefinedParameter', property='appid')
    if 'domain' not in args:
        return error('MissingParameter', property='domain')
    if not args['domain']:
        return error('UndefinedParameter', property='domain')


    if not re.match(domain_regex, args['domain']):
        err = error('InvalidParameter', property='domain')
        Logger.info(err)
        return err

    return None
