from db_init import db

import datetime
import json
import uuid
from utils import to_datetime


class TP_Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))

    # admin params set through dashboard
    admin_experiment_group = db.Column(db.Integer, default=1)
    admin_fb_max_mins = db.Column(db.Integer, default=10)
    admin_fb_max_opens = db.Column(db.Integer, default=2)
    admin_treatment_start = db.Column(db.DateTime, default=to_datetime("2017-04-24", "%Y-%m-%d"))
    admin_followup_start = db.Column(db.DateTime, default=to_datetime("2017-05-01", "%Y-%m-%d"))
    admin_logging_stop = db.Column(db.DateTime, default=to_datetime("2017-05-10", "%Y-%m-%d"))

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.admin_experiment_group = info.get('admin_experiment_group')
        self.admin_fb_max_mins = info.get('admin_fb_max_mins')
        self.admin_fb_max_opens = info.get('admin_fb_max_opens')
        # self.admin_treatment_start = info.get('admin_treatment_start')
        # self.admin_followup_start = info.get('admin_followup_start')
        # self.admin_logging_stop = info.get('admin_logging_stop')
        try:
            self.admin_treatment_start = to_datetime(info.get('admin_treatment_start'), "%Y%m-%d")
            self.admin_followup_start = to_datetime(info.get('admin_followup_start'), "%Y-%m-%d")
            self.admin_logging_stop = to_datetime(info.get('admin_logging_stop'), "%Y-%m-%d")
        except Exception as e:
            print e

    def __repr__(self):
        result = {
            'id': self.id,
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'admin_experiment_group': self.admin_experiment_group,
            'admin_fb_max_mins': self.admin_fb_max_mins,
            'admin_fb_max_opens': self.admin_fb_max_opens,
            'admin_treatment_start': str(self.admin_treatment_start),
            'admin_followup_start': str(self.admin_followup_start),
            'admin_logging_stop': str(self.admin_logging_stop)
        }
        return json.dumps(result)

    @staticmethod
    def add_user(info):
        TP_Admin.query.filter_by(worker_id=info['worker_id']).delete()
        db.session.commit()

        new_worker = TP_Admin(info)
        db.session.add(new_worker)
        db.session.commit()
        return (200, 'Successfully added user settings!', new_worker)

    @staticmethod
    def update_user(info):
        worker = TP_Admin.query.filter_by(worker_id=info['worker_id']).first()
        if not worker:
            return (-1, 'Error: worker not in admin dashboard.', -1)

        worker.admin_experiment_group = info.get('admin_experiment_group')
        worker.admin_fb_max_mins = info.get('admin_fb_max_mins')
        worker.admin_fb_max_opens = info.get('admin_fb_max_opens')
        worker.admin_treatment_start = info.get('admin_treatment_start')
        worker.admin_followup_start = info.get('admin_followup_start')
        worker.admin_logging_stop = info.get('admin_logging_stop')

        db.session.commit()
        return (200, 'Successfully updated admin user settings!', worker)


class TP_DailyResetHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin_reset_hour = db.Column(db.Integer, default=0)  # 0(midnight) to 23(11PM)

    def __init__(self, info):
        self.admin_reset_hour = info['admin_reset_hour']

    def __repr__(self):
        result = {'created_at': str(self.created_at), 'admin_reset_hour': self.admin_reset_hour}
        return json.dumps(result)

    @staticmethod
    def add(info):
        entry = TP_DailyResetHour(info)
        db.session.add(entry)
        db.session.commit()
        return (200, 'Successfully added reset time: {}.'.format(entry.admin_reset_hour), entry.admin_reset_hour)

    @staticmethod
    def get_last_updated_hour():
        most_recent = TP_DailyResetHour.query.order_by('created_at desc').first()
        return most_recent.admin_reset_hour if most_recent else 0


