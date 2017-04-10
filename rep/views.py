"""
Handle all app views
"""

from flask import flash, redirect, url_for, session, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from oauth2client.client import OAuth2WebServerFlow

from apiclient import discovery

import json, httplib2, pytz, requests, csv

from rep import app, login_manager
from rep.models import Experiment, Intervention, MobileUser, Mturk, MturkPrelimRecruit
from rep.models import MturkExclusive, NafEnroll, User, ImageTextUpload
from rep.models import CalendarConfig, DailyReminderConfig, GeneralNotificationConfig, VibrationConfig
from rep.models import NotifClickedStats, RescuetimeConfig, ScreenUnlockConfig

from rep.models import TP_DailyResetHour, TP_Enrolled, TP_Admin, TP_FBStats

from rep.rescuetime import RescueOauth2, RescueTime
from rep.pam import PamOauth
from rep.moves import Moves
from rep.errors import SLMError
from rep.upload import Upload

from rep import export

from gcal import Calendar, EventFactory
from rep.utils import requires_basic_auth
from rep.utils import to_json, to_datetime
from datetime import datetime


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
@app.route('/')
def index():

    if not current_user.is_authenticated:
        return render_template('index.html')

    if 'code' in request.args:
        code = request.args.get('code')
        return redirect(url_for('auth_rt', code=code))

    if 'error' in request.args:
        error = request.args.get('error')
        return redirect(url_for('auth_rt', error=error))

    return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


@app.route('/researcher_analysis/<key>/<study_begin>/<int_begin>/<int_end>/<study_end>')
@requires_basic_auth
def perform_research_analysis(key, study_begin, int_begin, int_end, study_end):
    results = {}
    users = User.get_all_users()

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


@app.route('/researcher_login')
@requires_basic_auth
def researcher_login():
    ctx = {'users': User.query.all(),
           'mobile_users': MobileUser.query.all(),
           'mturk_users': Mturk.query.all(),
           'experiments': Experiment.query.all(),
           'interventions': Intervention.query.all()}
    return render_template('researcher.html', **ctx)


@app.route('/experiments')
@requires_basic_auth
def experiments():
    ctx = {'users': User.query.all(),
           'mobile_users': MobileUser.query.all(),
           'mturk_users': Mturk.query.all(),
           'experiments': Experiment.query.all(),
           'interventions': Intervention.query.all()}
    return render_template('researcher.html', **ctx)


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@login_manager.user_loader
def user_loader(user_id):
    return User.get_user(user_id)

#################################
# Handle Errors
#################################


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error('Server Error: %s', (e))
    return SLMError.internal_server_error


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
        return json.dumps({'response': jsonify_responses('Already enrolled in experiment', ''),
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
    rt_user = User.query.filter_by(email=data['email']).first()
    if not rt_user: return {}
    return RescueTime.fetch_summary(rt_user.rescuetime_access_token, data['date'])


@app.route("/rescuetime/realtime", methods=['POST'])
def fetch_rt_realtime_activity():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    rt_user = User.query.filter_by(email=data['email']).first()
    if not rt_user: return {}
    return RescueTime.fetch_activity(rt_user.rescuetime_access_token, data['date'])


@app.route("/mobile/check/rescuetime", methods=['POST'])
def check_rt_conn():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    user = User.query.filter_by(email=data['email']).first()

    response = False
    if user:
        if user.rescuetime_access_token:
            response = True

    result = {'rt_response': response, 'rt_email': data['email']}
    return json.dumps(result)


@app.route("/mobile/check/calendar", methods=['POST'])
def check_cal_conn():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    user = User.query.filter_by(email=data['email']).first()

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
    user = User.query.filter_by(email=email).first()
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
        'users_unfiltered': User.query.all(),
        'experiment': experiment,
        'image_texts': ImageTextUpload.query.filter_by(code=code).all(),
        'uploaded_intvs': ImageTextUpload.query.filter_by(code=code).all(),
        'general_notifs': GeneralNotificationConfig.query.filter_by(code=code).all(),
        'gg': GeneralNotificationConfig,
        'interventions': interventions
    }
    return render_template('edit-experiment.html', **ctx)


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
    ctx = {'experiment': experiment, 'users_unfiltered': User.query.all()}
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
    ctx = {'mturk_stats': TP_FBStats.query.all(), 'experiment': experiment}
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


# Google login and calendar
@app.route('/google_login')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'google_login', _external=True))

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
    user = User.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())

    login_user(user)
    return redirect(url_for('home'))


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


# RescueTime
@app.route("/auth-rt")
@login_required
def auth_rt():
    if 'error' in request.args:
        flash('Sorry, authentication denied by user :(', 'danger')
        return redirect(url_for('home'))

    rt = RescueOauth2()

    code = request.args.get('code')
    if not code:
        return redirect(rt.auth_url)

    access_token = rt.fetch_access_token(code)
    current_user.update_field('rescuetime_access_token', access_token)
    flash('Successfully connected RescueTime!', 'success')

    return redirect(url_for('home'))


