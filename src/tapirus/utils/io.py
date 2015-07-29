import datetime
import os
import json


def delete_file(file_path):
    """

    :param file_path:
    :return:
    """

    # todo: check for IO errors/exceptions
    # todo: return True/False

    os.remove(file_path)


def parse_date(d):
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        raise


def parse_hour(h):
    try:
        return datetime.datetime.strptime(h, "%H")
    except ValueError:
        raise


def parse_timestamp(date, hour):
    string = '-'.join([date, hour])

    try:

        return datetime.datetime.strptime(string, "%Y-%m-%d-%H")
    except ValueError:
        raise


def validate_hour(h):
    try:
        datetime.datetime.strptime(h, "%H")
        return True
    except ValueError:
        return False


def validate_date(d):
    try:
        datetime.datetime.strptime(d, "%Y-%m-%d")
        return True
    except ValueError:
        return False


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
