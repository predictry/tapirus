__author__ = 'guilherme'


import os
import os.path
import csv


SRC_ROOT = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(SRC_ROOT, "../../../keys.csv")


def get_tenant_prediction_access_key(tenant_name):

    keys = dict()

    with open(KEYS_FILE, "r") as fp:

        reader = csv.reader(fp)

        for row in reader:

            _, tenant, access_key = row

            keys[tenant] = access_key

    if tenant_name in keys:

        return keys[tenant_name]
    else:
        return None
