__author__ = 'guilherme'

import re

from tapirus.api.v1.errors import error
from tapirus.utils.logger import Logger


NEO_VAR_NAME_REGEX = "^[a-zA-Z]{1,}(_){0,}([a-zA-Z0-9]{0,})?$"
POSITIVE_INTEGER_REGEX = "^\d+$"
NUMBER_REGEX = "(?:\d*\.)?\d+"
EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@" \
              "((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"

#validate: fields, limit, offset, domain, appid

re.compile(NEO_VAR_NAME_REGEX)
re.compile(POSITIVE_INTEGER_REGEX)
re.compile(NUMBER_REGEX)
re.compile(EMAIL_REGEX)


def parse_params(args, data=None, endpoint=None):
    if 'appid' not in args:
        return error('MissingParameter', property='appid')
    if not args['appid']:
        return error('UndefinedParameter', property='appid')
    if 'domain' not in args:
        return error('MissingParameter', property='domain')
    if not args['domain']:
        return error('UndefinedParameter', property='domain')

    #domain
    if not re.match(NEO_VAR_NAME_REGEX, args['domain']):
        err = error('InvalidParameter', property='domain', message="The value should be valid for the regex: %s"
                                                                   % NEO_VAR_NAME_REGEX)
        Logger.info(err)
        return err

    #fields
    if "fields" in args:
        fields = args["fields"].split(",")

        for field in fields:
            if not re.match(NEO_VAR_NAME_REGEX, field):
                err = error('InvalidParameter', property=field, message="The value should be valid for the regex: %s"
                                                                        % NEO_VAR_NAME_REGEX)
                Logger.info(err)
                return err

    #limit
    if "limit" in args:
        if not re.match(POSITIVE_INTEGER_REGEX, args["limit"]):
            err = error('InvalidParameter', property="limit", message="The value should be valid for the regex: %s"
                                                                      % POSITIVE_INTEGER_REGEX)
            Logger.info(err)
            return err

        args["limit"] = int(args["limit"])

    #offset
    if "offset" in args:
        if not re.match(POSITIVE_INTEGER_REGEX, args["offset"]):
            err = error('InvalidParameter', property="offset", message="The value should be valid for the regex: %s"
                                                                       % POSITIVE_INTEGER_REGEX)
            Logger.info(err)
            return err

        args["offset"] = int(args["offset"])


    if data and type(data) is dict:

        if "email" in data:
            if not re.match(EMAIL_REGEX, data["email"]):
                err = error('InvalidParameter', property="email", message="The value should be valid for the regex: %s"
                                                                           % EMAIL_REGEX)
                Logger.info(err)
                return err


        #customized validation
        if endpoint:
            if endpoint == "actions":
                if "type" in args:
                    if not re.match(NEO_VAR_NAME_REGEX, args["type"]):
                        err = error('InvalidParameter', property="type", message="The value should be valid for the regex: %s"
                                                                                   % NEO_VAR_NAME_REGEX)
                        Logger.info(err)
                        return err

                if "type" in data:
                    if not re.match(NEO_VAR_NAME_REGEX, data["type"]):
                        err = error('InvalidParameter', property="type", message="The value should be valid for the regex: %s"
                                                                                   % NEO_VAR_NAME_REGEX)
                        Logger.info(err)
                        return err


    return None