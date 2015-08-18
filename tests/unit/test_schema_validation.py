import unittest
import uuid
import datetime

from tapirus import constants
from tapirus.parser.v1 import pl
from tapirus.repo.models import Error


class TestDeleteEventValidation(unittest.TestCase):

    @property
    def uuid(self):
        return uuid.uuid4().__str__()

    def setUp(self):
        self.valid_events = [
            {
                'browser_id': self.uuid,
                'tenant_id': 'TENANT-1',
                'api_key': self.uuid,
                'user_id': self.uuid,
                'items': ['item-1', 'item-2', 'item-3'],
                'session_id': self.uuid,
                'action':
                    {
                        'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                    }
            },
            {
                'browser_id': self.uuid,
                'tenant_id': 'TENANT-1',
                'api_key': self.uuid,
                'user_id': self.uuid,
                'items': ['item-1'],
                'session_id': self.uuid,
                'action':
                    {
                        'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                    }
            },
            {
                'browser_id': self.uuid,
                'tenant_id': 'TENANT-1',
                'api_key': self.uuid,
                'user_id': self.uuid,
                'items': [],
                'session_id': self.uuid,
                'action':
                    {
                        'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                    }
            }
        ]

        self.invalid_events = [
            {
                'browser_id': self.uuid,
                'tenant_id': 'TENANT-1',
                'api_key': self.uuid,
                'user_id': self.uuid,
                'items': [1],
                'session_id': self.uuid,
                'action':
                    {
                        'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                    }
            },
            {
                'browser_id': self.uuid,
                'tenant_id': 'TENANT-1',
                'api_key': self.uuid,
                'user_id': self.uuid,
                'items': [{}],
                'session_id': self.uuid,
                'action':
                    {
                        'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                    }
            }
        ]

    def test_should_verify_correct_schema_passes_validation(self):

        for data in self.valid_events:

            self.assertTrue(pl.is_valid_schema(data))

            errors = pl.detect_schema_errors(Error(1, data, datetime.datetime.utcnow()))

            self.assertEquals(errors, [])

    def test_should_verify_incorrect_item_id_fails_validation(self):

        for data in self.invalid_events:

            self.assertFalse(pl.is_valid_schema(data))

        data = {
            'browser_id': self.uuid,
            'tenant_id': 'TENANT-1',
            'api_key': self.uuid,
            'user_id': self.uuid,
            'items': [{}, ""],
            'session_id': self.uuid,
            'action':
                {
                    'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                }
        }

        errors = pl.detect_schema_errors(Error(None, data, datetime.datetime.utcnow()))

        self.assertEqual(len(errors), 2)

        self.assertEqual(errors[0]['key'], 'action.DELETE_ITEM.items.item_id')
        self.assertEqual(pl.ErrorCause.WRONG_DATA_TYPE.value, errors[0]['cause'])

        self.assertEqual(errors[1]['key'], 'action.DELETE_ITEM.items.item_id')
        self.assertEqual(pl.ErrorCause.INVALID_VALUE.value, errors[1]['cause'])

    def test_should_verify_incorrect_items_data_type_fails_validation(self):

        data = {
            'browser_id': self.uuid,
            'tenant_id': 'TENANT-1',
            'api_key': self.uuid,
            'user_id': self.uuid,
            'items': {},
            'session_id': self.uuid,
            'action':
                {
                    'name': constants.REL_ACTION_TYPE_DELETE_ITEM
                }
        }

        errors = pl.detect_schema_errors(Error(None, data, datetime.datetime.utcnow()))

        self.assertEqual(len(errors), 1)

        if errors[0]['key'] == 'action.DELETE_ITEM.items':
            self.assertEqual(pl.ErrorCause.WRONG_DATA_TYPE.value, errors[0]['cause'])



