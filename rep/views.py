"""
Handle all app views
"""

from flask import flash, redirect, url_for, session, render_template, request
from flask import abort, Response
from flask_login import login_user, logout_user, current_user, login_required
from oauth2client.client import OAuth2WebServerFlow

from apiclient import discovery

import json, httplib2, pytz, requests, csv
import naf_quotes
import secret_keys

from rep import app, login_manager
from rep.models import Experiment, Intervention, MobileUser, Mturk, MturkPrelimRecruit
from rep.models import Experiment_v2, Protocol, Researcher, Enrollment, Participant, NewParticipant, TechnionUser
from rep.models import MturkExclusive, NafEnroll, NafStats, ImageTextUpload
from rep.models import CalendarConfig, DailyReminderConfig, GeneralNotificationConfig, VibrationConfig
from rep.models import NotifClickedStats, RescuetimeConfig, ScreenUnlockConfig

from rep.models import TP_DailyResetHour, TP_Enrolled, TP_Admin, TP_FBStats, TP_FgAppLog, TP_FacebookLog, TP_ScreenLog

from rep.rescuetime import RescueOauth2, RescueTime
from rep.omh import OMHOauth
from rep.moves import Moves
from rep.upload import Upload

from rep import export

from gcal import Calendar, EventFactory
from rep.utils import requires_basic_auth
from rep.utils import to_json, to_datetime
from datetime import datetime
from db_init import db

##########################################################################################################
app.debug = True


@app.route('/googlebcabee7122e5544b.html')
def google_domain_verification():
    return render_template('googlebcabee7122e5544b.html')


@app.route('/focus')
def justdoit():
    return render_template('justdoit.html')


@app.route('/download')
def download():
    return render_template('download.html')

#################################
# template views
#################################

@app.route('/rx')
@app.route('/researcher')
def researcher_view():
    if not current_user.is_authenticated:
        return render_template('index-researcher.html')

    if 'code' in request.args:
        code = request.args.get('code')
        return redirect(url_for('auth_rt', code=code))

    if 'error' in request.args:
        error = request.args.get('error')
        return redirect(url_for('auth_rt', error=error))

    return redirect(url_for('experiments'))


@app.route('/experiments')
@login_required
def experiments():
    ctx = {'users': Researcher.query.all(),
           'mobile_users': MobileUser.query.all(),
           'mturk_users': Mturk.query.all(),
           'experiments': Experiment_v2.query.all(),
           'interventions': Intervention.query.all()}
    return render_template('researcher_experiments.html', **ctx)


@app.route('/home')
@login_required
def home():
    ctx = {'participant': NewParticipant.query.get(current_user.email)}
    return render_template('home.html', **ctx)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('technion_home'))


@app.route('/researcher_analysis/<key>/<study_begin>/<int_begin>/<int_end>/<study_end>')
@requires_basic_auth
def perform_research_analysis(key, study_begin, int_begin, int_end, study_end):
    results = {}
    users = Researcher.get_all_users()

    for user in users:
        store = results.get(user.email, {})
        token = user.moves_access_token

        stats = Moves.get_stats(token, begin=study_begin, end=int_begin)
        store['baseline'] = stats[key]  # stats = {calories: num, duration: num, steps: num}

        stats = Moves.get_stats(token, begin=int_begin, end=int_end)
        store['intervention'] = stats[key]

        stats = Moves.get_stats(token, begin=int_end, end=study_end)
        store['follow_up'] = stats[key]

        results[user.email] = store

    return json.dumps(results)


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@login_manager.user_loader
def user_loader(user_id):
    return NewParticipant.get_user(user_id) or Researcher.get_user(user_id)

#################################
# Handle Errors
#################################

#
# @app.errorhandler(500)
# def internal_server_error(e):
#     app.logger.error('Server Error: %s', (e))
#     return SLMError.internal_server_error


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def get_next_condition(total_enrolled, ps_per_condition):
    return 1 + (total_enrolled % ps_per_condition)


#//////////////////////////////////////
# Beehive mobile user study connection
#//////////////////////////////////////
@app.route('/mobile/connect/study', methods=['POST'])
def connect_study():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    code = data['code']
    experiment = Experiment.query.filter_by(code=code).first()
    if not experiment:
        return json.dumps({'response': jsonify_responses('', ''), 'user': {}, 'experiment': {}})

    # already in experiment so no need to change anything
    user_in_experiment = MobileUser.query.filter_by(email=data['email'], code=code).first()
    if user_in_experiment:
        return json.dumps({'response': jsonify_responses('Welcome back!', ''),
                           'user': to_json(user_in_experiment),
                           'experiment': to_json(experiment)})

    # at this point user needs to be enrolled either as switching experiment or new user
    total_enrolled = len(MobileUser.query.filter_by(code=code).all())
    data['condition'] = get_next_condition(total_enrolled, experiment.ps_per_condition)

    # user in one experiment and moving to another
    existing_user = MobileUser.query.filter_by(email=data['email']).first()
    if existing_user:
        _, response, user = existing_user.update_experiment_info(code, data['condition'])
        return json.dumps({'response': response, 'user': to_json(user), 'experiment': to_json(experiment)})

    # enrolling as first timer in an experiment
    _, user_response, new_user = MobileUser.add_user(data)
    _, cal_response, __ = CalendarConfig.add(data)
    response = jsonify_responses(user_response, cal_response)
    return json.dumps({'response': response, 'user': to_json(new_user), 'experiment': to_json(experiment)})


def jsonify_responses(user_response, cal_response):
    return {'user_response': user_response, 'cal_response': cal_response}


@app.route('/mobile/add/calendar-config', methods=['POST'])
def add_calendar_setting():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, setting = CalendarConfig.add(data)
    return json.dumps({'response': response, 'cal_setting': to_json(setting)})


