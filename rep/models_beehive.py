from db_init import db
from utils import to_json
from flask import Response

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
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    screen_events = db.Column(db.Boolean, default=False)
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

    def __repr__(self):
        result = {
            'code': self.code,
            'label': self.label,
            'title': self.title,
            'description': self.description,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'screen_events': self.screen_events,
            'protocols': to_json(self.protocols),
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


# Database model for experiments
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
        self.code = info['code']
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
            'code': self.code,
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

