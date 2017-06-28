from celery import Celery
from celery.schedules import crontab
from datetime import date, timedelta

from rep import app
from rep import export
from rep.models import WebUser


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
# run celery verbose: celery -A tasks.celery worker --loglevel=info --beat
############
app.config.update(
    CELERY_TIMEZONE="America/New_York",
    CELERYBEAT_SCHEDULE={
        'export-data': {
            'task': 'rep.tasks.export_data',
            # 'schedule': timedelta(seconds=15)
            'schedule': crontab(
                hour="03", minute='00')
        },
    },)

celery = make_celery(app)


@celery.task()
def export_data():
    yesterday = date.today() - timedelta(1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    all_users = WebUser.get_all_users()
    for user in all_users:
        print '*** Exporting for user: {} ***'.format(user)

        if user.is_location_active:
            calname = app.config['LOCATION']
            resp = export.to_cal(calname, user.moves_access_token, yesterday, user.google_credentials)
            print 'Location resp: {}'.format(resp)
        else:
            print 'Skipping location for {}'.format(user)

        if user.is_mood_active:
            calname = app.config['MOOD']
            resp = export.to_cal(calname, user.pam_access_token, yesterday, user.google_credentials)
            print 'Mood resp: {}'.format(resp)
        else:
            print 'Skipping mood for {}'.format(user)

        if user.is_sn_active:
            calname = app.config['SN']
            resp = export.to_cal(calname, user.rescuetime_access_token, yesterday, user.google_credentials)
            print 'SN resp: {}'.format(resp)
        else:
            print 'Skipping social networks for {}'.format(user)

    return 'Export completed! Exported events for {} users.'.format(len(all_users))
