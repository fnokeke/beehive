from db_init import db
from utils import to_json
from flask import Response, abort

import datetime
import json
import uuid

#############################################################################################################
# Database model for experiments
class Experiment_v2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True)
    label = db.Column(db.String(120))
    title = db.Column(db.String(120))
    description = db.Column(db.String(250))
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    screen_events = db.Column(db.Boolean, default=False)
    app_usage = db.Column(db.Boolean, default=False)
    protocols = db.relationship('Protocol', backref='experiment', lazy='select')
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.code = info.get('code') if info.get('code') else Experiment_v2.generate_unique_id()
        self.label = info.get('label')
        self.title = info.get('title')
        self.description = info.get('description')
        self.start_date = info['start_date']
        self.end_date = info['end_date']
        self.screen_events = info.get('screen_events')
        self.app_usage = info.get('app_usage')

    def __repr__(self):
        result = {
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
    def add_experiment(info, protocols):
        existing_experiment = Experiment_v2.query.filter_by(title=info['title']).first()
        if existing_experiment:
            #return  Response('Experiment with that name exists', status=400, mimetype='application/json')
            return (400, 'Experiment with that title exists', existing_experiment)

        new_experiment = Experiment_v2(info)
        db.session.add(new_experiment)
        db.session.commit()
        new_experiment = Experiment_v2.query.filter_by(title=info['title']).first()

        # To DO:  Add protocols  to protocols table
        return (200, 'Successfully added experiment', new_experiment)
        #return Response("{'Experiment successfully created'}", status=200, mimetype='application/json')


    @staticmethod
    def delete_experiment(code):
        Experiment_v2.query.filter_by(code=code).delete()
        Protocol.query.filter_by(code=code).delete()
        db.session.commit()

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

#############################################################################################################
# Database model to store protocols for an experiment
class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #exp_id = db.Column(db.Integer, db.ForeignKey('experiment_v2.id'))
    exp_code = db.Column(db.String(10), db.ForeignKey('experiment_v2.code'))
    frequency = db.Column(db.String(120))
    method = db.Column(db.String(120))
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, info):
        self.exp_code = info['exp_code']
        self.frequency = info['frequency']
        self.method = info['method']
        self.start_date = info['start_date']
        self.end_date = info['end_date']
        self.start_time = info['start_time']
        self.end_time = info['end_time']
        self.created_date = info['created_date']


    def __repr__(self):
        result = {
            'id': self.id,
            'exp_code': self.exp_code,
            'frequency': str(self.frequency),
            'method': str(self.method),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'created_date': str(self.created_date)
        }
        return json.dumps(result)

    @staticmethod
    def add_protocol(info):
        new_protocol = Protocol(info)
        db.session.add(new_protocol)
        db.session.commit()
        latest_protocol = Protocol.query.order_by('created_at desc').first()
        return (200, 'Successfully added intervention', latest_protocol)

    @staticmethod
    def delete_protocol(id):
        deleted_protocol = Protocol.query.filter_by(id=id)
        Protocol.query.filter_by(id=id).delete()
        db.session.commit()
        return (200, 'Successfully deleted protocol.', deleted_protocol)


#############################################################################################################
# Database model to store enrollment information
# class Participant(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(250))
#     google_oauth = db.Column(db.String(250))
#     oauth_token = db.Column(db.String(250))
#     registered_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#
#     def __init__(self, info):
#         self.email = info.get('email')
#         self.google_oauth = info.get('google_oauth')
#         self.oauth_token = info.get('oauth_token')
#
#     def __repr__(self):
#         result = {
#             'id': self.id,
#             'email': self.email,
#             'google_oauth': self.google_oauth,
#             'oauth_token' : self.oauth_token,
#             'registered_date': str(self.registered_date)
#         }
#         return json.dumps(result)
#
#
#     @staticmethod
#     def register(data):
#         # Check if participant already registered
#         result = Participant.query.filter_by(email=data['email']).count()
#         print 'count: ', result
#         print 'data:' , data
#
#         if result > 0:
#             response_message = {'message' : 'Participant already enrolled'}
#             http_response_code = 200
#             return (http_response_code, response_message, str(result))
#
#         new_participant = Participant(data)
#         db.session.add(new_participant)
#         db.session.commit()
#
#         result = Participant.query.filter_by(email=data['email']).count()
#         if result>0:
#             response_message = {'message': 'Participant enrolled successfully'}
#             http_response_code = 200
#         else:
#             response_message = {'error': 'Participant enrollment failed'}
#             http_response_code = 500
#         return (http_response_code, response_message, result)


#############################################################################################################
# Database model to store participant information
class Participant(db.Model):
    # google login info and credentials for accessing google calendar
    id = db.Column(db.Integer, autoincrement=True)
    email = db.Column(db.String(120), primary_key=True, unique=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    picture = db.Column(db.String(120))
    google_credentials = db.Column(db.String(2500), unique=True)

    omh_access_token = db.Column(db.String(120))
    omh_refresh_token = db.Column(db.String(120))

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
            response_message = {'message' : 'Participant already enrolled in ' + data['exp_code']}
            http_response_code = 200
            return (http_response_code, response_message, str(result))

        new_enrollment = Enrollment(data)
        db.session.add(new_enrollment)
        db.session.commit()
        result = Enrollment.query.filter_by(exp_code=data['exp_code'], participant_id=data['participant_id'])
        if Enrollment.query.filter_by(exp_code=data['exp_code'], participant_id=data['participant_id']) is not None:
            response_message = {'message' : 'Participant enrolled successfully'}
            http_response_code = 200
        else:
            response_message = {'error': 'Participant enrollment failed'}
            http_response_code = 500
        return (http_response_code, response_message, result)
