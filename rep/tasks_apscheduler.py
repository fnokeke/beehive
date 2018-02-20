import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rep.views_core  import store_rescuetime_data


def print_date_time():
    print time.strftime("%A, %d. %B %Y %I:%M:%S %p")

def schedule_rescuetime_task():
    # Run-once on flask init and then schedule task
    print "###############################################################################################"
    store_rescuetime_data()
    # Schedule every 8 hours to ensure fault tolerance
    interval = 60 * 60 * 8
    print "###############################################################################################"
    print "                                     RescueTime Job Scheduled"
    print "###############################################################################################"
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.remove_all_jobs()
    scheduler.add_job(
        func=store_rescuetime_data,
        trigger=IntervalTrigger(seconds=interval),
        id='rescuetime_job',
        name='store_rescuetime_data',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
