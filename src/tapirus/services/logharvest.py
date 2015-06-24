import datetime

import schedule

from tapirus import tasks
from tapirus.utils import config
from tapirus.utils.logger import Logger


def harvest_past_hour():

    def inner():

        now = datetime.datetime.utcnow()
        timestamps = {now - datetime.timedelta(hours=1),
                      now - datetime.timedelta(hours=2)}

        # how do I make sure the timing is right? request for the past two hours
        for timestamp in timestamps:
            tasks.run_workflow_for_record.delay(timestamp)

    # TODO: read time interval from config file
    period = int(config.get('harvester', 'interval'))
    schedule.every(period).seconds.do(inner)

    Logger.info('Initiating work harvesting worker...')


def main():

    while True:
        schedule.run_pending()


if __name__ == '__main__':

    # register periodic tasks
    harvest_past_hour()

    # run tasks
    main()
