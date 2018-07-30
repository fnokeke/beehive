from db_init import db
from utils import to_json
from flask import Response, abort
from sqlalchemy import create_engine

import datetime
import json
import uuid

from config import SQLALCHEMY_DATABASE_URI


# Database model for experiments


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True)
    label = db.Column(db.String(120))
    title = db.Column(db.String(120))
    description = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rescuetime = db.Column(db.Boolean, default=False)
    calendar = db.Column(db.Boolean, default=False)
    phone_notif = db.Column(db.Boolean, default=False)
    screen_events = db.Column(db.Boolean, default=False)
    app_usage = db.Column(db.Boolean, default=False)
    protocols = db.relationship('Protocol', backref='experiment', lazy='select')
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    owner = db.Column(db.String(120), db.ForeignKey('researcher.email'))

    def __init__(self, info):
        self.code = info.get('code') if info.get('code') else Experiment.generate_unique_id()
        self.label = info.get('label')
        self.title = info.get('title')
        self.description = info.get('description')
        self.start_date = info['start_date']
        self.end_date = info['end_date']
        self.rescuetime = info.get('rescuetime')
        self.calendar = info.get('calendar')
        self.phone_notif = info.get('phone_notif')
        self.screen_events = info.get('screen_events')
        self.app_usage = info.get('app_usage')
        self.owner = info['owner']

        print 'info[start_date] = ', info['start_date']

    def __repr__(self):
        result = {
            'owner': self.owner,
            'code': self.code,
            'label': self.label,
            'title': self.title,
            'description': self.description,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'rescuetime': self.rescuetime,
            'calendar': self.calendar,
            'phone_notif': self.phone_notif,
            'screen_events': self.screen_events,
            'app_usage': self.app_usage,
            'created_date': str(self.created_date)
        }
        return json.dumps(result)

    @staticmethod
    def generate_unique_id():
        code = str(uuid.uuid4())[:6]
        while Experiment.query.filter_by(code=code).first():
            code = str(uuid.uuid4())[:6]
        return code

    @staticmethod
    def add_experiment(info):
        msg = "New experiment was successfully created."
        existing_experiment = Experiment.query.filter_by(owner=info['owner'], label=info['label']).first()
        if existing_experiment:  # recreate new experiment with updated details but same code
            # Experiment.delete_experiment(existing_experiment.code)
            info['code'] = existing_experiment.code
            Experiment.update_experiment(info)
            return 200, "Experiment was successfully updated.", info

        new_experiment = Experiment(info)
        db.session.add(new_experiment)
        db.session.commit()
        # new_experiment = Experiment.query.filter_by(owner=exp['owner'], label=exp['label']).first()

        # Add protocols  to protocols table
        protocols = json.loads(info['protocols'])
        for p in protocols:
            p['exp_code'] = new_experiment.code
            Protocol.add_protocol(p)

        return 200, msg, new_experiment

    @staticmethod
    def delete_experiment(code):
        e = db.session.query(Experiment).filter(Experiment.code == code).first()
        db.session.delete(e)
        db.session.commit()
        # Experiment.query.filter_by(code=code).delete()
        # Protocol.query.filter_by(code=code).delete()
        # db.session.commit()

    @staticmethod
    def update_experiment(info):
        experiment = Experiment.query.filter_by(code=info['code']).first()
        experiment.label = info.get('label')
        experiment.title = info.get('title')
        experiment.description = info.get('description')
        experiment.start_date = info.get('start_date')
        experiment.end_date = info.get('end_date')
        experiment.rescuetime = info.get('rescuetime')
        experiment.calendar = info.get('calendar')
        experiment.phone_notif = info.get('phone_notif')
        experiment.screen_events = info.get('screen_events')
        experiment.app_usage = info.get('app_usage')

        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        stmt = Protocol.__table__.delete().where(Protocol.exp_code == info['code'])
        engine.execute(stmt)
        # db.session.commit()

        # for p in db.session.query(Protocol).filter_by(code=info['code']).all():
        #     db.session.delete(p)
        #     db.session.commit()

        # stmt = Users.__table__.delete().where(Users.id.in_(subquery...))

        protocols = json.loads(info['protocols'])
        for p in protocols:
            p['exp_code'] = info['code']
            Protocol.add_protocol(p)

        db.session.commit()

        # p = db.session.query(Protocol).filter(Protocol.id == pid).first()
        # db.session.delete(p)
        # db.session.commit()



        return experiment

    @staticmethod
    def update_group(update):
        experiment = Experiment.query.filter_by(code=update['code']).first()
        return experiment


