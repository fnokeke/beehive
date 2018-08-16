from celery import Celery
from celery.schedules import crontab
from datetime import date, timedelta

from rep import app

import requests
import json
from datetime import datetime

from rep.models import GcalUser

import sendgrid
from sendgrid.helpers.mail import *
from secret_keys import SENDGRID_API_KEY

from rep import export
from rep.models import Researcher


def make_celery(app):
    celery = Celery(
        app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

############
# other celery configs are located in config.py
# 1) to run celery task first start redis-server using: redis-server
# 2) run celery in verbose mode: celery -A rep.tasks.celery worker --loglevel=info --beat
# 3) add your your celery task (a function) and schedule (fixed time or interval). see example below
# 4) Enjoy!
############
app.config.update(
    CELERY_TIMEZONE="America/New_York",
    CELERYBEAT_SCHEDULE={
        'export-data': {
            'task': 'rep.tasks.nudge_gcal_planners',
            # 'schedule': timedelta(seconds=15)
            'schedule': crontab(
                hour="07", minute='00')
        },
    },)

celery = make_celery(app)


@celery.task()
def trivial_task():
    return "Trivial task completed!"


def fetch_today_events(user):
    url = 'https://slm.smalldata.io/mobile/calendar/events'
    data = json.dumps({'email': user.email, 'date': datetime.now().strftime('%Y-%m-%d')})
    r = requests.post(url, data=data)
    events = []
    if r.status_code == 200:
        results = json.loads(r.text)
        events = results['events']
    return events


def sendgrid_email(recipient, subject, msg):
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = sendgrid.Email("beehive@smalldata.io")
    to_email = sendgrid.Email(recipient)
    html_msg = "<p>%s</p>" % msg
    content = Content("text/html", html_msg)
    mail_to_send = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail_to_send.get())
    print "***email nudge sent to user. status = %s *****" % response.status_code


def nudge_by_email(user, msg):
    subject = "Beehive daily planner."
    sendgrid_email(user.email, subject, msg)


@celery.task()
def nudge_gcal_planners():
    # today_date = datetime.now().strftime('%Y-%m-%d')
    given_date = date.today() - timedelta(days=1)
    given_date.strftime('%Y-%m-%d')
    users = GcalUser.query.filter_by(code='eddycu').all()
    for user in users:
        events = fetch_today_events(user)
        message = "You did not plan any events for date: %s." % given_date
        if len(events) > 0:
            message = "Great job! You had %s events planned for %s." % (len(events),  given_date)

        nudge_by_email(user, message)

    return "Successfully nudged %s user(s) today (%s)!" % (len(users), given_date)

# @celery.task()
# def export_data():
    # yesterday = date.today() - timedelta(1)
    # yesterday = yesterday.strftime('%Y-%m-%d')
    #
    # all_users = Researcher.get_all_users()
    # for user in all_users:
    #     print '*** Exporting for user: {} ***'.format(user)
    #
    #     if user.is_location_active:
    #         calname = app.config['LOCATION']
    #         resp = export.to_cal(calname, user.moves_access_token, yesterday, user.google_credentials)
    #         print 'Location resp: {}'.format(resp)
    #     else:
    #         print 'Skipping location for {}'.format(user)
    #
    #     if user.is_mood_active:
    #         calname = app.config['MOOD']
    #         resp = export.to_cal(calname, user.pam_access_token, yesterday, user.google_credentials)
    #         print 'Mood resp: {}'.format(resp)
    #     else:
    #         print 'Skipping mood for {}'.format(user)
    #
    #     if user.is_sn_active:
    #         calname = app.config['SN']
    #         resp = export.to_cal(calname, user.rescuetime_access_token, yesterday, user.google_credentials)
    #         print 'SN resp: {}'.format(resp)
    #     else:
    #         print 'Skipping social networks for {}'.format(user)
    #
    # return 'Export completed! Exported events for {} users.'.format(len(all_users))
