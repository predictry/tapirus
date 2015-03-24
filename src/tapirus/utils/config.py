__author__ = 'guilherme'

import os
import os.path
import configparser

from tapirus.core import errors

PROJECT_BASE = ''.join([os.path.dirname(os.path.abspath(__file__)), "/../../../"])
CONFIG_FILE = ''.join([PROJECT_BASE, 'config.ini'])


def get(section, option=None, type=None):

    config = configparser.ConfigParser()

    with open(CONFIG_FILE, "r") as fp:
        config.read_file(fp)

        if option:

            try:
                value = config.get(section, option)
            except configparser.NoOptionError as exc:
                raise errors.ConfigurationError(exc)
            else:

                if type and hasattr(type, '__call__'):
                    return type(value)
                else:
                    return value
        else:

            try:
                data = dict(config.items(section))
            except configparser.NoSectionError as exc:
                raise errors.ConfigurationError(exc)
            else:
                return data

'''
def load_configuration():

    if os.path.isfile(CONFIG_FILE):

        with open(CONFIG_FILE, 'r') as f:

            contents = ''.join(f.readlines())

            try:
                conf = json.loads(contents)
            except ValueError as err:
                print("[{0}] There was an error reading the '{1}' file: \n\t'{2}'".format(__name__, CONFIG_FILE, err))
                return None

            if "log_config_file_name" in conf:
                conf["log_config_file"] = conf["log_config_file_name"]

            return conf

    else:
        return None
'''