class TP_Enrolled(db.Model):
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50), primary_key=True, unique=True)
    worker_code = db.Column(db.String(6), unique=True)
    last_installed_ms = db.Column(db.String(30))
    pretty_last_installed = db.Column(db.String(30))
    app_version_name = db.Column(db.String(10))
    app_version_code = db.Column(db.String(10))
    phone_model = db.Column(db.String(30))
    android_version = db.Column(db.String(10))
    device_country = db.Column(db.String(10))
    device_id = db.Column(db.String(30))

    def __init__(self, info):
        self.worker_code = TP_Enrolled.generate_unique_id()
        self.worker_id = info['worker_id']
        self.last_installed_ms = info['last_installed_ms']
        self.pretty_last_installed = info['pretty_last_installed']
        self.app_version_name = info['app_version_name']
        self.app_version_code = info['app_version_code']
        self.phone_model = info['phone_model']
        self.android_version = info['android_version']
        self.device_country = info['device_country']
        self.device_id = info['device_id']

    def __repr__(self):
        result = {'worker_id': self.worker_id,
                  'worker_code': self.worker_code,
                  'device_id': self.device_id,
                  'created_at': str(self.created_at),
                  'last_installed_ms': self.last_installed_ms,
                  'pretty_last_installed': self.pretty_last_installed,
                  'app_version_name': self.app_version_name,
                  'app_version_code': self.app_version_code,
                  'phone_model': self.phone_model,
                  'device_country': self.device_country,
                  'android_version': self.android_version}
        return json.dumps(result)

    @staticmethod
    def generate_unique_id():
        code = str(uuid.uuid4())[:6]
        while TP_Enrolled.query.filter_by(worker_code=code).first():
            code = str(uuid.uuid4())[:6]
        return code

    @staticmethod
    def add_user(info):
        existing_worker = TP_Enrolled.query.filter_by(worker_id=info['worker_id']).first()
        existing_device = TP_Enrolled.query.filter_by(device_id=info['device_id']).first()

        if existing_worker:
            return (200, 'WorkerId already registered.', existing_worker)

        if existing_device:
            return (-1, 'This device is already registered using another WorkerId.', existing_device)

        new_worker = TP_Enrolled(info)
        db.session.add(new_worker)
        db.session.commit()
        return (200, 'Successfully connected!', new_worker)


class TP_FBStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    total_seconds = db.Column(db.Integer)
    total_opens = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)
    time_open = db.Column(db.Integer)
    ringer_mode = db.Column(db.String(10))
    screen_logs = db.Column(db.String(2500))
    daily_reset_hour = db.Column(db.Integer)  # 0(midnight) to 23(11PM)

    # current params updated through from android app
    current_experiment_group = db.Column(db.Integer)
    current_fb_max_mins = db.Column(db.Integer)
    current_fb_max_opens = db.Column(db.Integer)
    current_treatment_start = db.Column(db.DateTime)
    current_followup_start = db.Column(db.DateTime)
    current_logging_stop = db.Column(db.DateTime)

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.total_seconds = info['total_seconds']
        self.total_opens = info['total_opens']
        self.time_spent = info['time_spent']
        self.time_open = info['time_open']
        self.ringer_mode = info['ringer_mode']
        self.daily_reset_hour = info['daily_reset_hour']

        if len(info['screen_logs']) > 2500:
            self.screen_logs = "-1"
        else:
            self.screen_logs = info['screen_logs']

        self.current_experiment_group = info.get('current_experiment_group')
        self.current_fb_max_mins = info.get('current_fb_max_mins')
        self.current_fb_max_opens = info.get('current_fb_max_opens')
        self.current_treatment_start = info.get('current_treatment_start')
        self.current_followup_start = info.get('current_followup_start')
        self.current_logging_stop = info.get('current_logging_stop')

    def __repr__(self):
        result = {
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'total_seconds': self.total_seconds,
            'total_opens': self.total_opens,
            'time_spent': self.time_spent,
            'time_open': self.time_open,
            'ringer_mode': self.ringer_mode,
            'daily_reset_hour': self.daily_reset_hour,
            'screen_logs': self.screen_logs,
            'current_experiment_group': self.current_experiment_group,
            'current_fb_max_mins': self.current_fb_max_mins,
            'current_fb_max_opens': self.current_fb_max_opens,
            'current_treatment_start': str(self.current_treatment_start),
            'current_followup_start': str(self.current_followup_start),
            'current_logging_stop': str(self.current_logging_stop)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        #existing_worker = TP_Admin.query.filter_by(worker_id=info['worker_id']).first()
        #if not existing_worker:
        #    return (-1, 'Error: Should register user before posting FB stats. Pls contact researcher.', -1)

        new_stats = TP_FBStats(info)
        db.session.add(new_stats)
        db.session.commit()
        return (200, 'Successfully added stats!', new_stats)
