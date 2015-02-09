__author__ = 'guilherme'


import unittest
from tapirus.workers import harvester


class TestLogKeeper(unittest.TestCase):

    files = ["test_file.txt", "test_file2.txt"]

    def test_01_should_add_file_to_list(self):

        print("Testing addition of files to LogKeeper's list")

        harvester.add_log_keeper_file(self.files[0])

        files = harvester.get_log_keeper_files()
        assert self.files[0] in files

        harvester.add_log_keeper_file(self.files[1])

        files = harvester.get_log_keeper_files()
        assert self.files[1] in files

    def test_02_should_remove_file_from_list(self):

        print("Testing removal of files to LogKeeper's list")

        harvester.remove_log_keeper_file(self.files[0])

        files = harvester.get_log_keeper_files()
        assert self.files[0] not in files

        harvester.remove_log_keeper_file(self.files[1])

        files = harvester.get_log_keeper_files()
        assert self.files[1] not in files