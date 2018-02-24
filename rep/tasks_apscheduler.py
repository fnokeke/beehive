import time
import atexit

from datetime import date
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rep.views_rescuetime  import store_rescuetime_data
from rep.models import RescuetimeData


def print_date_time():
    print time.strftime("%A, %d. %B %Y %I:%M:%S %p")

def schedule_rescuetime_task():
    print "###############################################################################################"
    try:
        # Sanity check to avoid database data duplication
        date_yesterday = date.today() - timedelta(days=1)
        count_rows = RescuetimeData.query.filter_by(created_date=date_yesterday).count()
    except:
        print "schedule_rescuetime_task:", "rescuetime_data table not found!"
        print "schedule_rescuetime_task:", "FAILED - could not schedule task!"
        return

    store_rescuetime_data()
    # Schedule every 6 hours to ensure fault tolerance
    interval = 60 * 60 * 6
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
