import os
import os.path
import requests
import requests.exceptions
from tapirus.utils.logger import Logger

LOG_KEEPER_FILE_NAME = "data/log.keeper.list.db"
LOG_KEEPER_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../{0}".format(LOG_KEEPER_FILE_NAME))


def notify_log_keeper(url, file_name, status):
    """

    :param file_name:
    :param status:
    :return:
    """

    uri = '/'.join([url, file_name])
    payload = dict(status=status)

    try:
        response = requests.put(url=uri, json=payload)
    except requests.exceptions.ConnectionError as e:
        Logger.error("Connection error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    except requests.exceptions.HTTPError as e:
        Logger.error("HTTP error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    except Exception as e:
        Logger.error("Unexpected error while trying to notify LogKeeper@{0}:\n\t{1}".format(uri, e))
        return False
    else:

        if response.status_code != 200:

            Logger.error("LogKeeper@{0} Response:\n\t`{1}`".format(uri, response.status_code))
            return False

        else:

            Logger.info("Notified LogKeeper of processed file `{0}`".format(file_name))
            return True


def notify_log_keeper_of_backlogs(url):
    """
    Tries notify the log keeper of all files in the waiting list
    :return:
    """

    file_names = get_log_keeper_files()

    for file_name in file_names:

        if notify_log_keeper(url, file_name, status="processed"):
            remove_log_keeper_file(file_name)


def add_log_keeper_file(file_name):
    """
    Adds a file to the list of files to notify the log keeper about
    :param file_name:
    :return:
    """

    files_names = get_log_keeper_files()

    if file_name not in files_names:

        with open(LOG_KEEPER_DB, "a+", encoding="UTF-8") as f:
            f.write(''.join([file_name, "\n"]))


def remove_log_keeper_file(file_name):
    """
    Removes a file from the log keeper's pending notification list
    :param file_name:
    :return:
    """

    files_names = get_log_keeper_files()

    #if file is present, remove it
    if file_name in files_names:
        files_names.remove(file_name)

        #update file (or just re-write it)
        with open(LOG_KEEPER_DB, "w+", encoding="UTF-8") as f:
            for file_name in set(files_names):
                f.write(''.join([file_name, "\n"]))


def get_log_keeper_files():
    """
    Gets the list of files pending notification to the log keeper
    :return:
    """

    file_names = []

    if os.path.exists(LOG_KEEPER_DB):

        with open(LOG_KEEPER_DB, "r", encoding="UTF-8") as f:

            for line in f:
                file_names.append(line.strip())

    return file_names

