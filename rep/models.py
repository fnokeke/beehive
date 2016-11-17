"""
Implements all models (database tables)
"""
from rep import app
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy(app)


class Mturk(db.Model):
    worker_id = db.Column(db.String(120), primary_key=True, unique=True)
    moves_id = db.Column(db.String(120), unique=True)
    access_token = db.Column(db.String(120), unique=True)
    refresh_token = db.Column(db.String(120), unique=True)
    code = db.Column(db.String(120), unique=True)

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

        if existing_worker:
            return (-1, 'Worker already exists', existing_worker.code)
        elif existing_moves:
            return (-1, 'Moves Account Already exists', existing_worker.code)

        worker = Mturk(info['worker_id'])
        worker.moves_id = info['moves_id']
        worker.access_token = info['access_token']
        worker.refresh_token = info['refresh_token']
        worker.code = str(uuid.uuid4())

        db.session.add(worker)
        db.session.commit()

        return (200, 'Successfully added', worker.code)

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
