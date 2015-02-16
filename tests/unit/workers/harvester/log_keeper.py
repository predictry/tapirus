__author__ = 'guilherme'


import unittest
from tapirus.operator import log_keeper


class TestLogKeeper(unittest.TestCase):

    files = ["test_file.txt", "test_file2.txt"]

    def test_01_should_add_file_to_list(self):

        print("Testing addition of files to LogKeeper's list")

        log_keeper.add_log_keeper_file(self.files[0])

        files = log_keeper.get_log_keeper_files()
        assert self.files[0] in files

        log_keeper.add_log_keeper_file(self.files[1])

        files = log_keeper.get_log_keeper_files()
        assert self.files[1] in files

    def test_02_should_remove_file_from_list(self):

        print("Testing removal of files to LogKeeper's list")

        log_keeper.remove_log_keeper_file(self.files[0])

        files = log_keeper.get_log_keeper_files()
        assert self.files[0] not in files

        log_keeper.remove_log_keeper_file(self.files[1])

        files = log_keeper.get_log_keeper_files()
        assert self.files[1] not in files