"""
Implements all models (database tables)
"""
from rep import app
from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
import json

db = SQLAlchemy(app)


class Imageintv(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, image_url):
        id = db.Column(db.Integer, primary_key=True)
        self.image_url = image_url
        created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        result = {'image_url': self.image_url, 'created_at': str(self.created_at)}
        return json.dumps(result)

    @staticmethod
    def add_image_url(image_url):
        if Imageintv.query.filter_by(image_url=image_url).first():
            return

        new_image_url = Imageintv(image_url)
        db.session.add(new_image_url)
        db.session.commit()


class Textintv(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1500))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, text):
        self.text = text
        created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        result = {'text': self.text, 'created_at': str(self.created_at)}
        return json.dumps(result)

    @staticmethod
    def add_text(text):
        if Textintv.query.filter_by(text=text).first():
            return

        new_text = Textintv(text)
        db.session.add(new_text)
        db.session.commit()


class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    group = db.Column(db.String(1500))
    start = db.Column(db.String(120))
    every = db.Column(db.String(30))
    when = db.Column(db.String(30))
    repeat = db.Column(db.String(30))

    def __init__(self, info):
        group = info['group']
        start = info['start']
        every = info['every']
        when = info['when']
        repeat = info['repeat']

    def __repr__(self):
        result = {
            'group': self.group,
            'start': self.start,
            'every': self.every,
            'when': self.when,
            'repeat': self.repeat
        }
        return json.dumps(result)

    @staticmethod
    def add_intervention(info):
        new_intervention = Intervention(info)
        db.session.add(new_intervention)
        db.session.commit()
        latest_intervention = Intervention.query.order_by('created_at desc').first()
        return (200, 'Successfully added intervention', latest_intervention)


class MobileUser(db.Model):
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    code = db.Column(db.String(10))
    email = db.Column(db.String(120), primary_key=True, unique=True)

    def __init__(self, info):
        self.firstname = info['firstname']
        self.lastname = info['lastname']
        self.email = info['email']
        self.code = info['code']

    def __rep__(self):
        result = {'firstname': self.firstname, 'lastname': self.lastname, 'email': self.email, 'code': self.code}
        return json.dumps(result)

    @staticmethod
    def add_user(info):
        existing_user = MobileUser.query.filter_by(email=info['email']).first()
        if existing_user:
            return (-1, 'Welcome back.', existing_user)

        new_user = MobileUser(info)
        db.session.add(new_user)
        db.session.commit()

        new_user = MobileUser.query.filter_by(email=info['email']).first()
        return (200, 'Successfully added as a new user.', new_user)


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True)
    title = db.Column(db.String(120))
    rescuetime = db.Column(db.Boolean, default=False)
    aware = db.Column(db.Boolean, default=False)
    geofence = db.Column(db.Boolean, default=False)
    text = db.Column(db.Boolean, default=False)
    image = db.Column(db.Boolean, default=False)
    reminder = db.Column(db.Boolean, default=False)
    actuators = db.Column(db.Boolean, default=False)

    def __init__(self, info):
        self.title = info.get('title')
        self.code = Experiment.generate_unique_id()
        self.rescuetime = info.get('rescuetime')
        self.aware = info.get('aware')
        self.geofence = info.get('geofence')
        self.text = info.get('text')
        self.image = info.get('image')
        self.reminder = info.get('reminder')
        self.actuators = info.get('actuators')

    def __repr__(self):
        result = {
            'title': self.title,
            'code': self.code,
            'rescuetime': self.rescuetime,
            'aware': self.aware,
            'geofence': self.geofence,
            'text': self.text,
            'image': self.image,
            'reminder': self.reminder,
            'actuators': self.actuators
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
        existing_experiment = Experiment.query.filter_by(title=info['title']).first()
        if existing_experiment:
            return (-1, 'Experiment already exits.', existing_experiment)

        new_experiment = Experiment(info)
        db.session.add(new_experiment)
        db.session.commit()
        new_experiment = Experiment.query.filter_by(title=info['title']).first()
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
        experiment.text = update.get('text')
        experiment.image = update.get('image')
        experiment.reminder = update.get('reminder')
        experiment.actuators = update.get('actuators')
        db.session.commit()

        # experiment = Experiment.query.filter_by(code=update['code']).first()
        return experiment


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
        self.code = Mturk.generate_unique_id()

    def __repr__(self):
        return 'worker_id: {}/moves_id: {}'.format(self.worker_id, self.moves_id)

    @staticmethod
    def generate_unique_id():
        code = str(uuid.uuid4())[:6]
        while Mturk.query.filter_by(code=code).first():
            code = str(uuid.uuid4())[:6]
        return code

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
