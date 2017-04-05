from db_init import db

import datetime
import json


class TPrimeUserAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))

    # admin params set through dashboard
    admin_study_group = db.Column(db.Integer, default=1)
    admin_fb_max_mins = db.Column(db.Integer, default=10)
    admin_fb_max_opens = db.Column(db.Integer, default=2)
    admin_treatment_start = db.Column(db.DateTime)
    admin_followup_start = db.Column(db.DateTime)
    admin_logging_stop = db.Column(db.DateTime)

    def __init__(self, info):
        self.worker_id = info['worker_id']
        self.admin_study_group = info.get('admin_study_group')
        self.admin_fb_max_mins = info.get('admin_fb_max_mins')
        self.admin_fb_max_opens = info.get('admin_fb_max_opens')
        self.admin_treatment_start = info.get('admin_treatment_start')
        self.admin_followup_start = info.get('admin_followup_start')
        self.admin_logging_stop = info.get('admin_logging_stop')

    def __repr__(self):
        result = {
            'id': self.id,
            'worker_id': self.worker_id,
            'admin_study_group': self.admin_study_group,
            'admin_fb_max_mins': self.admin_fb_max_mins,
            'admin_fb_max_opens': self.admin_fb_max_opens,
            'admin_treatment_start': self.admin_treatment_start,
            'admin_followup_start': self.admin_followup_start,
            'admin_logging_stop': self.admin_logging_stop
        }
        return json.dumps(result)

    @staticmethod
    def update(existing_worker, info):
        existing_worker.admin_study_group = info.get('admin_study_group')
        existing_worker.admin_fb_max_mins = info.get('admin_fb_max_mins')
        existing_worker.admin_fb_max_opens = info.get('admin_fb_max_opens')
        existing_worker.admin_treatment_start = info.get('admin_treatment_start')
        existing_worker.admin_followup_start = info.get('admin_followup_start')
        existing_worker.admin_logging_stop = info.get('admin_logging_stop')

    @staticmethod
    def create_or_update(info):
        worker = TPrimeUserAdmin.query.filter_by(worker_id=info['worker_id']).first()
        if worker:
            TPrimeUserAdmin.update(worker, info)
        else:
            worker = TPrimeUserAdmin(info)
            db.session.add(worker)

        db.session.commit()
        return (200, 'Successfully added user settings!', worker)


class TPrimeFBStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    worker_id = db.Column(db.String(50))
    total_seconds = db.Column(db.Integer)
    total_opens = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)
    time_open = db.Column(db.Integer)
    ringer_mode = db.Column(db.String(10))

    # current params updated through from android app
    current_study_group = db.Column(db.Integer)
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

        self.current_study_group = info.get('current_study_group')
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
            'current_study_group': self.current_study_group,
            'current_fb_max_time': self.current_fb_max_time,
            'current_fb_max_opens': self.current_fb_max_opens,
            'current_treatment_start': self.current_treatment_start,
            'current_followup_start': self.current_followup_start,
            'current_logging_stop': self.current_logging_stop
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        existing_worker = TPrimeUserAdmin.query.filter_by(worker_id=info['worker_id']).first()
        if not existing_worker:
            return (-1, 'Error: Should register user before posting FB stats. Pls contact researcher.', -1)

        new_stats = TPrimeFBStats(info)
        db.session.add(new_stats)
        db.session.commit()
        return (200, 'Successfully added stats!', new_stats)


class TPrimeResetTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    daily_reset_time = db.Column(db.Integer, default=0)  # 0(midnight) to 23(11PM)

    def __init__(self, info):
        self.daily_reset_time = info['daily_reset_time']

    def __repr__(self):
        result = {'created_at': str(self.created_at), 'daily_reset_time': self.daily_reset_time}
        return json.dumps(result)

    @staticmethod
    def add(info):
        entry = TPrimeResetTime(info)
        db.session.add(entry)
        db.session.commit()
        return (200, 'Successfully added reset time: {}.'.format(entry.daily_reset_time), entry.daily_reset_time)
