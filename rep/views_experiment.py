from rep import app
from flask import render_template, request, Response
from flask_login import current_user, login_required
from rep.models import Experiment_v2

from datetime import datetime


@app.route('/experiments/create')
def create_experiment():
    ctx = {
        'today_date': datetime.now().strftime('%Y-%m-%d')
    }
    return render_template('create-edit-experiment.html', **ctx)


@app.route('/experiments')
@login_required
def experiments():
    ctx = {
        'user_type': 'researcher',
        'experiments': Experiment_v2.query.filter_by(owner=current_user.email).all()
    }
    return render_template('researcher_experiments.html', **ctx)


@app.route('/experiment/<code>')
def experiment_options(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first()
    }
    return render_template('create-edit-experiment.html', **ctx)


# Endpoint to add new experiment to the database v2
@app.route('/add/experiment/v2', methods=['POST'])
def add_experiment_v2():
    experiment = request.form.to_dict()
    status, response, _ = Experiment_v2.add_experiment(experiment)

    print 'experiment to add: '
    print experiment
    if status == 200:
        return response
    else:
        return Response(response, status=status, mimetype='application/json')