# PAM
@app.route("/auth-pam")
@login_required
def auth_pam():
    url = app.config['PAM_DSU'] + '/oauth/authorize?client_id={}&response_type=code'.format(app.config['PAM_CLIENT_ID'])

    print 'pam url: {}'.format(url)
    print 'pam token url: {}'.format(app.config['PAM_ACCESS_TOKEN_URL'])
    return redirect(url)


@app.route("/oauth2callback-pam")
def pam_oauth2callback():

    code = request.args.get('code')

    if not code:
        flash('sorry, could not connect PAM', 'danger')
    else:
        pam_oauth = PamOauth()
        access_token, refresh_token = pam_oauth.get_tokens(code)
        current_user.update_field('pam_access_token', access_token)
        current_user.update_field('pam_refresh_token', refresh_token)

        if not (access_token and refresh_token):
            flash('Sorry, connection failed. contact admin.', 'danger')
        else:
            flash('Successfully connected to PAM!', 'success')

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
        flash('Sorry, you have not authenticated PAM', 'danger')

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
        return SLMError.invalid_input_error

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
    return render_template('mturk/naf-join.html')


@app.route('/naf/<worker_id>')
def naf_watch_videos(worker_id):
    enrolled_worker = NafEnroll.query.filter_by(worker_id=worker_id).first()
    if not enrolled_worker:
        return render_template('mturk/mturk-404.html')
    if not 'step' in session:
        session['step'] = 1
    return render_template('mturk/naf-main.html', worker=enrolled_worker)


@app.route('/naf/update/step', methods=['POST'])
def naf_update_step():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    next_step = 1 + int(data['current_step']) % 8
    session['step'] = next_step
    return json.dumps({'next_step': next_step})


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

    # link = "<a href='/naf/{}'>continue here</a>.".format(worker_id)
    # enrolled_worker = MturkExclusive.query.filter_by(worker_id=worker_id).first()
    # current_datetime = datetime.now().strftime("%I:%M:%S %p on %B %d %Y")
    # if not enrolled_worker:
    # log_submission(current_datetime, worker_id, 'rejected')
    # return 'Worker ({}) cannot partake in experiment. You have to be registered by researcher.'.format(worker_id)

    # log_submission(current_datetime, worker_id, 'accepted')
    # link = "<a href='/naf/{}'>continue here</a>.".format(worker_id)
    # return 'Welcome {}, {}'.format(worker_id, link)


def naf_get_next_condition(total_enrolled):
    no_of_groups = 6
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
        print '{}/{}'.format(msg, gen_code)
    else:
        flash(msg, 'danger')
        print 'sorry, user add error: {} / {}'.format(msg, gen_code)

    return redirect(url_for('mturk', gen_code=gen_code))


@app.route('/mobile/turkprime/enroll', methods=['POST'])
def mobile_worker_id():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    status, response, worker = TP_Enrolled.add_user(data)
    if status == -1:
        return json.dumps({'status': -1, 'response': response, 'worker_id': -1, 'survey_link': ''})

    TP_Admin.add_user(data)
    user_response = response + '\nYour Code: {}\nRemember to complete survey:'.format(worker.worker_code)
    server_response = {'status': 200,
                       'response': user_response,
                       'worker_id': worker.worker_id,
                       'survey_link': 'http://bit.ly/beginExp'}
    return json.dumps(server_response)


@app.route('/mobile/turkprime/fb-stats', methods=['POST'])
def mobile_worker_fb_stats():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    _, response, stats = TP_FBStats.add_stats(data)
    server_response = {'response': response, 'worker_id': data['worker_id'], 'summary': to_json(stats)}
    server_response = append_admin_fb_response(server_response)
    return json.dumps(server_response, default=str)


def append_admin_fb_response(data):
    worker = TP_Admin.query.filter_by(worker_id=data['worker_id']).first()
    if worker:
        data['admin_experiment_group'] = worker.admin_experiment_group
        data['admin_fb_max_mins'] = worker.admin_fb_max_mins
        data['admin_fb_max_opens'] = worker.admin_fb_max_opens
        data['admin_treatment_start'] = worker.admin_treatment_start
        data['admin_followup_start'] = worker.admin_followup_start
        data['admin_logging_stop'] = worker.admin_logging_stop
        data['admin_daily_reset_hour'] = TP_DailyResetHour.get_last_updated_hour()
    else:
        data['admin_experiment_group'] = 1
        data['admin_fb_max_mins'] = 13
        data['admin_fb_max_opens'] = 13
        data['admin_treatment_start'] = '2017-04-18'
        data['admin_followup_start'] = '2017-04-25'
        data['admin_logging_stop'] = '2017-05-04'
        data['admin_daily_reset_hour'] = '0'
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
        'worker_id': w_id.strip(" "),
        'experiment_group': exp_group.strip(" "),
        'experiment_code': exp_code.strip(" "),
        'experiment_label': exp_label.strip(" ")
    }


@app.template_filter('nyc')
def _jinja2_filter_nyctime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('America/New_York'))


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
