from db_init import db
from utils import to_json
from flask import Response, abort

import datetime
import json
import uuid

# Database model for experiments


class Experiment_v2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True)
    label = db.Column(db.String(120))
    title = db.Column(db.String(120))
    description = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    screen_events = db.Column(db.Boolean, default=False)
    app_usage = db.Column(db.Boolean, default=False)
    protocols = db.relationship('ProtocolPushNotif', backref='experiment_v2', lazy='select')
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner = db.Column(db.String(120), db.ForeignKey('researcher.email'))

    def __init__(self, info):
        self.code = info.get('code') if info.get('code') else Experiment_v2.generate_unique_id()
        self.label = info.get('label')
        self.title = info.get('title')
        self.description = info.get('description')
        self.start_date = info['start_date']
        self.end_date = info['end_date']
        self.screen_events = info.get('screen_events')
        self.app_usage = info.get('app_usage')
        self.owner = info['owner']

        print 'info[start_date] = ', info['start_date']
        print 'self.start_date = ', self.start_date

    def __repr__(self):
        result = {
            'owner': self.owner,
            'code': self.code,
            'label': self.label,
            'title': self.title,
            'description': self.description,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'screen_events': self.screen_events,
            'app_usage': self.app_usage,
            'created_date': str(self.created_date)
        }
        return json.dumps(result)

    @staticmethod
    def generate_unique_id():
        code = str(uuid.uuid4())[:6]
        while Experiment_v2.query.filter_by(code=code).first():
            code = str(uuid.uuid4())[:6]
        return code

    @staticmethod
    def add_experiment(exp):
        msg = "New experiment was successfully created."
        existing_experiment = Experiment_v2.query.filter_by(title=exp['title']).first()
        if existing_experiment:  # recreate new experiment with updated details but same code
            exp['code'] = existing_experiment.code
            Experiment_v2.delete_experiment(existing_experiment.code)
            msg = "Experiment was successfully updated."

        new_experiment = Experiment_v2(exp)
        db.session.add(new_experiment)
        db.session.commit()
        new_experiment = Experiment_v2.query.filter_by(title=exp['title']).first()

        # Add protocols  to protocols table
        protocols = json.loads(exp['protocols'])
        for p in protocols:
            p['exp_code'] = new_experiment.code
            ProtocolPushNotif.add_protocol(p)

        return 200, msg, new_experiment

    @staticmethod
    def delete_experiment(code):
        e = db.session.query(Experiment_v2).filter(Experiment_v2.code == code).first()
        db.session.delete(e)
        db.session.commit()
        # Experiment_v2.query.filter_by(code=code).delete()
        # ProtocolPushNotif.query.filter_by(code=code).delete()
        # db.session.commit()

    @staticmethod
    def update_experiment(update):
        experiment = Experiment_v2.query.filter_by(code=update['code']).first()
        for key, value in update.iteritems():
            setattr(experiment, key, value)

        experiment.code = update.get('code')
        experiment.label = update.get('label')
        experiment.title = update.get('title')
        experiment.description = update.get('description')
        experiment.start_date = update.get('start_date')
        experiment.end_date = update.get('end_date')
        experiment.screen_events = update.get('screen_events')
        db.session.commit()
        return experiment

    @staticmethod
    def update_group(update):
        experiment = Experiment_v2.query.filter_by(code=update['code']).first()
        return experiment


