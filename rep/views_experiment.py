import json
from datetime import datetime

import requests
from flask import render_template, request, Response, redirect
from flask import url_for, flash
from flask_login import current_user, login_required

import secret_keys
import utils
from rep import app
from rep.models import Experiment, Protocol

TEMP_DIR = "./temp"


@app.route('/experiments/create')
def create_experiment():
    ctx = {
        'today_date': datetime.now().strftime('%Y-%m-%d')
    }
    return render_template('experiment/create-edit-experiment.html', **ctx)


@app.route('/delete/experiment/<code>')
def delete_experiment(code):
    Experiment.delete_experiment(code)
    flash('Successfully deleted research study.', 'success')
    return redirect(url_for('researcher_view'))


@app.route('/experiments')
@login_required
def experiments():
    ctx = {
        'user_type': 'researcher',
        'experiments': Experiment.query.filter_by(owner=current_user.email).all()
    }
    return render_template('experiment/researcher_experiments.html', **ctx)


@app.route('/experiment/<code>')
def experiment_options(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'experiment_page': True
    }
    ctx['show_pam'] = utils.get_state("pam", ctx['protocols'])
    ctx['show_survey'] = utils.get_state("push_survey", ctx['protocols'])
    return render_template('experiment/create-edit-experiment.html', **ctx)


def update_firebase_topic(code):
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {'Authorization': secret_keys.FIREBASE_KEY, 'content-type': 'application/json'}
    topic = '/topics/' + code
    data = json.dumps({'to': topic, 'data': {'type': 'syncStudy'}})
    requests.post(url, headers=headers, data=data)


def is_editing(experiment):
    return 'code' in experiment


@app.route('/add/experiment', methods=['POST'])
def add_experiment():
    experiment = request.form.to_dict()
    status, response, _ = Experiment.add_experiment(experiment)

    if is_editing(experiment):
        update_firebase_topic(experiment['code'])

    if status == 200:
        return response
    else:
        return Response(response, status=status, mimetype='application/json')


@app.route('/instructions/experiment/<code>')
def experiment_instructions(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first()
    }
    return render_template('experiment/experiment-instructions.html', **ctx)

