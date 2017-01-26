"""
Handle all app views
"""

from flask import flash, redirect, url_for, session, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from oauth2client.client import OAuth2WebServerFlow

from apiclient import discovery

import json, httplib2, pytz, requests

from rep import app, login_manager
from rep.models import Experiment, Intervention, MobileUser, Mturk, User, Uploaded_Intv
from rep.rescuetime import RescueOauth2, RescueTime
from rep.pam import PamOauth
from rep.moves import Moves
from rep.errors import SLMError
from rep.upload import Upload

from rep import export

from gcal import Calendar, EventFactory
from rep.utils import requires_basic_auth
from datetime import datetime


@app.route('/googlebcabee7122e5544b.html')
def google_domain_verification():
    return render_template('googlebcabee7122e5544b.html')


@app.route('/focus')
def justdoit():
    return render_template('justdoit.html')


#################################
# template views
#################################
@app.route('/index')
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


@app.route('/experiments')
@login_required
def experiments():
    return render_template('experiments.html')


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
    experiment = Experiment.query.filter_by(code=data['code']).first()
    if not experiment:
        return json.dumps({'experiment': 'None'})

    # already in experiment so no need to change anything
    already_in_experiment = MobileUser.query.filter_by(email=data['email'], code=data['code']).first()
    if already_in_experiment:
        response = 'Already enrolled in experiment.'
        user = already_in_experiment
        result = {'response': response, 'user': str(user), 'experiment': str(experiment)}
        return json.dumps(result)

    # condition needs to be updated for remaining operation
    total_enrolled = len(MobileUser.query.filter_by(code=data['code']).all())
    condition = get_next_condition(total_enrolled, experiment.ps_per_condition)

    # in one experiment and moving to another
    user_exists = MobileUser.query.filter_by(email=data['email']).first()
    if user_exists:
        MobileUser.update_field(data['email'], 'condition', condition)
        _, __, user = MobileUser.update_field(data['email'], 'code', data['code'])
        response = 'Successfully switched to another experiment ({}).'.format(data['code'])
        result = {'response': response, 'user': str(user), 'experiment': str(experiment)}
        return json.dumps(result)

    # enrolling as first timer in an experiment
    # data contains all attributes for new user except condition so add that property
    data['condition'] = condition
    _, response, user = MobileUser.add_user(data)
    result = {'response': response, 'user': str(user), 'experiment': str(experiment)}
    return json.dumps(result)


#////////////////////////////////////////////
# mobile Beehive rescuetime && interventions
#////////////////////////////////////////////
@app.route("/rescuetime/summary/<email>/<date>")
def get_summary_rt_data(email, date):
    rt_user = User.query.filter_by(email=email).first()
    if not rt_user:
        return {}

    result = RescueTime.fetch_intv_feed(rt_user.rescuetime_access_token, date)
    return json.dumps(result)


@app.route("/rescuetime/realtime/<email>/<date>")
def get_rt_realtime_activity(email, date):
    rt_user = User.query.filter_by(email=email).first()
    if not rt_user:
        return {}

    result = RescueTime.fetch_realtime_feed(rt_user.rescuetime_access_token, date)
    return json.dumps(result)


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


@app.route('/mobile/ordered/interventions/<code>', methods=['GET'])
def fetch_ordered_interventions(code):
    interventions = Intervention.query.filter_by(code=code).order_by('created_at desc').all()
    return '{}'.format(interventions)


#////////////////////////////////////
# Researcher modify experiments
#////////////////////////////////////
@app.route('/add/experiment', methods=['POST'])
def add_experiment():
    experiment = {
        'title': request.form.get('title'),
        'rescuetime': True if request.form.get('rescuetime') == 'true' else False,
        'aware': True if request.form.get('aware') == 'true' else False,
        'geofence': True if request.form.get('geofence') == 'true' else False,
        'text': True if request.form.get('text') == 'true' else False,
        'image': True if request.form.get('image') == 'true' else False,
        'reminder': True if request.form.get('reminder') == 'true' else False,
        'actuators': True if request.form.get('actuators') == 'true' else False
    }

    _, response, __ = Experiment.add_experiment(experiment)
    return response


