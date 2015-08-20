import unittest
import os.path

from tapirus.utils import config
from tapirus.core import errors


class ConfigurationFileTest(unittest.TestCase):

    sample_config = {
        'database': {
            'username': 'user',
            'password': 'password',
            'host': 'localhost',
            'port': 1234
        },
        's3': {
            'bucket': 'bucket-name',
            'prefix': 'mystore'
        },
        'sample': {
            'complex': 5 + 7j,
            'float': 4.67,
            'bool': False,
            'bool2': True
        }
    }

    tmp_config = config.CONFIG_FILE

    @classmethod
    def setUpClass(cls):
        config.CONFIG_FILE = os.path.join(config.PROJECT_BASE, 'test-config.ini')

    @classmethod
    def tearDownClass(cls):
        config.CONFIG_FILE = cls.tmp_config
        print(config.CONFIG_FILE)

    def test_001_should_create_configuration_file(self):

        for section, data in self.sample_config.items():

            for k, val in data.items():
                config.save(section, k, val)

        for section, data in self.sample_config.items():

            for k, val in data.items():
                self.assertEqual(str(val), config.get(section, k))

    def test_002_should_retrieve_values_based_type(self):

        self.assertEqual(config.get('database', 'port', int), self.sample_config['database']['port'])
        self.assertEqual(config.get('sample', 'complex', complex), self.sample_config['sample']['complex'])
        self.assertEqual(config.get('sample', 'float', float), self.sample_config['sample']['float'])
        self.assertEqual(config.get('sample', 'bool', bool), self.sample_config['sample']['bool'])
        self.assertEqual(config.get('sample', 'bool2', bool), self.sample_config['sample']['bool2'])

    def test_003_should_fail_reading_non_existing_value(self):

        self.assertRaises(errors.ConfigurationError, config.get, 'database', 'secret')
        self.assertRaises(errors.ConfigurationError, config.get, 'queue')

    def test_004_should_fail_to_parse_read_invalid_data_type(self):

        self.assertRaises(errors.ConfigurationError, config.get, 'sample', 'bool', 1)



