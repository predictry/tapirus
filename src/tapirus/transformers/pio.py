
import predictionio

from tapirus.model import constants
from tapirus.model.store import Session, Agent, User, Item, Action
from tapirus.utils.logger import Logger


class PredictionIODataHandler(object):

    def __init__(self, access_key, url, threads, qsize):
        self.client = predictionio.EventClient(
            access_key=access_key,
            url=url,
            threads=threads,
            qsize=qsize
        )

    @classmethod
    def transform(cls, session, agent, user, items, actions):

        assert isinstance(session, Session)
        assert isinstance(agent, Agent)
        assert isinstance(user, User)
        assert type(items) is set
        assert type(actions) is list

        events = []

        event = dict(event="$set", entityType="user", entityId=user.id, eventTime=user.timestamp)

        events.append(event)

        for item in items:

            assert isinstance(item, Item)

            event = dict(event="$set", entityType="item", entityId=item.id, eventTime=item.timestamp,
                         properties=item.fields)

            events.append(event)

        for action in actions:

            assert isinstance(action, Action)

            name = action.name.lower()

            if action.name in (constants.REL_ACTION_TYPE_VIEW, constants.REL_ACTION_TYPE_ADD_TO_CART,
                               constants.REL_ACTION_TYPE_BUY, constants.REL_ACTION_TYPE_STARTED_CHECKOUT,
                               constants.REL_ACTION_TYPE_STARTED_PAYMENT):

                event = dict(event=name, entityType="user", entityId=action.user, targetEntityType="item",
                             targetEntityId=action.item, eventTime=action.timestamp,
                             properties=action.fields)

                events.append(event)

            elif action.name == constants.REL_ACTION_TYPE_SEARCH:
                pass

            elif action.name in (constants.REL_ACTION_TYPE_CHECK_DELETE_ITEM, constants.REL_ACTION_TYPE_DELETE_ITEM):

                event = dict(event="$delete", entityType="item", entityId=action.item, eventTime=action.timestamp)

                events.append(event)

        return events
