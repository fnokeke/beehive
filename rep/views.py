"""
Handle all app views
"""

from flask import flash, redirect, url_for, session, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from oauth2client.client import OAuth2WebServerFlow

from apiclient import discovery

import json, httplib2, requests

from rep import app, login_manager
from rep.models import User, Mturk
from rep.rescuetime import RescueOauth2
from rep.pam import PamOauth
from rep.moves import Moves
from rep.errors import SLMError
from rep.upload import Upload

from rep import export

from gcal import Calendar, EventFactory
from rep.utils import requires_basic_auth


@app.route('/')
@app.route('/index')
@app.route('/mturk')
def mturk():
    return render_template('mturk.html')

#################################
# MTURK
#################################


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


#################################
# MTURK
#################################
@app.route('/old_index')
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


@app.route('/experiments')
@login_required
def experiments():
    return render_template('experiments.html')


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/fetch/images')
def fetch_uploads():
    return json.dumps(Upload.get_all_urls())
    # return '{}'.format(Upload.get_all_urls())


@app.route('/upload/image', methods=['POST'])
def image_upload():
    image_name = request.form['image_name']
    image = request.files['image']

    Upload.save(image_name, image)
    url = Upload.get_url(image_name)
    return 'Retrieved image: {}'.format(url)


@app.route('/upload/txt', methods=['POST'])
def txt_upload():
    txt = request.form.get('txt')
    return 'Got txt: {}'.format(txt)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


@login_manager.user_loader
def user_loader(user_id):
    return User.get_user(user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error('Server Error: %s', (e))
    return SLMError.internal_server_error

#######################################
# Authenticate Services
#######################################


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


@app.route('/researcher_login')
@requires_basic_auth
def researcher_login():
    return render_template('researcher.html', users=User.query.all(), mturk_users=Mturk.query.all())


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

# TODO: http://stackoverflow.com/questions/25065194/google-sign-in-uncaught-securityerror
# TODO: catch calendar insert errors and update UI errors accordingly
# TODO: fix calendar CSS view to make it render the dates properly
# TODO: change everywhere you have MOOD to PAM
# TODO: handle moves expired access token
# TODO: only enable activate tracking for an app that has been connected
# TODO: divide the modules into researcher and participants
# TODO: remove the CSS table formatting in researcher page
# TODO: automatically refresh list of all images on image upload
# TODO: create table to delete any image
# TODO: allow uploads of multiple images at same time
# TODO: allow images to be saved by pasting custom url
# TODO: allow images to be uploaded from drag and drop