class Researcher(db.Model):
    # google login info and credentials for accessing google calendar
    email = db.Column(db.String(120), primary_key=True, unique=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    picture = db.Column(db.String(120))
    google_credentials = db.Column(db.String(2500), unique=True)

    def __init__(self, profile):
        self.email = profile.get('email', '')
        self.firstname = profile.get('given_name', '')
        self.lastname = profile.get('family_name', '')
        self.gender = profile.get('gender', '')
        self.picture = profile.get('picture', '')

    def __repr__(self):
        return self.email

    def is_active(self):
        return True

    def is_authenticated(self):
        """
        Returns `True`. Researcher is always authenticated.
        """
        return True

    def is_anonymous(self):
        """
        Returns `False`. There are no Anonymous here.
        """
        return False

    def get_id(self):
        """
        Take `id` attribute and convert it to `unicode`.
        """
        return unicode(self.email)

    def update_field(self, key, value):
        """
        Set user field with give value and save to database.
        """
        user = Researcher.query.get(self.email)
        setattr(user, key, value)  # same: user.key = value
        db.session.commit()

    def is_authorized(self, label):
        """
        Return True if datastream label has been authenticated else False.
        """
        if label == 'moves':
            return self.moves_id and self.moves_access_token and self.moves_refresh_token
        elif label == 'gcal':
            return self.google_credentials
        elif label == 'pam':
            return self.pam_access_token and self.pam_refresh_token
        else:
            raise NotImplementedError("Auth failed for label: %s." % label)

    @classmethod
    def get_user(cls, email):
        """
        Return user object from database using primary_key(email).
        """
        return cls.query.get(email)

    @classmethod
    def get_all_users(cls):
        """
        Return list of all users from database.
        """
        return cls.query.all()

    @classmethod
    def from_profile(cls, profile):
        """
        Return new user or existing user from database using their profile information.
        """
        email = profile.get('email')
        if not cls.query.get(email):
            new_user = cls(profile)
            db.session.add(new_user)
            db.session.commit()

        user = cls.query.get(email)
        return user


# Database model to store participant information
class Participant(db.Model):
    email = db.Column(db.String(120), primary_key=True, unique=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    google_credentials = db.Column(db.String(2500), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, profile, google_credentials):
        print '********** now creating user ****************'
        print google_credentials
        self.email = profile['email']
        self.firstname = profile['firstname']
        self.lastname = profile['lastname']
        self.gender = profile['gender']
        self.google_credentials = google_credentials

    def __repr__(self):
        return self.email

    def is_active(self):
        return True

    def is_authenticated(self):
        """
        Returns `True`. NewParticipant is always authenticated.
        """
        return True

    def is_anonymous(self):
        """
        Returns `False`. There are no Anonymous here.
        """
        return False

    def get_id(self):
        """
        Take `id` attribute and convert it to `unicode`.
        """
        return unicode(self.email)

    def update_field(self, key, value):
        """
        Set user field with give value and save to database.
        """
        user = Participant.query.get(self.email)
        setattr(user, key, value)  # same: user.key = value
        db.session.commit()

    def update_moves_id(self, moves_id):
        """
        Set moves_id field
        """
        if Participant.query.filter_by(moves_id=moves_id).first():
            return 'Already Exists'
        self.update_field('moves_id', moves_id)

    def is_authorized(self, label):
        """
        Return True if datastream label has been authenticated else False.
        """
        if label == 'moves':
            return self.moves_id and self.moves_access_token and self.moves_refresh_token
        elif label == 'gcal':
            return self.google_credentials
        elif label == 'pam':
            return self.pam_access_token and self.pam_refresh_token
        else:
            raise NotImplementedError("Auth failed for label: %s." % label)

    @classmethod
    def get_user(cls, email):
        """
        Return user object from database using primary_key(email).
        """
        return cls.query.get(email)

    @classmethod
    def get_all_users(cls):
        """
        Return list of all users from database.
        """
        return cls.query.all()

    @classmethod
    def from_profile(cls, profile, google_credentials):
        """
        Return new user or existing user from database using their profile information.
        """
        email = profile.get('email')
        if not cls.query.get(email):
            new_user = cls(profile, google_credentials)
            db.session.add(new_user)
            db.session.commit()

        user = cls.query.get(email)
        return user


#############################################################################################################
# Database model to store enrollment information
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(120), db.ForeignKey('participant.email'))
    exp_code = db.Column(db.String(10), db.ForeignKey('experiment_v2.code'))
    enrolled_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, data):
        self.participant_id = data.get('participant_id')
        self.exp_code = data.get('exp_code')

    def __repr__(self):
        result = {
            'participant_id': self.participant_id,
            'exp_code': self.exp_code,
            'enrolled_date': str(self.enrolled_date)
        }
        return json.dumps(result)

    @staticmethod
    def enroll(data):
        # Check if participant already registered
        # if Participant.query.filter_by(email=data['email']).first() == None:
        #     abort(400, "Participant not registered")

        # Check if already enrolled to prevent duplicate enrollment
        result = Enrollment.query.filter_by(exp_code=data['exp_code'], participant_id=data['participant_id']).count()
        if result > 0:
            response_message = {'message': 'Participant already enrolled in ' + data['exp_code']}
            http_response_code = 200
            resp = {}
            experiment = Experiment_v2.query.filter_by(code=data['exp_code']).first()
            resp['experiment'] = json.loads(str(experiment))
            protocols = Protocol.query.filter_by(exp_code=data['exp_code']).all()
            resp['protocols'] = json.loads(str(protocols))
            return (http_response_code, resp, result)

        new_enrollment = Enrollment(data)
        db.session.add(new_enrollment)
        db.session.commit()
        result = Enrollment.query.filter_by(exp_code=data['exp_code'], participant_id=data['participant_id'])
        if Enrollment.query.filter_by(exp_code=data['exp_code'], participant_id=data['participant_id']) is not None:
            http_response_code = 200
            resp = {}
            experiment = Experiment_v2.query.filter_by(code=data['exp_code']).first()
            resp['experiment'] = json.loads(str(experiment))
            protocols = Protocol.query.filter_by(exp_code=data['exp_code']).all()
            resp['protocols'] = json.loads(str(protocols))
            return (http_response_code, resp, result)
        else:
            response_message = {'error': 'Participant enrollment failed'}
            http_response_code = 500
        return (http_response_code, response_message, result)


