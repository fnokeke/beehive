#!~/.virtualenvs/rep-aws-env/bin/python

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from rep import app

def print_date_time():
    print time.strftime("%A, %d. %B %Y %I:%M:%S %p")

# start the flask loop
if __name__ == "__main__":
    print "Schedule Tasks"
    print time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=print_date_time,
        trigger=IntervalTrigger(seconds=120),
        id='printing_job',
        name='Print date and time every five seconds',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)