@app.route('/mobile/add/daily-reminder-config', methods=['POST'])
def add_daily_reminder():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, reminder = DailyReminderConfig.add(data)
    return json.dumps({'response': response, 'reminder': to_json(reminder)})


@app.route('/mobile/add/general-notification-config', methods=['POST'])
def add_notif_setting():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, setting = GeneralNotificationConfig.add(data)
    return json.dumps({'response': response, 'general_notif_setting': to_json(setting)})


@app.route('/mobile/add/rescuetime-config', methods=['POST'])
def add_rescuetime_config():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, rt_config = RescuetimeConfig.add(data)
    return json.dumps({'response': response, 'rescuetime_config': to_json(rt_config)})


@app.route('/mobile/add/screen-unlock-config', methods=['POST'])
def add_screen_unlock_config():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, unlock_config = ScreenUnlockConfig.add(data)
    return json.dumps({'response': response, 'screen_unlock_config': to_json(unlock_config)})


@app.route('/mobile/add/vibration-config', methods=['POST'])
def add_vibration_config():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, vibr_config = VibrationConfig.add(data)
    return json.dumps({'response': response, 'vibration_config': to_json(vibr_config)})


def millis_to_dt(time_milli):
    time_milli = int(time_milli)
    return datetime.utcfromtimestamp(time_milli // 1000).replace(microsecond=time_milli % 1000 * 1000)


@app.route('/mobile/add/notif-clicked-stats', methods=['POST'])
def add_notif_clicked_stats():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    data['time_appeared'] = millis_to_dt(data['time_appeared'])
    data['time_clicked'] = millis_to_dt(data['time_clicked'])

    _, response, notif_stats = NotifClickedStats.add_stats(data)
    return json.dumps({'response': response, 'notif_stats': to_json(notif_stats)})


#////////////////////////////////////////////
# mobile Beehive rescuetime && interventions
#////////////////////////////////////////////
@app.route("/rescuetime/summary", methods=['POST'])
def fetch_rt_summary():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    rt_user = Participant.query.filter_by(email=data['email']).first()
    if not rt_user: return {}
    return RescueTime.fetch_summary(rt_user.rescuetime_access_token, data['date'])


@app.route("/rescuetime/realtime", methods=['POST'])
def fetch_rt_realtime_activity():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    rt_user = Participant.query.filter_by(email=data['email']).first()
    if not rt_user: return {}
    return RescueTime.fetch_activity(rt_user.rescuetime_access_token, data['date'])


@app.route("/mobile/check/rescuetime", methods=['POST'])
def check_rt_conn():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    user = Participant.query.filter_by(email=data['email']).first()

    response = False
    if user:
        if user.rescuetime_access_token:
            response = True

    result = {'rt_response': response, 'rt_email': data['email']}
    return json.dumps(result)


@app.route("/mobile/check/calendar", methods=['POST'])
def check_cal_conn():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    user = Participant.query.filter_by(email=data['email']).first()

    response = False
    if user:
        if user.google_credentials:
            response = True

    result = {'cal_response': response, 'cal_email': data['email']}
    return json.dumps(result)


@app.route("/mobile/calendar/events", methods=['POST'])
def get_all_events():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    email, date = data['email'], data['date']
    user = Participant.query.filter_by(email=email).first()
    events = -1
    if user and date:
        events = Calendar(email, email, user.google_credentials).get_all_events(date)
        events = minimize_events(events)
    return json.dumps({'events': events})


def minimize_events(events):
    minimal_events = []
    for ev in events:
        minimal_events.append({'summary': ev['summary'], 'start': ev['start'], 'end': ev['end']})
    return minimal_events


@app.route('/mobile/interventions', methods=['POST'])
def fetch_interventions():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    interventions = Intervention.query.filter_by(code=data['code']).order_by('start').all()
    intv_response = [str(x) for x in interventions]
    return json.dumps({"intv_response": intv_response})


#////////////////////////////////////
# Researcher modify experiments
#////////////////////////////////////
# Endpoint to add new experiment to the database
@app.route('/add/experiment', methods=['POST'])
def add_experiment():
    experiment = {
        'title': request.form.get('title'),
        'start': request.form.get('start'),
        'end': request.form.get('end'),
        'rescuetime': request.form.get('rescuetime', False),
        'calendar': request.form.get('calendar', False),
        'geofence': request.form.get('geofence', False),
        'text': request.form.get('text', False),
        'image': request.form.get('image', False),
        'reminder': request.form.get('reminder', False),
        'actuators': request.form.get('actuators', False)
    }
    _, response, __ = Experiment.add_experiment(experiment)
    return response


# Endpoint to add new experiment to the database v2
@app.route('/add/experiment/v2', methods=['POST'])
def add_experiment_v2():
    experiment = {
        'label': request.form.get('label'),
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date', False),
        'screen_events': request.form.get('screen_events', False),
        'app_usage': request.form.get('app_usage', False),
    }

    protocols = request.form.get('protocols')
    print "Adding experiment to database.."
    #_, response, __ = Experiment_v2.add_experiment(experiment, protocols)
    status, response, _ = Experiment_v2.add_experiment(experiment, protocols)
    if (status == 200):
        return response
    else:
        return Response(response, status=status, mimetype='application/json')


# New experiment create view
@app.route('/experiments/create')
def create_experiment():
    return render_template('create-experiment.html')



@app.route('/experiment/<code>')
def experiment_options(code):
    # Fetch experiment details and pass to template
    ctx = {
        'exp-code': code
    }
    return render_template('experiment-options.html', **ctx)


@app.route('/edit-experiment/<code>')
def edit_experiment(code):
    experiment = Experiment.query.filter_by(code=code).first()
    intv_type = get_intv_type(experiment)
    interventions = Intervention.query.filter_by(code=code, intv_type=intv_type).order_by('start').all()
    next_start_date = datetime.now().strftime("%Y-%m-%d")
    if interventions:
        next_start_date = to_datetime(interventions[-1].end).strftime("%Y-%m-%d")

    ctx = {
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment_start': experiment.start.strftime("%Y-%m-%d"),
        'experiment_end': experiment.end.strftime("%Y-%m-%d"),
        'next_start_date': next_start_date,
        'enrolled_users': MobileUser.query.filter_by(code=code).all(),
        'users_unfiltered': Researcher.query.all(),
        'experiment': experiment,
        'image_texts': ImageTextUpload.query.filter_by(code=code).all(),
        'uploaded_intvs': ImageTextUpload.query.filter_by(code=code).all(),
        'general_notifs': GeneralNotificationConfig.query.filter_by(code=code).all(),
        'gg': GeneralNotificationConfig,
        'interventions': interventions
    }
    return render_template('edit-experiment.html', **ctx)


@app.route('/old_edit-experiment/<code>')
def old_edit_experiment(code):
    experiment = Experiment.query.filter_by(code=code).first()
    intv_type = get_intv_type(experiment)
    interventions = Intervention.query.filter_by(code=code, intv_type=intv_type).order_by('start').all()
    next_start_date = datetime.now().strftime("%Y-%m-%d")
    if interventions:
        next_start_date = to_datetime(interventions[-1].end).strftime("%Y-%m-%d")

    ctx = {
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment_start': experiment.start.strftime("%Y-%m-%d"),
        'experiment_end': experiment.end.strftime("%Y-%m-%d"),
        'next_start_date': next_start_date,
        'enrolled_users': MobileUser.query.filter_by(code=code).all(),
        'users_unfiltered': Researcher.query.all(),
        'experiment': experiment,
        'image_texts': ImageTextUpload.query.filter_by(code=code).all(),
        'uploaded_intvs': ImageTextUpload.query.filter_by(code=code).all(),
        'general_notifs': GeneralNotificationConfig.query.filter_by(code=code).all(),
        'gg': GeneralNotificationConfig,
        'interventions': interventions
    }
    return render_template('old-edit-experiment.html', **ctx)


@app.route('/notif-clicked-dashboard/<code>')
def notif_clicked_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    ctx = {'notif_stats': NotifClickedStats.query.filter_by(code=code).all(), 'experiment': experiment}
    return render_template('/dashboards/notif-clicked-dashboard.html', **ctx)


@app.route('/participants-dashboard/<code>')
def participant_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    intv_type = get_intv_type(experiment)
    ctx = {
        'enrolled_users': MobileUser.query.filter_by(code=code).all(),
        'experiment': experiment,
        'interventions': Intervention.query.filter_by(
            code=code, intv_type=intv_type).order_by('start').all()
    }
    return render_template('/dashboards/participants-dashboard.html', **ctx)


@app.route('/rescuetime-dashboard/<code>')
def rescuetime_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    ctx = {'experiment': experiment, 'users_unfiltered': Participant.query.all()}
    return render_template('/dashboards/rescuetime-dashboard.html', **ctx)


@app.route('/stats-dashboard/<code>')
def stats_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    ctx = {'experiment': experiment}
    return render_template('/dashboards/stats-dashboard.html', **ctx)


@app.route('/mturk-participants-dashboard/<code>')
def mturk_participant_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    ctx = {'mturk_users': TP_Enrolled.query.all(), 'experiment': experiment}
    return render_template('/dashboards/mturk-participants-dashboard.html', **ctx)


@app.route('/mturk-stats-dashboard/<code>')
def mturk_stats_dashboard(code):
    experiment = Experiment.query.filter_by(code=code).first()
    ctx = {'mturk_stats': TP_FBStats.query.order_by('created_at desc').limit(2000).all(), 'experiment': experiment}
    return render_template('/dashboards/mturk-stats-dashboard.html', **ctx)


def get_intv_type(experiment):
    intv_type = ''
    if experiment.calendar:
        intv_type = 'calendar'
    elif experiment.rescuetime:
        intv_type = 'rescuetime'
    elif experiment.actuators:
        intv_type = 'actuators'
    elif experiment.image and experiment.text:
        intv_type = 'text_image'
    return intv_type


@app.route('/delete/experiment/<code>')
def delete_experiment(code):
    Experiment.delete_experiment(code)
    flash('Returning to experiment page.', 'success')
    return redirect(url_for('researcher_login'))


@app.route('/update/experiment', methods=['POST'])
def update_experiment():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    data['start'] = '{} 05:00:00 -0500'.format(data['start'])
    data['end'] = '{} 05:00:00 -0500'.format(data['end'])
    data['start'] = datetime.strptime(data['start'], '%Y-%m-%d %H:%M:%S -0500')
    data['end'] = datetime.strptime(data['end'], '%Y-%m-%d %H:%M:%S -0500')
    updated_exp = Experiment.update_experiment(data)
    return str(updated_exp)


@app.route('/update/group', methods=['POST'])
def update_group():
    update = {
        'code': request.form.get('code'),
        'no_of_condition': request.form.get('no_of_condition'),
        'ps_per_condition': request.form.get('ps_per_condition')
    }
    updated_exp = Experiment.update_group(update)
    return str(updated_exp)


@app.route('/fetch/experiments', methods=['GET'])
def fetch_experiments():
    results = []

    for exp in Experiment.query.all():
        exp_json = json.loads(str(exp))
        results.append(exp_json)

    return json.dumps(results)


@app.route('/fetch/experiment/<code>')
def fetch_experiment_by_code(code):
    experiment = Experiment.query.filter_by(code=code).first()
    return str(experiment)

##########################################################################################################
# Participant registration and enrollment APIs
##########################################################################################################
# Register a participant and enroll in an experiment
# -------- NOT USED -------- #
@app.route('/participant/register', methods=['POST'])
def participant_enroll():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    # Check request validity
    if not 'email' in data:
        response_message = {'error': 'email is required'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    # Check request referrer
    if not 'application' in data:
        response_message = {'error': 'application is required'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    if data['application'] != 'swift' and data['application'] != 'objc':
        response_message = {'error': 'application must be swift or objc'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    # Check if participant already registered
    if NewParticipant.query.filter_by(email=data['email']).first() == None:
        # Register new participant
        # TO DO : Perform ooAuth redirection Add missing data
        new_participant = {}
        new_participant['email'] = data['email']
        new_participant['google_oauth'] = 'TO DO'
        new_participant['oauth_token'] = 'TO DO'
        status, response, _ = NewParticipant.register(new_participant)
        return Response(response=json.dumps(response), status=status, mimetype='application/json')
    else:
        # get participant ID
        participant = NewParticipant.query.filter_by(email=data['email']).first()
        response_message = {'message': 'Participant already registered'}
        http_status = 200
        return redirect('https://www.google.com')
        #return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')
        #return redirect(url_for('experiments'))


# Register a participant in an experiment
@app.route('/google_login_participant')
def google_login_participant():
    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_PARTICIPANT'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'google_login_participant', _external=True))

    auth_code = request.args.get('code')
    if not auth_code:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    credentials = flow.step2_exchange(auth_code, http=httplib2.Http())
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('oauth2', 'v2', http=http)

    profile = service.userinfo().get().execute()

    user = Participant.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())
    login_user(user)
    return redirect(url_for('home'))

    # login_user(user)
    # email = str(profile['email'])
    # redirect_url = 'http://smalldata.io/?email=' + email
    # # TODO: Redirect user back to app
    # return redirect(redirect_url)


# Enroll a participant in an experiment
@app.route('/enroll', methods=['POST'])
def participant_register():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    # Checkc request validity
    if not 'email' in data:
        response_message = {'error': 'email is required'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    if not 'code' in data:
        response_message = {'error': 'code is required'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    # Check if experiment code is valid
    if Experiment_v2.query.filter_by(code=data['code']).first() == None:
        response_message = {'error': 'Invalid experiment code'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')

    # Add missing data
    data['google_oauth'] = 'None'
    data['oauth_token'] = 'None'

    # Check if participant is already registered
    if Participant.query.filter_by(email=data['email']).first() == None:
        print 'User does not exist.'
        response_message = {'error': 'User does not exist!'}
        http_status = 400
        return Response(response=json.dumps(response_message), status=http_status, mimetype='application/json')
    else:
        print 'User FOUND!'
        # get participant ID
        participant = Participant.query.filter_by(email=data['email']).first()
        print participant.email

    # Append participant ID
    data['participant_id'] = participant.email

    # Enroll the participant in experiment
    new_enrollment = {}
    new_enrollment['participant_id'] = participant.email
    new_enrollment['exp_code'] = str(data['code'])

    status, response, _ = Enrollment.enroll(new_enrollment)
    return Response(response=json.dumps(response), status=status, mimetype='application/json')


##########################################################################################################
# Experiments V2 APIs
##########################################################################################################
# Fetch experiments from v2 table
@app.route('/fetch/experiments/v2', methods=['GET'])
def fetch_experiments_v2():
    results = []

    for exp in Experiment_v2.query.all():
        exp_json = json.loads(str(exp))
        results.append(exp_json)

    return json.dumps(results)


@app.route('/fetch/experiment/v2/<code>')
def fetch_experiment_by_code_v2(code):

    experiment = Experiment_v2.query.filter_by(code=code).first()
    print 'Experiment: ', str(experiment)
    protocols = Protocol.query.filter_by(exp_code=code).all()
    print 'protocol count ', Protocol.query.filter_by(exp_code=code).count()
    print 'protocols: ', str(protocols)
    print
    experiment = json.loads(str(experiment))
    experiment['protocols'] = json.loads(str(protocols))
    experiment = json.dumps(experiment)
    return str(experiment)


#////////////////////////////////////
# Researcher modify interventions
#////////////////////////////////////
@app.route('/add/intervention', methods=['POST'])
def add_intervention():
    # data['start'] = datetime.strptime(data['start'], '%Y-%m-%dT%H:%M:%S.000Z')
    # data['end'] = datetime.strptime(data['end'], '%Y-%m-%dT%H:%M:%S.000Z')
    data = json.loads(request.data) if request.data else request.form.to_dict()
    data['start'] = millis_to_dt(data['start'])
    data['end'] = millis_to_dt(data['end'])
    _, response, added_intv = Intervention.add_intervention(data)
    return str(added_intv)


@app.route('/delete/intervention', methods=['POST'])
def delete_intervention():
    created_at = request.form.get('created_at')
    Intervention.delete_intervention(created_at)
    return 'intervention deleted.'


@app.route('/upload/intervention', methods=['POST'])
def upload_intv():
    text = request.form.get('text')
    image_name = request.form.get('image_name')
    code = request.form.get('code')
    image = request.files.get('image')

    image_url = None
    if image_name and image:
        Upload.save(image_name, image)
        image_url = Upload.get_url(image_name)

    new_intv = {'text': text, 'image_name': image_name, 'image_url': image_url, 'code': code}
    ImageTextUpload.add(new_intv)

    msg = ''
    if image and image_name and text:
        msg = 'image with text added.'
    elif image and image_name:
        msg = 'only image added.'
    elif text:
        msg = 'only text added.'

    return msg


@app.route('/fetch/uploaded/features/<code>', methods=['GET'])
def fetch_uploaded_intv(code):
    data = {
        'image_text_uploads': to_json(ImageTextUpload.query.filter_by(code=code).order_by('created_at').all()),
        'last_calendar_config': to_json(CalendarConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        'last_daily_reminder_config':
        to_json(DailyReminderConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        'last_rescuetime_config':
        to_json(RescuetimeConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        'last_general_notification_config':
        to_json(GeneralNotificationConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        'last_screen_unlock_config':
        to_json(ScreenUnlockConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        'last_vibration_config':
        to_json(VibrationConfig.query.filter_by(code=code).order_by('created_at desc').first()),
        #
    }
    return json.dumps(data)

# /////////////////////////////////////
# Connect Service Providers
# /////////////////////////////////////

# @app.route('/google_login_participant')
# def google_login_participant():
#     flow = OAuth2WebServerFlow(
#         client_id=app.config['GOOGLE_CLIENT_ID'],
#         client_secret=app.config['GOOGLE_CLIENT_SECRET'],
#         scope=app.config['GOOGLE_SCOPE_PARTICIPANT'],
#         access_type='offline',
#         prompt='consent',
#         redirect_uri=url_for(
#             'google_login_participant', _external=True))
#
#     auth_code = request.args.get('code')
#     if not auth_code:
#         auth_uri = flow.step1_get_authorize_url()
#         return redirect(auth_uri)
#
#     credentials = flow.step2_exchange(auth_code, http=httplib2.Http())
#     if credentials.access_token_expired:
#         credentials.refresh(httplib2.Http())
#
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('oauth2', 'v2', http=http)
#
#     profile = service.userinfo().get().execute()
#     user = NewParticipant.from_profile(profile)
#     user.update_field('google_credentials', credentials.to_json())
#
#     login_user(user)
#     return redirect(url_for('home'))

# Connect to Ohmage
@app.route("/auth-omh")
@login_required
def auth_omh():
    return redirect(OMHOauth.AUTH_CODE_URL)


#TODO: update this callback so it shows omh not pam
@app.route("/ohmage")
@app.route("/oauth2callback-pam")
def omh_oauth2callback():

    code = request.args.get('code')

    if not code:
        flash('sorry, could not connect PAM', 'danger')
    else:
        omh_oauth = OMHOauth()
        access_token, refresh_token, response = omh_oauth.get_tokens(code)
        #user = NewParticipant.get_user(current_user.email)
        user = Participant.get_user(current_user.email)
        user.update_field('omh_access_token', access_token)
        user.update_field('omh_refresh_token', refresh_token)

        if not (access_token and refresh_token):
            flash('Sorry, connection failed. contact admin: {}'.format(response), 'danger')
        else:
            flash('Successfully connected to Ohmage!', 'success')

    #return redirect(url_for('home'))
    print "User: ", current_user
    # TODO: Redirect user back to app
    if current_user.is_authenticated():
        redirect_url = 'http://smalldata.io/?email=' + str(current_user)
    else:
        redirect_url = 'http://smalldata.io/'
    return redirect(redirect_url)



# Google login for researchers
@app.route('/google_login_researcher')
def google_login_researcher():
    if current_user.is_authenticated:
        return redirect(url_for('experiments'))

    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_RESEARCHER'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'google_login_researcher', _external=True))

    auth_code = request.args.get('code')
    if not auth_code:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    credentials = flow.step2_exchange(auth_code, http=httplib2.Http())
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('oauth2', 'v2', http=http)

    profile = service.userinfo().get().execute()
    user = Researcher.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())

    login_user(user)
    return redirect(url_for('experiments'))


# Moves
@app.route("/auth-moves")
@login_required
def auth_moves():
    c = '&client_id=' + app.config['MOVES_CLIENT_ID']
    e = '&client_secret=' + app.config['MOVES_CLIENT_SECRET']
    r = '&redirect_uri=' + app.config['MOVES_REDIRECT_URI']
    s = '&scope=' + app.config['MOVES_SCOPE']

    code = request.args.get('code')
    if not code:  # redirect to page for user to type code into their moves app
        url = app.config['MOVES_WEB_URL'] + c + s
        return redirect(url)

    url = app.config['MOVES_ACCESS_TOKEN_URL'] + code + c + e + r
    r = requests.post(url)
    if r.status_code != 200:
        msg = 'Moves Connection Error(%s): %s' % (r.status_code, r.reason)
        flash(msg, 'danger')
        return redirect(url_for('auth_moves'))

    results = json.loads(r.text)
    if 'Already Exists' == current_user.update_moves_id(str(results['user_id'])):
        msg = 'Error: cannot continue because your Moves device has already been connected with another SLM account.'
        flash(msg, 'danger')
        return redirect(url_for('home'))

    current_user.update_field('moves_access_token', results['access_token'])
    current_user.update_field('moves_refresh_token', results['refresh_token'])
    flash('Successfully connected Moves.', 'success')
    return redirect(url_for('home'))


#######################################################
# fetch different datastreams: Moves, PAM, RescueTime
#######################################################
@app.route("/data-moves/<date>")
@login_required
def get_moves_data(date):
    if not current_user.moves_access_token:
        flash('Sorry, you have not authenticated moves', 'danger')

    calname = app.config['LOCATION']
    resp = export.to_cal(calname, current_user.moves_access_token, date)
    return resp


@app.route("/data-pam/<date>")
@login_required
def get_pam_data(date):
    if not current_user.moves_access_token:
        flash('Sorry, you have not authenticated Ohmage', 'danger')

    calname = app.config['MOOD']
    resp = export.to_cal(calname, current_user.pam_access_token, date)
    return resp


@app.route("/data-rt/<date>")
@login_required
def get_rt_data(date):
    if not current_user.rescuetime_access_token:
        flash('Sorry, you have not authenticated RescueTime', 'danger')

    calname = app.config['SN']
    resp = export.to_cal(calname, current_user.rescuetime_access_token, date)
    return resp


########################
# Configure Settings
########################
@app.route('/settings/tracking/<field>/<state>')
@login_required
def tracking_settings(field, state):
    is_activated = True if state == 'true' else False
    if is_activated == 'invalid':
        return -1

    if field == 'location':
        current_user.update_field('is_location_active', is_activated)
        return 'Moves successfully activated!' if is_activated else 'deactivated.'
    elif field == 'mood':
        current_user.update_field('is_mood_active', is_activated)
        return 'PAM successfully activated!' if is_activated else 'deactivated.'
    elif field == 'sn':
        current_user.update_field('is_sn_active', is_activated)
        return 'RescueTime successfully activated!' if is_activated else 'deactivated.'


@app.route("/settings/profile/update", methods=['POST'])
@login_required
def update_profile():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    gender = request.form.get('gender')

    if firstname != '':
        current_user.update_field('firstname', firstname)
    if lastname != '':
        current_user.update_field('lastname', lastname)
    if gender != '':
        current_user.update_field('gender', gender)

    return 'update profile request: %s' % request.form


@app.route('/settings/execute/<calname>/<cmd>')
@login_required
def execute_calendar_command(calname, cmd):
    print '{} {}'.format(cmd, calname)

    if calname == 'Location':
        cname = app.config['LOCATION']
    elif calname == 'Mood':
        cname = app.config['MOOD']
    elif calname == 'SocialNetworks':
        cname = app.config['SN']
    else:
        cname = calname

    cal = Calendar(cname)
    response = None

    if cmd == 'DeleteCalendar':
        cal.delete_calendar()
    elif cmd == 'ResetCalendar':
        cal.reset_calendar()
    elif cmd == 'InsertTestEvent':
        response = cal.insert_event(EventFactory.generate_random_event())

    return response or 'Successfully completed!'

#################################
# MTURK
#################################


@app.route('/mturkregister')
@requires_basic_auth
def registermturk():
    return render_template('mturk/register-mturk.html')


@app.route('/mturk')
def welcome_and_check():
    return render_template('mturk/checkmturk.html')

#///////////////// Nicki - Aditya - Fabian ///////////////////
#/////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////


@app.route('/naf')
def naf_join():
    return render_template('naf/naf-hindi-test.html')


@app.route('/nafa')
def nafa():
    return render_template('naf/a.html')


@app.route('/nafb')
def nafb():
    return render_template('naf/b.html')


@app.route('/nafc')
def nafc():
    return render_template('naf/c.html')


@app.route('/nafd')
def nafd():
    return render_template('naf/d.html')


@app.route('/nafe')
def nafe():
    return render_template('naf/e.html')


@app.route('/naff')
def naff():
    return render_template('naf/f.html')


@app.route('/naf/<worker_id>')
def naf_watch_videos(worker_id):
    enrolled_worker = NafEnroll.query.filter_by(worker_id=worker_id).first()
    if not enrolled_worker:
        return render_template('mturk/mturk-404.html')
    session['step'] = 1
    ctx = {'worker': enrolled_worker, 'quotes': naf_quotes.get(enrolled_worker.group)}
    return render_template('naf/naf-main.html', **ctx)


@app.route('/naf/update/step', methods=['POST'])
def naf_update_step():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    cur_step = int(data['current_step'])
    if cur_step == 5:
        return json.dumps({'next_step': cur_step})

    next_step = 1 + cur_step % 5
    session['step'] = next_step
    return json.dumps({'next_step': next_step})


@app.route('/naf/submit', methods=['POST'])
def naf_submit():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response, _ = NafStats.submit_worker_info(data)
    return json.dumps({'status': status, 'response': response})


@app.route('/naf/dashboard')
@requires_basic_auth
def naf_dashboard():
    ctx = {'naf_stats': NafStats.query.all(), 'naf_users': NafEnroll.query.all()}
    return render_template('naf/naf_dashboard.html', **ctx)


@app.route('/naf/enroll/worker_id', methods=['POST'])
def naf_verify_worker_id():
    data = json.loads(request.data) if request.data else request.form.to_dict()

    total_enrolled = len(NafEnroll.query.all())
    data['group'] = naf_get_next_condition(total_enrolled)

    worker_id = data['worker_id']
    enrolled_worker = NafEnroll.query.filter_by(worker_id=worker_id).first()
    if not enrolled_worker:
        status, response, worker = NafEnroll.add_worker(data)
        enrolled_worker = NafEnroll.query.filter_by(worker_id=worker_id).first()

    link = "<a href='/naf/{}'>continue here</a>.".format(worker_id)
    return 'Welcome {}, {}'.format(worker_id, link)


def naf_get_next_condition(total_enrolled):
    no_of_groups = 3
    return 1 + (total_enrolled % no_of_groups)


@app.route('/naf/register/csv', methods=['POST'])
def naf_register_mturk_workers():
    csv_file = request.files.get('mturk.csv')
    count = 0
    duplicates = ""
    for row in csv.reader(csv_file):
        worker_info = get_worker_info(row)
        status, _, worker = MturkExclusive.add(worker_info)
        if status == 200:
            count += 1
        else:
            duplicates += worker.worker_id + "; "

    duplicates = "None" if duplicates == "" else duplicates
    response = -1
    if csv_file:
        response = 'Successfully registered {} new user(s).<br><br>Duplicates:<br>{}'.format(count, duplicates)

    return response
#/////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////


@app.route('/mturkdownload')
def mturk_download():
    return render_template('mturk/mturk-download.html')


@app.route('/tp')
def plain_mturk():
    return render_template('mturk/enroll.html')


@app.route('/tech')
def enroll_technion():
    return render_template('mturk/tech.html')


@app.route('/mturk/<worker_id>')
def amturk(worker_id):
    enrolled_worker = MturkExclusive.query.filter_by(worker_id=worker_id).first()
    if not enrolled_worker:
        return render_template('mturk/mturk-404.html')
    return render_template('mturk/enroll.html', worker=enrolled_worker)


@app.route('/mturk/verify/worker_id', methods=['POST'])
def worker_id():
    worker_id = request.form['worker_id']
    enrolled_worker = MturkExclusive.query.filter_by(worker_id=worker_id).first()
    current_datetime = datetime.now().strftime("%I:%M:%S %p on %B %d %Y")
    if not enrolled_worker:
        log_submission(current_datetime, worker_id, 'rejected')
        return 'Worker ({}) cannot partake in experiment. You have to be registered by researcher.'.format(worker_id)

    log_submission(current_datetime, worker_id, 'accepted')
    link = "<a href='/mturk/{}'>continue here</a>.".format(worker_id)
    return 'Welcome {}, {}'.format(worker_id, link)


def log_submission(time_of_click, worker_id, category):
    log_file = 'accepted.csv' if category == 'accepted' else 'rejected.csv'
    with open(log_file, 'a') as myfile:
        row = '{},{}\n'.format(time_of_click, worker_id)
        myfile.write(row)


@app.route("/mturk-auth-moves")
def mturk_auth_moves():
    c = '&client_id=' + app.config['MTURK_MOVES_CLIENT_ID']
    e = '&client_secret=' + app.config['MTURK_MOVES_CLIENT_SECRET']
    r = '&redirect_uri=' + app.config['MTURK_MOVES_REDIRECT_URI']
    s = '&scope=' + app.config['MOVES_SCOPE']

    code = request.args.get('code')
    if not code:
        url = app.config['MOVES_WEB_URL'] + c + s
        return redirect(url)

    url = app.config['MOVES_ACCESS_TOKEN_URL'] + code + c + e + r
    r = requests.post(url)
    if r.status_code != 200:
        msg = 'Moves Connection Error(%s): %s' % (r.status_code, r.reason)
        flash(msg, 'danger')
        return redirect(url_for('mturk_auth_moves'))

    results = json.loads(r.text)
    info = {
        'worker_id': session['worker_id'],
        'moves_id': str(results['user_id']),
        'access_token': results['access_token'],
        'refresh_token': results['refresh_token'],
        'ip': request.access_route[-1]
    }
    valid, msg, gen_code = Mturk.add_user(info)

    if valid == 200:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('mturk', gen_code=gen_code))


@app.route('/firebase/sync', methods=['POST'])
def firebase_sync():
    form = json.loads(request.data) if request.data else request.form.to_dict()
    data = {'to': form['firebase_sync_token'], 'data': {'type': 'serverSync'}}
    data = json.dumps(data)
    headers = {'Authorization': secret_keys.FIREBASE_KEY, 'content-type': 'application/json'}
    url = 'https://fcm.googleapis.com/fcm/send'
    r = requests.post(url, headers=headers, data=data)
    return json.dumps(r.json())


@app.route('/mobile/turkprime/enroll', methods=['POST'])
def mobile_worker_id():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response, worker = TP_Enrolled.add_user(data)
    if status == -1:
        return json.dumps({'status': -1, 'response': response, 'worker_id': -1, 'survey_link': ''})

    VALID_CODES = ["mturk", "tech", "hci", "uncdf"]
    if not data['study_code'] in VALID_CODES:
        return json.dumps({'status': -1,
                           'response': "Invalid study code. Check it and try again.",
                           'worker_id': -1,
                           'survey_link': ''})

    TP_Admin.add_user(data)
    user_response = response + '\nYour HIT Code: {}\nClick to complete survey:'.format(worker.worker_code)

    survey_link = 'http://bit.ly/surveyOne'
    if data['study_code'] == 'tech':
        survey_link = 'http://bit.ly/surveyTech'

    server_response = {'status': 200,
                       'response': user_response,
                       'worker_id': worker.worker_id,
                       'survey_link': survey_link}
    return json.dumps(server_response)


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


@app.route('/server-fb-stats', methods=['POST'])
def server_data():
    args = json.loads(request.form.get('params'))

    mturk_stats = TP_FBStats.query.order_by('created_at desc').all()
    total = len(mturk_stats)
    filtered_length = total

    search = args['search']['value']
    if search:
        search = '%{}%'.format(search)
        mturk_stats = TP_FBStats.query.filter(TP_FBStats.worker_id.ilike(search)).order_by('created_at desc').all()
        filtered_length = len(mturk_stats)

    data = []
    for x in mturk_stats:
        entry = get_ordered_entry(x)
        data.append(entry.values())

    start = args['start']
    length = args['length']
    data = data[start:start + length]
    draw = args['draw']

    return json.dumps({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered_length,
        "data": data
        #
    })


from collections import OrderedDict


def get_ordered_entry(db_stats_entry):
    entry = json.loads(str(db_stats_entry))
    ordered = OrderedDict()

    ordered['local_time'] = entry['local_time']
    ordered['worker_id'] = entry['worker_id']
    ordered['current_experiment_group'] = entry['current_experiment_group']
    ordered['total_seconds'] = entry['total_seconds']
    ordered['total_opens'] = entry['total_opens']
    ordered['time_spent'] = entry['time_spent']
    ordered['time_open'] = entry['time_open']
    ordered['ringer_mode'] = entry['ringer_mode']
    ordered['current_fb_max_mins'] = entry['current_fb_max_mins']
    ordered['current_fb_max_opens'] = entry['current_fb_max_opens']
    ordered['current_treatment_start'] = entry['current_treatment_start']
    ordered['current_followup_start'] = entry['current_followup_start']
    ordered['current_logging_stop'] = entry['current_logging_stop']
    ordered['time_spent_list'] = entry['time_spent_list']
    ordered['current_firebase_token'] = entry['current_firebase_token']

    return ordered


@app.route('/mobile/turkprime/all/fb-stats')
def get_all_fb_stats():
    stats = TP_FBStats.query.all()
    return json.dumps({'stats': stats})


def rm_null(val):
    return "" if (val == "None" or val == None) else val


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


@app.route('/mobile/mturk/prelim-recruit', methods=['POST'])
def prelim_recruit():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response, worker = MturkPrelimRecruit.add_worker(data)

    if status == 200:
        response = response + '\nYour Mturk Code: {}'.format(worker.worker_code)

    return json.dumps({'status': status, 'response': response})


@app.route('/mturk/register/csv', methods=['POST'])
def register_mturk_workers():
    csv_file = request.files.get('mturk.csv')
    count = 0
    duplicates = ""
    for row in csv.reader(csv_file):
        worker_info = get_worker_info(row)
        status, _, worker = MturkExclusive.add(worker_info)
        if status == 200:
            count += 1
        else:
            duplicates += worker.worker_id + "; "

    duplicates = "None" if duplicates == "" else duplicates
    response = -1
    if csv_file:
        response = 'Successfully registered {} new user(s).<br><br>Duplicates:<br>{}'.format(count, duplicates)

    return response


def get_worker_info(row):
    w_id, exp_group, exp_code, exp_label = row
    return {
        'worker_id': w_id.strip(),
        'experiment_group': exp_group.strip(),
        'experiment_code': exp_code.strip(),
        'experiment_label': exp_label.strip()
    }


@app.template_filter('nyc')
def _jinja2_filter_nyctime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('America/New_York'))


@app.template_filter('india')
def _jinja2_filter_indiatime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('Asia/Calcutta'))


@app.template_filter('fancydatetime')
def _jinja2_strformat_datetime(date, fmt=None):
    # return date.strftime('%b %d %Y, %-I:%M %p')
    return date.strftime('%b %d, %-I:%M %p')


@app.template_filter('onlyfancydate')
def _jinja2_strformat_only_date(date):
    return date.strftime('%b %d, %Y')


@app.template_filter('onlyfancytime')
def _jinja2_strformatonly_time(time_str):
    if not ':' in time_str: return time_str
    date = datetime.now()
    hr, mins = time_str.split(':')[:2]
    date = date.replace(hour=int(hr), minute=int(mins))
    return date.strftime('%-I:%M %p')


@app.template_filter('todatetime')
def _jinja2_strformat_ftime(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')


@app.template_filter('ms_to_datetime')
def _jinja2_ms_to_datetime_ftime(time_milli):
    return millis_to_dt(time_milli)


@app.template_filter('str_to_json')
def _str_to_json(json_str):
    return json.loads(json_str)


@app.template_filter('id_to_text_image')
def split_into_text_image(text_image_id):
    if text_image_id != 'baseline':
        return 200, ImageTextUpload.query.get(int(text_image_id))
    return -1, text_image_id

# TODO: handle moves expired access token
# TODO: only enable activate tracking for an app that has been connected
# TODO: create table to delete any image
# TODO: allow uploads of multiple images at same time
# TODO: allow images to be saved by pasting custom url
# TODO: allow images to be uploaded from drag and drop
# TODO: prevent inserting interventions for the same date
# TODO: disable save entry button until preview has been done.
# TODO: change start & end datetime from string to datetime format in models
# TODO: after save, jump to apply intv anchor on web page
# TODO: format stnd and end time
# TODO: merge update group and update experiment functions
# TODO: add proper confirmation prompty library
# TODO: add testing



# RescueTime
@app.route("/auth-rt")
@login_required
def auth_rt():
    if 'error' in request.args:
        flash('Sorry, authentication denied by user :(', 'danger')
        return redirect(url_for('technion_home'))

    rt = RescueOauth2()

    code = request.args.get('code')
    if not code:
        return redirect(rt.auth_url)

    access_token = rt.fetch_access_token(code)
    # import ipdb; ipdb.set_trace()
    user = TechnionUser.get_user(current_user.email)
    user.update_field('rescuetime_access_token', access_token)
    flash('Successfully connected RescueTime!', 'success')

    return redirect(url_for('technion_home'))


@app.route('/login-technion-user')
def login_technion_user():
    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_PARTICIPANT'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'login_technion_user', _external=True))

    auth_code = request.args.get('code')
    if not auth_code:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    credentials = flow.step2_exchange(auth_code, http=httplib2.Http())
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('oauth2', 'v2', http=http)

    profile = service.userinfo().get().execute()
    user = TechnionUser.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())

    login_user(user)
    return redirect(url_for('technion_home'))

# DO NOT REMOVE THIS AS IT IS FOR ONGOING EXPERIMENT
# MOVING default view to show participant page because of an experiment
# Default login view for the beehive platform
@app.route('/')
@app.route('/technion-home')
def technion_home():
    if not current_user.is_authenticated:
        return render_template('technion/technion-index.html')

    if 'code' in request.args:
        code = request.args.get('code')
        return redirect(url_for('auth_rt', code=code))

    if 'error' in request.args:
        error = request.args.get('error')
        return redirect(url_for('auth_rt', error=error))

    ctx = {'participant': TechnionUser.query.get(current_user.email)}
    return render_template('technion/technion-home.html', **ctx)

@app.route('/tdash')
def technion_dashboard():
    ctx = {'technion_users': TechnionUser.query.all()}
    return render_template('technion/technion-dashboard.html', **ctx)

@app.route('/subliminal')
def subliminal():
    return render_template('subliminal.html')