class ProtocolPushNotif(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    exp_code = db.Column(db.String(10), db.ForeignKey('experiment_v2.code'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    frequency = db.Column(db.String(10))
    notif_details = db.Column(db.String(1600))
    notif_appid = db.Column(db.String(300))
    notif_type = db.Column(db.String(20))
    notif_time = db.Column(db.String(20))
    probable_half_notify = db.Column(db.Boolean, default=False)

    def __init__(self, data):
        self.label = data.get('label')
        self.exp_code = data.get('exp_code')
        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')
        self.frequency = data.get('frequency')
        self.notif_details = data.get('notif_details')
        self.notif_appid = data.get('notif_appid')
        self.notif_type = data.get('notif_type')
        self.notif_time = data.get('notif_time')
        self.probable_half_notify = data.get('probable_half_notify')

    def __repr__(self):
        result = {
            'id': self.id,
            'label': self.label,
            'exp_code': self.exp_code,
            'created_at': str(self.created_at),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'frequency': str(self.frequency),
            'notif_details': str(self.notif_details),
            'notif_appid': str(self.notif_appid),
            'notif_type': str(self.notif_type),
            'notif_time': str(self.notif_time),
            'probable_half_notify': str(self.probable_half_notify)
        }
        return json.dumps(result)

    @staticmethod
    def add_protocol(data):
        new_protocol = ProtocolPushNotif(data)
        db.session.add(new_protocol)
        db.session.commit()
        latest_protocol = ProtocolPushNotif.query.order_by('created_at desc').first()
        return 200, 'Successfully added intervention', latest_protocol

    @staticmethod
    def delete_protocol(pid):
        # deleted_protocol = ProtocolPushNotif.query.filter_by(id=pid)
        # ProtocolPushNotif.query.filter_by(id=pid).delete()
        p = db.session.query(ProtocolPushNotif).filter(ProtocolPushNotif.id == pid).first()
        db.session.delete(p)
        db.session.commit()
        return 200, 'Successfully deleted protocol.', p


class NotifEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment_v2.code'))

    alarm_millis = db.Column(db.BigInteger)
    ringer_mode = db.Column(db.String(10))
    title = db.Column(db.String(50))
    content = db.Column(db.String(50))
    app_id = db.Column(db.String(30))

    was_dismissed = db.Column(db.Boolean)
    event_time_millis = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.email = info['email']
        self.code = info['code']
        self.alarm_millis = info['alarm_millis']
        self.ringer_mode = info['ringer_mode']
        self.title = info['title']
        self.content = info['content']
        self.app_id = info['app_id']
        self.was_dismissed = info['was_dismissed']
        self.event_time_millis = info['event_time_millis']

    def __repr__(self):
        result = {
            'id': self.id,
            'email': self.email,
            'code': self.code,
            'alarm_millis': self.alarm_millis,
            'ringer_mode': self.ringer_mode,
            'title': self.title,
            'content': self.content,
            'app_id': self.app_id,
            'was_dismissed': self.was_dismissed,
            'event_time_millis': str(self.event_time_millis),
            'created_at': str(self.created_at)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        rows = info['logs'].split(';')

        for row in rows:
            if row == "" or info['email'] == "":
                continue

            email, code, alarm_millis, ringer_mode, title, content, app_id, was_dismissed, event_time_millis = \
                row.split(",")

            entry = {
                'email': email.strip('#'),  # temp fix because for some reason username has '#
                'code': code.strip(),
                'alarm_millis': alarm_millis,
                'ringer_mode': ringer_mode,
                'title': title,
                'content': content,
                'app_id': app_id,
                'was_dismissed': was_dismissed,
                'event_time_millis': event_time_millis
            }
            new_stat = NotifEvent(entry)
            db.session.add(new_stat)

        db.session.commit()
        return 200, 'Successfully added Notif Event!', ""


class InAppAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment_v2.code'))
    event_time_millis = db.Column(db.BigInteger)
    event_desc = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.email = info['email']
        self.code = info['code']
        self.event_time_millis = info['event_time_millis']
        self.event_desc = info['event_desc']

    def __repr__(self):
        result = {
            'id': self.id,
            'email': self.email,
            'code': self.code,
            'event_time_millis': str(self.event_time_millis),
            'event_desc': self.event_desc,
            'created_at': str(self.created_at)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        rows = info['logs'].split(';')
        for row in rows:
            if row == "" or info['email'] == "":
                continue

            event_time_millis, event_desc = row.split(",")
            entry = {
                'email': info['email'].strip('#'),
                'code': info['code'].strip(),
                'event_time_millis': event_time_millis,
                'event_desc': event_desc
            }
            new_stat = InAppAnalytics(entry)
            db.session.add(new_stat)

        db.session.commit()
        return 200, 'Successfully added InAppAnalytics Event!', ""

# TODO: have only one experiment table
# TODO: move to same place: Beehive Researcher, Participant, NotifEvent
# TODO: consider creating a beehive package instead of prefixing every file with Beehive
# TODO: increase the length of notification title and content
