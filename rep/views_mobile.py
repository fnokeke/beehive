from rep import app
from flask import request, Response

from rep.models import TP_DailyResetHour, TP_Enrolled, TP_Admin, TP_FBStats, TP_FgAppLog, TP_FacebookLog, TP_ScreenLog, \
    MobileUser, PAM, MobileSurvey
from rep.models import Participant
from rep.models import MobileNotifLogs

import json

from rep.models import Experiment, Protocol
from rep.models_beehive import NotifEvent, InAppAnalytics
from rep.utils import to_json


@app.route('/mobile/register', methods=['POST'])
def mobile_register_user():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response = MobileUser.register(data)
    return Response(status=status, response=json.dumps({'response': response}), mimetype='application/json')


@app.route('/mobile/fetchstudy', methods=["POST"])
def fetch_study():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    code = data.get('code')
    experiment = Experiment.query.filter_by(code=code).first()
    protocols = Protocol.query.filter_by(exp_code=code).all()  # FIXME: consistent using exp_code or code for models
    response = {
        'experiment': json.loads(str(experiment)) if experiment else None,
        'protocols': [to_json(p) for p in protocols] if protocols else [],
        'login_type': ['google_login'],
        'google_login_type': 'google_no_ohmage'
    }
    status = 200

    if not experiment:
        status = 400
        response = {"error": "Invalid experiment code"}

    return Response(response=json.dumps(response), status=status, mimetype='application/json')


@app.route('/mobile/add/notif', methods=['POST'])
def add_notif_events():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    data['email'] = data['email'].strip('#')  # temp fix because for some reason '#' is appended to username :/
    _, response, __ = NotifEvent.add_stats(data)
    return json.dumps({'response': response, 'email': data['email']})


@app.route('/mobile/add/analytics', methods=['POST'])
def add_app_analytics():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    data['email'] = data['email'].strip('#')  # temp fix because for some reason '#' is appended to username :/
    _, response, __ = InAppAnalytics.add_stats(data)
    return json.dumps({'response': response, 'email': data['email']})


@app.route('/mobile/turkprime/enroll', methods=['POST'])
def mobile_worker_id():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response, worker = TP_Enrolled.add_user(data)
    if status == -1:
        return json.dumps({'status': -1, 'response': response, 'worker_id': -1, 'survey_link': ''})

    TP_Admin.add_user(data)
    # user_response = response + '\nYour Study Code: {}'.format(worker.worker_code)
    # user_response = response + '\nYour HIT Code: {}\nClick to complete survey:'.format(worker.worker_code)

    # survey_link = 'http://bit.ly/surveyOne'
    # if data['study_code'] == 'tech':
    #     survey_link = 'http://bit.ly/surveyTech'

    server_response = {'status': 200,
                       'response': response,
                       'worker_id': worker.worker_id,
                       'survey_link': ''}
    return json.dumps(server_response)


@app.route('/mobile/turkprime/all/fb-stats')
def get_all_fb_stats():
    stats = TP_FBStats.query.all()
    return json.dumps({'stats': stats})


@app.route('/mobile/turkprime/fb-stats', methods=['POST'])
def mobile_worker_fb_stats():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, stats = TP_FBStats.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id'], 'summary': to_json(stats)}
    server_response = append_admin_fb_response(server_response)
    return json.dumps(server_response, default=str)


@app.route('/mobile/turkprime/facebook-logs', methods=['POST'])
def mobile_facebook_logs():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = TP_FacebookLog.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id']}
    server_response = append_admin_fb_response(server_response)
    return json.dumps(server_response, default=str)


@app.route('/mobile/turkprime/app-logs', methods=['POST'])
def mobile_fg_app_log():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = TP_FgAppLog.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id']}
    return json.dumps(server_response, default=str)


@app.route('/mobile/turkprime/screen-event-logs', methods=['POST'])
def mobile_screen_event_log():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = TP_ScreenLog.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id']}
    return json.dumps(server_response, default=str)


@app.route('/mobile/phone-notif-logs', methods=['POST'])
def mobile_phone_notif_log():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = MobileNotifLogs.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id']}
    return json.dumps(server_response, default=str)


def append_admin_fb_response(data):
    worker = TP_Admin.query.filter_by(worker_id=data['worker_id']).first()
    if worker:
        data['admin_experiment_group'] = rm_null(worker.admin_experiment_group)
        data['admin_fb_max_mins'] = rm_null(worker.admin_fb_max_mins)
        data['admin_fb_max_opens'] = rm_null(worker.admin_fb_max_opens)
        data['admin_treatment_start'] = rm_null(worker.admin_treatment_start)
        data['admin_followup_start'] = rm_null(worker.admin_followup_start)
        data['admin_logging_stop'] = rm_null(worker.admin_logging_stop)
        data['admin_daily_reset_hour'] = rm_null(TP_DailyResetHour.get_last_updated_hour())
        data['admin_static_ratio_100'] = 50
        data['admin_adaptive_ratio_100'] = 80
    return data


def rm_null(val):
    return "" if (val == "None" or not val) else val


@app.route('/mobile/pam-logs', methods=['POST'])
def mobile_pam_log():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = PAM.add_stats(data)
    return json.dumps({'response': response, 'email': data['email']})


@app.route('/mobile/survey-logs', methods=['POST'])
def mobile_survey_log():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, __ = MobileSurvey.add_stats(data)
    return json.dumps({'response': response, 'email': data['email']})
