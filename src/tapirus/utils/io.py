__author__ = 'guilherme'

import os


def delete_file(file_path):
    """

    :param file_path:
    :return:
    """

    #todo: check for IO errors/exceptions
    #todo: return True/False

    os.remove(file_path)

