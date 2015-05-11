__author__ = 'guilherme'

import predictionio

from tapirus.model.constants import *
from tapirus.model.store import is_valid_data


class PredictionIOEventHandler(object):

    def __init__(self, access_key, url, threads, qsize):
        self.client = predictionio.EventClient(
            access_key=access_key,
            url=url,
            threads=threads,
            qsize=qsize
        )

    def handle(self, entry):

        events = self.transform(entry)

        for event in events:

            self.client.create_event(**event)

    def handle_events(self, entries):

        for entity in entries:

            self.handle(entity)

    @classmethod
    def transform(cls, data):

        event_time = data["datetime"]

        if is_valid_data(data) is False:
            return []

        events = []

        #User
        if SCHEMA_KEY_USER in data:

            event = dict(event="$set", entity_type="user", entity_id=data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID],
                         event_time=event_time)

            events.append(event)

        #Actions
        if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_VIEW:

            #Collect items
            for item in data[SCHEMA_KEY_ITEMS]:

                event = dict(event="$set", entity_type="item", entity_id=item[SCHEMA_KEY_ITEM_ID],
                             event_time=event_time)

                events.append(event)

                if SCHEMA_KEY_USER in data:
                    user_id = data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]
                else:
                    user_id = data[SCHEMA_KEY_SESSION_ID]

                event = dict(event="view", entity_type="user", entity_id=user_id, target_entity_type="item",
                             target_entity_id=item[SCHEMA_KEY_ITEM_ID], event_time=event_time)

                events.append(event)

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_CHECK_DELETE_ITEM:

            event = dict(event="$unset", entity_type="item", entity_id=data[SCHEMA_KEY_ITEM_ID], event_time=event_time)

            events.append(event)

        return events