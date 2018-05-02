import json, pytz
from rep import app
from flask import render_template, request, Response, redirect
from flask import url_for, flash, send_file, make_response
from flask_login import current_user, login_required
from rep.models import Experiment_v2, Enrollment, Participant, ProtocolPushNotif
from rep.models import InAppAnalytics

from datetime import datetime


@app.route('/experiments/create')
def create_experiment():
    ctx = {
        'today_date': datetime.now().strftime('%Y-%m-%d')
    }
    return render_template('experiment/create-edit-experiment.html', **ctx)


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
        'protocols': ProtocolPushNotif.query.filter_by(exp_code=code).all(),
        'experiment_page': True
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
    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id)\
        .add_columns(Participant.email, Participant.firstname, Participant.lastname, Participant.gender, Participant.created_at)\
        .filter(Enrollment.exp_code == code).all()

    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first(),
        'protocols': ProtocolPushNotif.query.filter_by(exp_code=code).all(),
        'participants': participants,
        'dashboard_page': True
    }
    return render_template('experiment/experiment-participants.html', **ctx)


# Endpoint to download participants in an experiment
@app.route('/download/participants/experiment/<code>')
def experiment_participants_download(code):
    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id)\
        .add_columns(Participant.email, Participant.firstname, Participant.lastname, Participant.gender, Participant.created_at)\
        .filter(Enrollment.exp_code == code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"

    count = 1
    for participant in participants:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) +  "," + str(participant.email) + "," + str(participant.firstname) + "," + \
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


# Endpoint to display App analytics for an experiment
@app.route('/app-analytics/experiment/<code>')
def experiment_app_analytics(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first(),
        'protocols': ProtocolPushNotif.query.filter_by(exp_code=code).all(),
        'events': InAppAnalytics.query.filter_by(code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-app-analytics.html', **ctx)



# Endpoint to download app analytics for an experiment
@app.route('/download/app-analytics/experiment/<code>')
def experiment_app_analytics_download(code):
    events = InAppAnalytics.query.filter_by(code=code).all()
    csv_data = "NO," + "EMAIL," + "EVENT TIME (millis)," + "EVENT DESCRIPTION,"  + "EVENT DATE"

    count = 1
    for event in events:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) +  "," + str(event.email) + "," + str(event.event_time_millis) + "," + \
              str(event.event_desc) + "," + str(event.created_at)
        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-app-analytics.csv"
    try:
        response = make_response(csv_data)
        cd = 'attachment; filename=beehive-' + download_name
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response

    except Exception as e:
        return redirect(url_for('experiment_app_analytics', code=code))


# Endpoint to display protocols for an experiment
@app.route('/protocols/experiment/<code>')
def experiment_protocols(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment_v2.query.filter_by(code=code).first(),
        'protocols': ProtocolPushNotif.query.filter_by(exp_code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-protocols.html', **ctx)


# Endpoint to download protocols for an experiment
@app.route('/download/protocols/experiment/<code>')
def experiment_protocols_download(code):
    protocols = ProtocolPushNotif.query.filter_by(exp_code=code).all()
    csv_data = "NO," + "LABEL," + "START DATE," + "END DATE," + "FREQUENCY," + "METHOD," + "DETAILS," \
               + "APP ID," + "TYPE," + "TIME," + "HALF NOTIFY,"

    count = 1
    for protocol in protocols:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) +  "," + str(protocol.label) + "," + str(protocol.start_date) + "," + str(protocol.end_date) \
              + "," + str(protocol.frequency) + "," + str(protocol.method) + "," + str(protocol.notif_details) \
              + "," + str(protocol.notif_appid) + "," + str(protocol.notif_type) + "," + str(protocol.notif_time) \
              + "," + str(protocol.probable_half_notify)

        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-protocols.csv"
    try:
        response = make_response(csv_data)
        cd = 'attachment; filename=beehive-' + download_name
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response

    except Exception as e:
        return redirect(url_for('experiment_protocols', code=code))