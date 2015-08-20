import datetime

import schedule

from tapirus import tasks
from tapirus.utils import config
from tapirus.utils.logger import Logger


def harvest_past_hour():

    def inner():

        now = datetime.datetime.utcnow()
        timestamps = [now - datetime.timedelta(hours=x) for x in range(1, 7*24+1)]

        # how do I make sure the timing is right? request for the past two hours
        for timestamp in timestamps:
            tasks.run_workflow_for_record.delay(timestamp)

    period = config.get('harvester', 'interval', type=int, fallback=3600)
    schedule.every(period).seconds.do(inner)

    Logger.info('Initiating log harvesting worker...')


def main():

    while True:
            schedule.run_pending()


if __name__ == '__main__':

    # register periodic tasks
    harvest_past_hour()

    # run tasks
    main()
