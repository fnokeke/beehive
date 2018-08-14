import json, pytz
from rep import app
from flask import render_template, request, Response, redirect
from flask import url_for, flash, send_file, make_response
from flask_login import current_user, login_required
from rep.models import Experiment, Enrollment, Participant, Protocol, MobileUser
from rep.models import InAppAnalytics, TP_FgAppLog, TP_ScreenLog, RescuetimeUser
from io import BytesIO
from datetime import datetime

import time, os
import requests
import json
import secret_keys
import zipfile, shutil

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

# Endpoint to display participants in an experiment
@app.route('/participants/experiment/<code>')
def experiment_participants(code):
    # participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id)\
    #     .add_columns(Participant.email, Participant.firstname, Participant.lastname, Participant.gender, Participant.created_at)\
    #     .filter(Enrollment.exp_code == code).all()

    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'participants': MobileUser.query.filter_by(code=code).all(),
        'rescuetime_participants': RescuetimeUser.query.filter_by(code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-participants.html', **ctx)


# Endpoint to download participants in an experiment
@app.route('/download/participants/experiment/<code>')
def experiment_participants_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id) \
        .add_columns(Participant.email, Participant.firstname, Participant.lastname, Participant.gender,
                     Participant.created_at) \
        .filter(Enrollment.exp_code == code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"

    count = 1
    for participant in participants:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(participant.email) + "," + str(participant.firstname) + "," + \
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


# Endpoint to download rescuetime participants in an experiment
@app.route('/download/rescuetime-participants/experiment/<code>')
def experiment_rescuetime_participants_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    participants = RescuetimeUser.query.filter_by(code=code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"

    count = 1
    for participant in participants:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(participant.email) + "," + str(participant.firstname) + "," + \
              str(participant.lastname) + "," + str(participant.gender) + "," + str(participant.created_at)
        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-rescuetime-participants.csv"
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
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'events': InAppAnalytics.query.filter_by(code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-app-analytics.html', **ctx)


# Endpoint to download app analytics for an experiment
@app.route('/download/app-analytics/experiment/<code>')
def experiment_app_analytics_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403
    events = InAppAnalytics.query.filter_by(code=code).all()
    csv_data = "NO," + "EMAIL," + "EVENT TIME (millis)," + "EVENT DESCRIPTION," + "EVENT DATE"

    count = 1
    for event in events:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(event.email) + "," + str(event.event_time_millis) + "," + \
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
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-protocols.html', **ctx)


# Endpoint to download protocols for an experiment
@app.route('/download/protocols/experiment/<code>')
def experiment_protocols_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    protocols = Protocol.query.filter_by(exp_code=code).all()
    csv_data = "NO," + "LABEL," + "START DATE," + "END DATE," + "FREQUENCY," + "METHOD," + "DETAILSKO," \
               + "APP ID," + "TYPE," + "TIME," + "HALF NOTIFY,"

    count = 1
    for protocol in protocols:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(protocol.label) + "," + str(protocol.start_date) + "," + str(protocol.end_date) \
              + "," + str(protocol.frequency) + "," + str(protocol.method) + "," + str(protocol.notif_details.substr(0,15)) + "...}" \
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


# Endpoint to display App usage for an experiment
@app.route('/app-usage/experiment/<code>')
def experiment_app_usage(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'app_usage': TP_FgAppLog.query.filter_by(code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-app-usage.html', **ctx)


# Endpoint to download protocols for an experiment
@app.route('/download/app-usage/experiment/<code>')
def experiment_app_usage_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    app_usage = TP_FgAppLog.query.filter_by(code=code).all()
    csv_data = "NO," + "WORKER ID," + "APP ID," + "TIME (seconds)," + "TIME (millis)," + "DATE"

    count = 1
    for app in app_usage:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(app.worker_id) + "," + str(app.app_id) + "," + str(app.time_seconds) \
              + "," + str(app.time_millis) + "," + str(app.created_at)

        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-app-usage.csv"
    try:
        response = make_response(csv_data)
        cd = 'attachment; filename=beehive-' + download_name
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response

    except Exception as e:
        return redirect(url_for('experiment_app_usage', code=code))


# Endpoint to display Screen events for an experiment
@app.route('/screen-events/experiment/<code>')
def experiment_screen_events(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'screen_events': TP_ScreenLog.query.filter_by(code=code).all(),
        'dashboard_page': True
    }
    return render_template('experiment/experiment-screen-events.html', **ctx)


# Endpoint to download protocols for an experiment
@app.route('/download/screen-events/experiment/<code>')
def experiment_screen_event_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    screen_event = TP_ScreenLog.query.filter_by(code=code).all()
    csv_data = "NO," + "WORKER ID," + "EVENT," + "TIME (millis)," + "DATE"

    count = 1
    for event in screen_event:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(event.worker_id) + "," + str(event.event) + "," \
              + str(event.time_millis) + "," + str(event.created_at)

        csv_data = csv_data + row
        count = count + 1

    download_name = code + "-screen-events.csv"
    try:
        response = make_response(csv_data)
        cd = 'attachment; filename=beehive-' + download_name
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response

    except Exception as e:
        return redirect(url_for('experiment_screen_events', code=code))


# Endpoint to download protocols for an experiment
@app.route('/download/all-data/experiment/<code>')
def experiment_all_data_download(code):
    if not user_is_owner_of_experiment(code):
        return render_template('403-forbidden.html'), 403

    file_name = "experiment-" + str(code) + "-data"
    zip_file_name = "temp/" + file_name + ".zip"
    data_files_path = TEMP_DIR + "/experiment-" + str(code) + "-data/"

    # clean directory
    try:
        dir_path = os.path.dirname(os.path.realpath(TEMP_DIR))
        absname = os.path.abspath(os.path.join(dir_path, "temp"))
        shutil.rmtree(absname)
    except OSError:
        pass

    # Generate temp dir
    if not os.path.exists(data_files_path):
        os.makedirs(data_files_path)

    ####################################################################################################################
    # Generate data files
    ####################################################################################################################
    # Generate participants file
    generate_participants_csv(code)

    # Generate RescueTime participants file
    generate_rescuetime_participants_csv(code)

    # Generate app-analytics participants file
    generate_app_analytics_csv(code)

    # Generate protocols file
    generate_protocols_csv(code)

    # Generate app-usage participants file
    generate_app_usage_csv(code)

    # Generate screen events participants file
    generate_screen_events_csv(code)

    ####################################################################################################################
    # compress data files
    ####################################################################################################################
    abs_path = os.path.abspath(TEMP_DIR)
    zipped = zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED)
    for dirname, subdirs, files in os.walk(data_files_path):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_path) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zipped.write(absname, arcname)

    zipped.close()

    # In Memory file compression (not used)
    # memory_file = BytesIO()
    # with zipfile.ZipFile(memory_file, 'w') as zf:
    #     for dirname, subdirs, files in os.walk(data_files_path):
    #         for filename in files:
    #             print "Zipping file: ", filename
    #             data = zipfile.ZipInfo(filename)
    #             data.date_time = time.localtime(time.time())[:6]
    #             absname = os.path.abspath(os.path.join(dirname, filename))
    #             arcname = absname[len(abs_path) + 1:]
    #             data.compress_type = zipfile.ZIP_DEFLATED
    #             zf.writestr(data, arcname)
    # memory_file.seek(0)
    # return send_file(memory_file, attachment_filename='capsule.zip', as_attachment=True)

    download_name = "experiment-" + str(code) + "-data.zip"

    try:
        dir_path = os.path.dirname(os.path.realpath(TEMP_DIR))
        absname = os.path.abspath(os.path.join(dir_path, zip_file_name))
        print  "dir_path:", absname
        return send_file(absname, attachment_filename=download_name, as_attachment=True)

    except Exception as e:
        return redirect(url_for('experiments'))


def generate_participants_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-participants.csv"
    participants = Participant.query.join(Enrollment, Participant.email == Enrollment.participant_id) \
        .add_columns(Participant.email, Participant.firstname, Participant.lastname, Participant.gender,
                     Participant.created_at) \
        .filter(Enrollment.exp_code == code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"
    count = 1
    for participant in participants:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(participant.email) + "," + str(participant.firstname) + "," + \
              str(participant.lastname) + "," + str(participant.gender) + "," + str(participant.created_at)
        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


def generate_rescuetime_participants_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-rescuetime-participants.csv"
    participants = RescuetimeUser.query.filter_by(code=code).all()
    csv_data = "NO," + "EMAIL," + "FIRSTNAME," + "LASTNAME," + "GENDER," + "ENROLLMENT DATE"

    if len(participants) <= 0:
        return

    count = 1
    for participant in participants:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(participant.email) + "," + str(participant.firstname) + "," + \
              str(participant.lastname) + "," + str(participant.gender) + "," + str(participant.created_at)
        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


def generate_app_analytics_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-app-analytics.csv"
    events = InAppAnalytics.query.filter_by(code=code).all()
    csv_data = "NO," + "EMAIL," + "EVENT TIME (millis)," + "EVENT DESCRIPTION," + "EVENT DATE"

    if len(events) <= 0:
        return

    count = 1
    for event in events:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(event.email) + "," + str(event.event_time_millis) + "," + \
              str(event.event_desc) + "," + str(event.created_at)
        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


def generate_protocols_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-protocols.csv"
    protocols = Protocol.query.filter_by(exp_code=code).all()
    csv_data = "NO," + "LABEL," + "START DATE," + "END DATE," + "FREQUENCY," + "METHOD," + "DETAILSKK," \
               + "APP ID," + "TYPE," + "TIME," + "HALF NOTIFY,"

    if len(protocols) <= 0:
        return

    count = 1
    for protocol in protocols:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(protocol.label) + "," + str(protocol.start_date) + "," + str(protocol.end_date) \
              + "," + str(protocol.frequency) + "," + str(protocol.method) + "," + str(protocol.notif_details.substr(0, 15)) + "...}" \
              + "," + str(protocol.notif_appid) + "," + str(protocol.notif_type) + "," + str(protocol.notif_time) \
              + "," + str(protocol.probable_half_notify)

        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


def generate_app_usage_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-app-usage.csv"
    app_usage = TP_FgAppLog.query.filter_by(code=code).all()
    csv_data = "NO," + "WORKER ID," + "APP ID," + "TIME (seconds)," + "TIME (millis)," + "DATE"

    if len(app_usage) <= 0:
        return

    count = 1
    for app in app_usage:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(app.worker_id) + "," + str(app.app_id) + "," + str(app.time_seconds) \
              + "," + str(app.time_millis) + "," + str(app.created_at)

        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


def generate_screen_events_csv(code):
    csv_file_path = TEMP_DIR + "/experiment-" + str(code) + "-data/" + code + "-screen-events.csv"
    screen_events = TP_ScreenLog.query.filter_by(code=code).all()
    csv_data = "NO," + "WORKER ID," + "EVENT," + "TIME (millis)," + "DATE"

    if len(screen_events) <= 0:
        return

    count = 1
    for event in screen_events:
        # Convert to CSV format
        csv_data = csv_data + "\n"
        row = str(count) + "," + str(event.worker_id) + "," + str(event.event) + "," \
              + str(event.time_millis) + "," + str(event.created_at)

        csv_data = csv_data + row
        count = count + 1
    file = open(csv_file_path, "w+");
    file.write(str(csv_data))
    file.close()


# Security: check permission before download
def user_is_owner_of_experiment(code):
    try:
        experiment_owner = Experiment.query.filter_by(owner=current_user.email, code=code).all()
        print "experiment_owner:", experiment_owner
        print "len(experiment_owner) = ", len(experiment_owner)

        if len(experiment_owner) <= 0:
            return False
        else:
            return True

    except Exception as e:
        print "user_is_owner_of_experiment: Security exception for - ", current_user.email
        return False
