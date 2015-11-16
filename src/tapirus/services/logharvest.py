import datetime
import schedule
import time
from tapirus import tasks
from tapirus.utils import config
from tapirus.utils.logger import Logger


def harvest():
    now = datetime.datetime.utcnow()
    timestamps = [now - datetime.timedelta(hours=x) for x in range(2, 7*24+1)]

    # how do I make sure the timing is right? request for the past two hours
    for timestamp in timestamps:
        Logger.info('Harvesting for {0}'.format(timestamp))
        tasks.run_workflow_for_record.delay(timestamp)


def main():
    Logger.info('Initiating log harvesting worker...')
    harvest()
    period = config.get('harvester', 'interval', type=int, fallback=3600)
    schedule.every(period).seconds.do(harvest)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # run tasks
    main()