class Researcher(db.Model):
    # google login info and credentials for accessing google calendar
    email = db.Column(db.String(50), primary_key=True, unique=True)
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
    email = db.Column(db.String(50), primary_key=True, unique=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    google_credentials = db.Column(db.String(2500), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, profile, google_credentials):
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
        Returns `True`. Participant is always authenticated.
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
    exp_code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
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
            experiment = Experiment.query.filter_by(code=data['exp_code']).first()
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
            experiment = Experiment.query.filter_by(code=data['exp_code']).first()
            resp['experiment'] = json.loads(str(experiment))
            protocols = Protocol.query.filter_by(exp_code=data['exp_code']).all()
            resp['protocols'] = json.loads(str(protocols))
            return (http_response_code, resp, result)
        else:
            response_message = {'error': 'Participant enrollment failed'}
            http_response_code = 500
        return (http_response_code, response_message, result)


class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120))
    exp_code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    frequency = db.Column(db.String(10))
    method = db.Column(db.String(20))
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
        self.method = data.get('method')
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
            'method': str(self.method),
            'notif_details': str(self.notif_details),
            'notif_appid': str(self.notif_appid),
            'notif_type': str(self.notif_type),
            'notif_time': str(self.notif_time),
            'probable_half_notify': str(self.probable_half_notify)
        }
        return json.dumps(result)

    @staticmethod
    def add_protocol(data):
        new_protocol = Protocol(data)
        db.session.add(new_protocol)
        db.session.commit()
        latest_protocol = Protocol.query.order_by('created_at desc').first()
        return 200, 'Successfully added intervention', latest_protocol

    @staticmethod
    def delete_protocol(pid):
        p = db.session.query(Protocol).filter(Protocol.id == pid).first()
        db.session.delete(p)
        db.session.commit()
        return 200, 'Successfully deleted protocol.', p


class NotifEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))

    alarm_millis = db.Column(db.BigInteger)
    ringer_mode = db.Column(db.String(10))
    method = db.Column(db.String(20))
    title = db.Column(db.String(120))
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
        self.method = info['method']
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
            'method': self.method,
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
        rows = info['logs'].split('\n')

        for row in rows:
            if row == "" or info['email'] == "":
                continue

            email, code, alarm_millis, ringer_mode, method, title, content, app_id, was_dismissed, event_time_millis = \
                row.split(",")

            entry = {
                'email': email.strip('#'),  # temp fix because for some reason username has '#
                'code': code.strip(),
                'alarm_millis': alarm_millis,
                'ringer_mode': ringer_mode,
                'method': method,
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
    email = db.Column(db.String(50), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
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
        rows = info['logs'].split('\n')
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


class MobileUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
    email = db.Column(db.String(50), db.ForeignKey('participant.email'))
    last_installed_ms = db.Column(db.String(30))
    pretty_last_installed = db.Column(db.String(30))
    app_version_name = db.Column(db.String(10))
    app_version_code = db.Column(db.String(10))
    phone_model = db.Column(db.String(30))
    android_version = db.Column(db.String(10))
    device_country = db.Column(db.String(10))
    device_id = db.Column(db.String(30))

    def __init__(self, info):
        self.code = info['code']
        self.email = info['email']
        self.last_installed_ms = info['last_installed_ms']
        self.pretty_last_installed = info['pretty_last_installed']
        self.app_version_name = info['app_version_name']
        self.app_version_code = info['app_version_code']
        self.phone_model = info['phone_model']
        self.android_version = info['android_version']
        self.device_country = info['device_country']
        self.device_id = info['device_id']

    def __repr__(self):
        result = {
            'email': self.email,
            'code': self.code,
            'last_installed_ms': self.last_installed_ms,
            'pretty_last_installed': self.pretty_last_installed,
            'app_version_name': self.app_version_name,
            'app_version_code': self.app_version_code,
            'phone_model': self.phone_model,
            'device_id': self.device_id,
            'device_country': self.device_country,
            'android_version': self.android_version}
        return json.dumps(result)

    @classmethod
    def register(cls, data):
        code = data['code']
        experiment = Experiment.query.filter_by(code=code).first()
        if not experiment:
            return 400, "Experiment doesn't exist"

        # already in experiment so no need to change anything
        user_in_experiment = MobileUser.query.filter_by(email=data['email'], code=code).first()
        if user_in_experiment:
            return 200, "Already registered. Welcome back!"

        # enrolling as first timer in an experiment
        new_user = MobileUser(data)
        db.session.add(new_user)
        db.session.commit()
        return 200, "Successfully registered!"

    @staticmethod
    def add_user(info):
        existing_user = MobileUser.query.filter_by(email=info['email']).first()
        if existing_user:
            return (-1, 'Welcome back ' + existing_user.email, existing_user)

        new_user = MobileUser(info)
        db.session.add(new_user)
        db.session.commit()

        return (200, 'Successfully enrolled in experiment.', new_user)


class PAM(db.Model):
    __tablename__ = "pam"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
    timestamp_z = db.Column(db.String)
    affect_arousal = db.Column(db.String)
    affect_valence = db.Column(db.String)
    positive_affect = db.Column(db.String)
    mood = db.Column(db.String)
    negative_affect = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.email = info['email']
        self.code = info['code']
        self.timestamp_z = info['timestamp_z']
        self.affect_arousal = info['affect_arousal']
        self.affect_valence = info['affect_valence']
        self.positive_affect = info['positive_affect']
        self.mood = info['mood']
        self.negative_affect = info['negative_affect']

    def __repr__(self):
        result = {
            'email': self.email,
            'code': self.code,
            'timestamp_z': self.timestamp_z,
            'affect_arousal': self.affect_arousal,
            'affect_valence': self.affect_valence,
            'positive_affect': self.positive_affect,
            'mood': self.mood,
            'negative_affect': self.negative_affect,
            'created_at': str(self.created_at)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        rows = info['logs'].split('\n')
        if len(rows) > 0:
            headers = rows[0].split(',')
            for row in rows[1:]:
                if row == "":
                    print "No data in row"
                    continue
                print
                print
                print '**************************'
                print headers
                print row
                print '**************************'
                values = row.split(',')
                entry = {
                    'email': info['email'].strip('#'),
                    'code': info['code'].strip(),
                    'timestamp_z': '' if 'timestamp' not in headers else values[headers.index('timestamp')],
                    'affect_arousal': '' if 'affect_arousal' not in headers else values[headers.index('affect_arousal')],
                    'affect_valence': '' if 'affect_valence' not in headers else values[headers.index('affect_valence')],
                    'positive_affect': '' if 'positive_affect' not in headers else values[headers.index('positive_affect')],
                    'mood': '' if 'mood' not in headers else values[headers.index('mood')],
                    'negative_affect': '' if 'negative_affect' not in headers else values[headers.index('negative_affect')]
                }
                new_stat = PAM(entry)
                db.session.add(new_stat)
                db.session.commit()
        return 200, 'Successfully added PAM log!', ""


class MobileSurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('participant.email'))
    code = db.Column(db.String(10), db.ForeignKey('experiment.code'))
    header = db.Column(db.String(200))
    response = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.email = info['email']
        self.code = info['code']
        self.header = info['header']
        self.response = info['response']

    def __repr__(self):
        result = {
            'email': self.email,
            'code': self.code,
            'header': self.header,
            'response': self.response,
            'created_at': str(self.created_at)
        }
        return json.dumps(result)

    @staticmethod
    def add_stats(info):
        rows = info['logs'].split('\n')
        if rows == "":
            print
            print '***************No survey data.***************'
            print

        header = rows[0]
        response = ';'.join(rows[1:])
        if len(rows) > 0 and header != "" and response != "":
            entry = {
                'email': info['email'].strip('#'),
                'code': info['code'].strip(),
                'header': header,
                'response': response
            }
            new_stat = MobileSurvey(entry)
            db.session.add(new_stat)
            db.session.commit()

        return 200, 'Successfully added survey log!', len(rows)

# TODO: have only one experiment table
# TODO: move to same place: Beehive Researcher, Participant, NotifEvent
# TODO: consider creating a beehive package instead of prefixing every file with Beehive
# TODO: increase the length of notification title and content