@app.route('/edit-experiment/<code>')
def edit_experiment(code):
    ctx = {
        'enrolled_users': MobileUser.query.filter_by(code=code).all(),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'uploaded_intvs': Uploaded_Intv.query.all(),
        'interventions': Intervention.query.filter_by(code=code).order_by('created_at desc').all()
    }
    return render_template('edit-experiment.html', **ctx)


@app.route('/delete/experiment/<code>')
def delete_experiment(code):
    Experiment.delete_experiment(code)
    flash('Returning to experiment page.', 'success')
    return redirect(url_for('researcher_login'))


@app.route('/update/experiment', methods=['POST'])
def update_experiment():
    update = {
        'title': request.form.get('title'),
        'code': request.form.get('code'),
        'rescuetime': True if request.form.get('rescuetime') == 'true' else False,
        'aware': True if request.form.get('aware') == 'true' else False,
        'geofence': True if request.form.get('geofence') == 'true' else False,
        'text': True if request.form.get('text') == 'true' else False,
        'image': True if request.form.get('image') == 'true' else False,
        'reminder': True if request.form.get('reminder') == 'true' else False,
        'actuators': True if request.form.get('actuators') == 'true' else False
    }
    updated_exp = Experiment.update_experiment(update)
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
    intv = {
        'code': request.form.get('code'),
        'treatment': request.form.get('treatment'),
        'start': request.form.get('start'),
        'end': request.form.get('end'),
        'every': request.form.get('every'),
        'when': request.form.get('when'),
        'repeat': request.form.get('repeat')
    }

    intv['start'] = datetime.strptime(intv['start'], '%Y-%m-%dT%H:%M:%S.000Z')
    intv['end'] = datetime.strptime(intv['end'], '%Y-%m-%dT%H:%M:%S.000Z')

    _, response, added_intv = Intervention.add_intervention(intv)
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
    image = request.files.get('image')

    image_url = None
    if image_name and image:
        Upload.save(image_name, image)
        image_url = Upload.get_url(image_name)

    new_intv = {'text': text, 'image_name': image_name, 'image_url': image_url}
    Uploaded_Intv.add_intv(new_intv)

    msg = ''
    if image and image_name and text:
        msg = 'image with text added.'
    elif image and image_name:
        msg = 'only image added.'
    elif text:
        msg = 'only text added.'

    return msg


@app.route('/fetch/uploaded/intervention', methods=['GET'])
def fetch_uploaded_intv():
    all_intv = Uploaded_Intv.query.all()
    return '{}'.format(all_intv)

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


@app.route('/mturk')
def mturk():
    return render_template('mturk.html')


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


@app.route('/mturk/worker_id', methods=['POST'])
def worker_id():
    worker_id = request.form['worker_id']
    session['worker_id'] = worker_id
    return 'Rcvd id: {}'.format(worker_id)


@app.template_filter('nyc')
def _jinja2_filter_nyctime(date, fmt=None):
    return pytz.utc.localize(date).astimezone(pytz.timezone('America/New_York'))


@app.template_filter('fancydatetime')
def _jinja2_strformat_datetime(date, fmt=None):
    return date.strftime('%b %d, %Y / %-I:%M %p')


@app.template_filter('onlyfancydate')
def _jinja2_strformat_only_date(date):
    return date.strftime('%b %d, %Y')


@app.template_filter('onlyfancytime')
def _jinja2_strformatonly_time(time_str):
    date = datetime.now()
    hr, mins, secs = time_str.split(':')
    if '.' in secs:
        secs, _ = secs.split('.')
    date = date.replace(hour=int(hr), minute=int(mins), second=int(secs))
    return date.strftime('%-I:%M %p')


@app.template_filter('todatetime')
def _jinja2_strformat_ftime(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')

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
