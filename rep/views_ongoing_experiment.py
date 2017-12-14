from rep import app
from flask import render_template
from flask_login import current_user, login_required
from rep.models import Experiment_v2, Researcher

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
        'experiment': Experiment_v2.query.filter_by(code=code).first()
    }
    return render_template('experiment-options.html', **ctx)


