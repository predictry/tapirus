__author__ = 'guilherme'

import os
import json

PROJECT_BASE = ''.join([os.path.dirname(os.path.abspath(__file__)), "/../"])
CONFIG_FILE = ''.join([PROJECT_BASE, 'server-config.json'])

config = dict()


def load_configuration():

    if os.path.isfile(CONFIG_FILE):

        f = open(CONFIG_FILE, 'r')

        contents = ''.join(f.readlines())

        global config
        config = json.loads(contents)

        if "log_config_file_name" in config:
            config["log_config_file"] = ''.join([PROJECT_BASE, config["log_config_file_name"]])

load_configuration()