from db_init import db

import datetime
import json
import uuid
from utils import to_datetime


class TP_Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    study_code = db.Column(db.String(10))
    admin_experiment_group = db.Column(db.Integer)
    admin_fb_max_mins = db.Column(db.Integer)
    admin_fb_max_opens = db.Column(db.Integer)
    admin_treatment_start = db.Column(db.DateTime)
    admin_followup_start = db.Column(db.DateTime)
    admin_logging_stop = db.Column(db.DateTime)

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.study_code = info['study_code']
        self.admin_experiment_group = info.get('admin_experiment_group')
        self.admin_fb_max_mins = info.get('admin_fb_max_mins')
        self.admin_fb_max_opens = info.get('admin_fb_max_opens')
        self.admin_treatment_start = to_datetime(info.get('admin_treatment_start'), "%Y%m-%d")
        self.admin_followup_start = to_datetime(info.get('admin_followup_start'), "%Y-%m-%d")
        self.admin_logging_stop = to_datetime(info.get('admin_logging_stop'), "%Y-%m-%d")

    def __repr__(self):
        result = {
            'id': self.id,
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'study_code': self.study_code,
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
        worker = TP_Admin.query.filter_by(worker_id=info['worker_id']).first()
        if worker:
            return (200, 'Admin already added worker.', worker)

        new_worker = TP_Admin(info)
        db.session.add(new_worker)
        db.session.commit()
        return (200, 'Admin successfully added new worker!', new_worker)

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
        most_recent = TP_DailyResetHour.query.order_by(TP_DailyResetHour.created_at.desc()).first()
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
        if existing_worker:
            return (200, 'Welcome back!', existing_worker)

        existing_device = TP_Enrolled.query.filter_by(device_id=info['device_id']).first()
        if existing_device:
            return (200, 'Welcome back! Device already registered.', existing_device)
            # return (-1, 'Device already registered with another WorkerId.', existing_device)

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
    daily_reset_hour = db.Column(db.Integer)  # 0(midnight) to 23(11PM)

    # current params updated through from android app
    current_experiment_group = db.Column(db.Integer)
    current_fb_max_mins = db.Column(db.Integer)
    current_fb_max_opens = db.Column(db.Integer)
    current_treatment_start = db.Column(db.DateTime)
    current_followup_start = db.Column(db.DateTime)
    current_logging_stop = db.Column(db.DateTime)
    current_firebase_token = db.Column(db.String(500))
    current_static_ratio_100 = db.Column(db.Integer)
    current_adaptive_ratio_100 = db.Column(db.Integer)
    current_ratio_of_limit = db.Column(db.Float)
    local_time = db.Column(db.String(25))
    time_spent_list = db.Column(db.String(500))
    num_opens_list = db.Column(db.String(500))

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.total_seconds = info['total_seconds']
        self.total_opens = info['total_opens']
        self.time_spent = info['time_spent']
        self.time_open = info['time_open']
        self.ringer_mode = info['ringer_mode']
        self.daily_reset_hour = info['daily_reset_hour']

        self.current_experiment_group = info.get('current_experiment_group')
        self.current_fb_max_mins = info.get('current_fb_max_mins')
        self.current_fb_max_opens = info.get('current_fb_max_opens')
        self.current_treatment_start = info.get('current_treatment_start')
        self.current_followup_start = info.get('current_followup_start')
        self.current_logging_stop = info.get('current_logging_stop')
        self.current_firebase_token = info.get('current_firebase_token')
        self.current_static_ratio_100 = info.get('current_static_ratio_100')
        self.current_adaptive_ratio_100 = info.get('current_adaptive_ratio_100')
        self.current_ratio_of_limit = info.get('current_ratio_of_limit')
        self.local_time = info.get('local_time')
        self.time_spent_list = info.get('time_spent_list')
        self.num_opens_list = info.get('num_opens_list')

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
            'current_experiment_group': self.current_experiment_group,
            'current_fb_max_mins': self.current_fb_max_mins,
            'current_fb_max_opens': self.current_fb_max_opens,
            'current_treatment_start': str(self.current_treatment_start),
            'current_followup_start': str(self.current_followup_start),
            'current_logging_stop': str(self.current_logging_stop),
            'current_firebase_token': str(self.current_firebase_token),
            'current_static_ratio_100': str(self.current_static_ratio_100),
            'current_adaptive_ratio_100': str(self.current_adaptive_ratio_100),
            'current_ratio_of_limit': str(self.current_ratio_of_limit),
            'local_time': str(self.local_time),
            'time_spent_list': str(self.time_spent_list),
            'num_opens_list': str(self.num_opens_list)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        new_stats = TP_FBStats(info)
        db.session.add(new_stats)
        db.session.commit()
        return (200, 'Successfully added fbstats!', new_stats)


class TP_FacebookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    time_millis = db.Column(db.BigInteger)
    fb_date = db.Column(db.String(30))
    time_spent = db.Column(db.Integer)
    time_open = db.Column(db.Integer)

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.time_millis = info['time_millis']
        self.fb_date = info['fb_date']
        self.time_spent = info['time_spent']
        self.time_open = info['time_open']

    def __repr__(self):
        result = {
            'id': str(self.id),
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'time_millis': self.time_millis,
            'fb_date': self.fb_date,
            'time_spent': self.time_spent,
            'time_open': self.time_open
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        worker_id = info['worker_id']
        logs = info['logs']
        rows = logs.split(';')

        for row in rows:
            if row == "": continue
            time_millis, fb_date, time_spent, time_open = row.split(",")
            entry = {'worker_id': worker_id,
                     'time_millis': time_millis,
                     'fb_date': fb_date,
                     'time_spent': time_spent,
                     'time_open': time_open}
            new_stats = TP_FacebookLog(entry)
            db.session.add(new_stats)

        db.session.commit()
        return (200, 'Successfully added Facebook log!', "")


class TP_FgAppLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    app_id = db.Column(db.String(30))
    time_seconds = db.Column(db.String(20))
    time_millis = db.Column(db.BigInteger)
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.app_id = info['app_id'][:30]
        self.time_seconds = info['time_seconds']
        self.time_millis = info['time_millis']

    def __repr__(self):
        result = {
            'id': str(self.id),
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'app_id': self.app_id,
            'time_seconds': self.time_seconds,
            'time_millis': self.time_millis
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        worker_id = info['worker_id']
        logs = info['logs']
        rows = logs.split(';')

        for row in rows:
            if row == "": continue
            app_id, time_seconds, time_millis = row.split(",")
            entry = {'worker_id': worker_id, 'app_id': app_id, 'time_seconds': time_seconds, 'time_millis': time_millis}
            new_stats = TP_FgAppLog(entry)
            db.session.add(new_stats)

        db.session.commit()
        return (200, 'Successfully added fgAppLog stats!', "")


class MobileNotifLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
    time_millis = db.Column(db.BigInteger)
    app_id = db.Column(db.String(30))
    posted_millis = db.Column(db.BigInteger)
    action = db.Column(db.String(10))

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.code = info['code']
        self.time_millis = info['time_millis']
        self.app_id = info['app_id'][:30]
        self.posted_millis = info['posted_millis']
        self.action = info['action']

    def __repr__(self):
        result = {
            'id': str(self.id),
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'code': self.code,
            'time_millis': self.time_millis,
            'posted_millis': self.posted_millis,
            'action': self.action
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        rows = info['logs'].split(';')
        for row in rows:
            if row != "":
                time_millis, app_id, posted_millis, action = row.split(",")
                new_stats = MobileNotifLogs({
                    'worker_id': info['worker_id'],
                    'code': info['code'],
                    'time_millis': time_millis,
                    'app_id': app_id,
                    'posted_millis': posted_millis,
                    'action': action
                })
                db.session.add(new_stats)

        db.session.commit()
        return 200, 'Successfully added phone notif logs!', ""



class TP_ScreenLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    event = db.Column(db.String(30))
    time_millis = db.Column(db.BigInteger)
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.event = info['event']
        self.time_millis = info['time_millis']

    def __repr__(self):
        result = {
            'id': str(self.id),
            'created_at': str(self.created_at),
            'worker_id': self.worker_id,
            'event': self.event,
            'time_millis': self.time_millis
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        worker_id = info['worker_id']
        logs = info['logs']
        rows = logs.split(';')

        for row in rows:
            if row == "": continue
            event, time_millis = row.split(",")
            entry = {'worker_id': worker_id, 'event': event, 'time_millis': time_millis}
            new_stats = TP_ScreenLog(entry)
            db.session.add(new_stats)

        db.session.commit()
        return (200, 'Successfully added screenLog stats!', "")

# TODO: remove experiment and use just experiment
# TODO: remove TP_name and use Mobile_name
