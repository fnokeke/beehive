import json, pytz
from rep import app
from flask import render_template, request, Response, redirect
from flask import url_for, flash, send_file, make_response
from flask_login import current_user, login_required
from rep.models import Experiment_v2, Enrollment, Participant, ProtocolPushNotif

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
    return render_template('experiment/researcher_experiments.html', **ctx)


@app.route('/experiment/<code>')
def experiment_options(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first(),
        'protocols': ProtocolPushNotif.query.filter_by(exp_code=code).all()
    }
    return render_template('experiment/create-edit-experiment.html', **ctx)


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


# Endpoint to display participants in an experiment
@app.route('/participants/experiment/<code>')
def experiment_participants(code):
    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id). \
        add_columns(Participant.firstname, Participant.lastname, Participant.gender, Participant.created_at).filter(
        Enrollment.exp_code == code).all()

    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first(),
        'participants': participants
    }
    return render_template('experiment/experiment-participants.html', **ctx)


# Endpoint to download participants in an experiment
@app.route('/download/participants/experiment/<code>')
def experiment_participants_download(code):
    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id). \
        add_columns(Participant.firstname, Participant.lastname, Participant.gender, Participant.created_at).filter(
        Enrollment.exp_code == code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"

    count = 1
    for participant in participants:
        # Download and save calender
        csv_data = csv_data + "\n"
        row = str(count) +  "," + str(participant[0]) + "," + str(participant.firstname) + "," + \
              str(participant.lastname) + "," + str(participant.gender) + "," + str(participant.created_at)
        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-participants.csv"
    try:
        response = make_response(csv_data)
        cd = 'attachment; filename=beehive-' + download_name
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response

    except Exception as e:
        return redirect(url_for('experiment_participants', code=code))