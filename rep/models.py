"""
Implements all models (database tables)
"""
from rep import app
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
import json

db = SQLAlchemy(app)


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(120), unique=True)
    title = db.Column(db.String(120))
    rescuetime = db.Column(db.Boolean, default=False)
    aware = db.Column(db.Boolean, default=False)
    geofence = db.Column(db.Boolean, default=False)
    text_image = db.Column(db.Boolean, default=False)
    reminder = db.Column(db.Boolean, default=False)
    actuators = db.Column(db.Boolean, default=False)

    def __init__(self, info):
        self.title = info.get('title')
        self.code = str(uuid.uuid4())
        self.rescuetime = info.get('rescuetime')
        self.aware = info.get('aware')
        self.geofence = info.get('geofence')
        self.text_image = info.get('text_image')
        self.reminder = info.get('reminder')
        self.actuators = info.get('actuators')

    def __repr__(self):
        result = {
            'title': self.title,
            'code': self.code,
            'rescuetime': self.rescuetime,
            'aware': self.aware,
            'geofence': self.geofence,
            'text_image': self.text_image,
            'reminder': self.reminder,
            'actuators': self.actuators
        }
        return json.dumps(result)

    @staticmethod
    def add_experiment(info):
        existing_experiment = Experiment.query.filter_by(title=info['title']).first()
        if existing_experiment:
            return (-1, 'Experiment already exits.', existing_experiment)

        new_experiment = Experiment(info)
        db.session.add(new_experiment)
        db.session.commit()
        return (200, 'Successfully added experiment', new_experiment)

    @staticmethod
    def delete_experiment(code):
        experiment = Experiment.query.filter_by(code=code).delete()
        db.session.commit()

    @staticmethod
    def update_experiment(update):
        print '***********'
        print update
        print '***********'
        experiment = Experiment.query.filter_by(code=update['code']).first()

        experiment.title = update.get('title')
        experiment.code = update.get('code')
        experiment.rescuetime = update.get('rescuetime')
        experiment.aware = update.get('aware')
        experiment.geofence = update.get('geofence')
        experiment.text_image = update.get('text_image')
        experiment.reminder = update.get('reminder')
        experiment.actuators = update.get('actuators')
        db.session.commit()

        # experiment = Experiment.query.filter_by(code=update['code']).first()
        return experiment


class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(120))
    txt = db.Column(db.String(120))
    date = db.Column(db.String(120), unique=True)

    def __init__(self, image_url, txt, date):
        self.image_url = image_url
        self.txt = txt
        self.date = date

    def __repr__(self):
        return 'date: {} / has_image: {} / has_txt: {}'.format(self.date, self.image_url != None, self.txt != None)

    @staticmethod
    def add_intervention(info):
        existing_intervention = Intervention.query.filter_by(image_url=info['image_url']).first()
        if existing_intervention:
            return (-1, 'Intervention already exits.', existing_intervention)

        new_intervention = Intervention(info['image_url'], info['txt'], info['date'])
        db.session.add(new_intervention)
        db.session.commit()
        return (200, 'Successfully added intervention', new_intervention)


class Mturk(db.Model):
    worker_id = db.Column(db.String(120), primary_key=True, unique=True)
    moves_id = db.Column(db.String(120), unique=True)
    access_token = db.Column(db.String(120), unique=True)
    refresh_token = db.Column(db.String(120), unique=True)
    code = db.Column(db.String(120), unique=True)
    ip = db.Column(db.String(24))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def __repr__(self):
        return 'worker_id: {}/moves_id: {}'.format(self.worker_id, self.moves_id)

    @staticmethod
    def get_worker(worker_id):
        """
        Return user object from database using primary_key(email).
        """
        return Mturk.query.get(worker_id)

    @staticmethod
    def add_user(info):
        """ add new mturk user and return worker generated code if adding new worker """
        existing_worker = Mturk.query.filter_by(worker_id=info['worker_id']).first()
        existing_moves = Mturk.query.filter_by(moves_id=info['moves_id']).first()

        if existing_moves:
            return (-1, 'Moves app has already been connected. Contact Mturk requester.', existing_worker.code)
        elif existing_worker:
            return (-1, 'Worker has already been verified. Contact Mturk requester.', existing_worker.code)

        worker = Mturk(info['worker_id'])
        worker.moves_id = info['moves_id']
        worker.access_token = info['access_token']
        worker.refresh_token = info['refresh_token']
        worker.code = str(uuid.uuid4())
        worker.ip = str(info['ip'])

        db.session.add(worker)
        db.session.commit()

        return (200, 'Successfully connected your moves app!', worker.code)

    def update_field(self, key, value):
        """
        Set user field with give value and save to database.
        """
        worker = Mturk.query.get(self.worker_id)
        setattr(worker, key, value)
        db.session.commit()


class User(db.Model):

    # google login info and credentials for accessing google calendar
    email = db.Column(db.String(120), primary_key=True, unique=True)
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    gender = db.Column(db.String(10))
    picture = db.Column(db.String(120))
    google_credentials = db.Column(db.String(2500), unique=True)

    # activate datastreams
    is_location_active = db.Column(db.Boolean, default=False)
    is_mood_active = db.Column(db.Boolean, default=False)
    is_sn_active = db.Column(db.Boolean, default=False)

    # moves
    moves_id = db.Column(db.String(120), unique=True)
    moves_access_token = db.Column(db.String(120), unique=True)
    moves_refresh_token = db.Column(db.String(120), unique=True)

    # rescuetime
    rescuetime_access_token = db.Column(db.String(120), unique=True)
    rescuetime_refresh_token = db.Column(db.String(120), unique=True)

    # pam
    pam_access_token = db.Column(db.String(120), unique=True)
    pam_refresh_token = db.Column(db.String(120), unique=True)

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
        Returns `True`. User is always authenticated. Herp Derp.
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
        user = User.query.get(self.email)
        setattr(user, key, value)  # same: user.key = value
        db.session.commit()

    def update_moves_id(self, moves_id):
        """
        Set moves_id field
        """
        if User.query.filter_by(moves_id=moves_id).first():
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
