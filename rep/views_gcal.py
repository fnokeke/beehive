import json, pytz
import os, time, datetime
import httplib2
from rep import app
from flask import render_template, flash, send_file, make_response
from flask import redirect, url_for, session, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from apiclient import discovery
from datetime import date, datetime, timedelta
from rep.models import  Researcher, GcalUser, Experiment

from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client
from sendgrid.helpers.mail import *
from gcal import CalendarService, Calendar


@app.route('/gcal/dash')
def gcal_dashboard():
    gcal_users = GcalUser.get_all_users_data()
    print "gcal_users:", gcal_users
    data = []
    ctx = {'users': gcal_users, 'data': data}
    return render_template('/gcal/gcal-dashboard.html', **ctx)


@app.route('/gcal/download/<start>/<end>/')
def gcal_download(start, end):
    print "<start>:", start
    print "<end>:", end
    download_name = start + '-  to-' + end
    start = start.replace('-',' ') + ' ' + '00'+ ' ' + '00' + ' ' + '00'
    end = end.replace('-', ' ') + ' ' + '23' + ' ' + '59' + ' ' + '59'

    try:
        start_date = datetime.strptime(start, '%Y %m %d %H %M %S')
        end_date = datetime.strptime(end, '%Y %m %d %H %M %S')
    except:
        print "gcal_download: Date parsing exception!"
        mdate = datetime.now(pytz.timezone('America/New_York'))
        start_date = mdate
        end_date = mdate + timedelta(days=3)


    print "<start_date>:", start_date
    print "<end_date>:", end_date
    data = []
    gcal_users = GcalUser.get_all_users_credentials()
    for user in gcal_users:
        # Download and save calender
        google_credentials = client.OAuth2Credentials.from_json(user['google_credentials'])
        http = httplib2.Http()

        if google_credentials.access_token_expired:
            google_credentials.refresh(http)

        http_auth = google_credentials.authorize(http)
        gcal_service = discovery.build('calendar', 'v3', http=http_auth)
        events = get_calender_events_in_range(gcal_service, start_date, end_date)
        print "+++++++++++  USER = ", user['email'] , ' \n\n\n'
        print events
        res = {}
        res['email'] = user['email']
        res['events'] = events
        data.append(res)
        print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++ \n\n\n "

    BASE_DIR = "./gcal/"
    filename = "gcal-events.txt"
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    file_path = BASE_DIR + filename

    file = open(file_path, "w+");
    file.write(json.dumps(data))
    file.close()

    full_file_path = os.path.join(app.root_path, 'gcal', 'gcal-events.txt')
    print "full_file_path: ", full_file_path

    try:
        #return send_file("test", as_attachment=True, attachment_filename='beehive-gcal.txt')
        json_data = json.dumps(data)
        response = make_response(json_data)
        cd = 'attachment; filename=beehive-gcal-' + download_name + '.json'
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/json'
        return response

    except Exception as e:
        ctx = {'users': gcal_users, 'data': data}
        return render_template('/gcal/gcal-dashboard.html', **ctx)



@app.route('/login-gcal-user')
def login_gcal_user():
    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_CALENDER_READ'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'login_gcal_user', _external=True))

    auth_code = request.args.get('code')
    if not auth_code:
        print " login-gcal-user: No Code"
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    # Google auth success
    print " login-gcal-user: auth_code success"
    credentials = flow.step2_exchange(auth_code, http=httplib2.Http())
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('oauth2', 'v2', http=http)

    profile = service.userinfo().get().execute()
    user = GcalUser.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())

    login_user(user)
    session['user_type'] = 'gcal_user'

    # Download and save calender
    # gcal_service = discovery.build('calendar', 'v3', http=http)
    # mdate = datetime.now(pytz.timezone('America/New_York'))
    # start = mdate - timedelta(days=1)
    # end = mdate + timedelta(days=3)
    # events = get_calender_events_in_range(gcal_service, start, end)

    user.update_field('connected', True)
    return redirect(url_for('gcal_home'))


# Return function after Google login
@app.route('/gcal')
def gcal_home():
    if not current_user.is_authenticated:
        return render_template('/gcal/gcal-index.html')

    # if 'code' in request.args:
    #     code = request.args.get('code')
    #     print " gcal_home(): code OK"
    #     return redirect(url_for('gcal_home', code=code))
    #
    # if 'error' in request.args:
    #     error = request.args.get('error')
    #     print " gcal_home(): ERROR"
    #     return redirect(url_for('gcal_home', error=error))

    # Go directy to Gcal home
    print " gcal_home(): Success"
    ctx = {'gcal_user': GcalUser.query.get(current_user.email)}
    return render_template('/gcal/gcal-home.html', **ctx)


# Function to download calender events in a date range
def get_calender_events_in_range(service, start, end):
    # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    # mdate = datetime.now(pytz.timezone('America/New_York'))

    start_time = start.strftime('%Y-%m-%dT%H:%M:%Sz')
    end_time = end.strftime('%Y-%m-%dT%H:%M:%Sz')

    eventsResult = service.events().list(
        calendarId='primary', timeMin=start_time, timeMax=end_time, orderBy='startTime', singleEvents=True).execute()

    events = eventsResult.get('items', [])

    events_list = [];
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start, event['summary'], end)
        res = {}
        res['summary'] = event['summary'];
        res['start'] = start;
        res['end'] = end;
        events_list.append(res)
    return events_list


# Function to download 10 calender events
def get_calender_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print 'get_calender_events:', start, event['summary']
    return events


@app.route("/submit/gcalcode", methods=['POST'])
def submit_gcal_code():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    response = GcalUser.update_code(data)
    result = {'is_valid': "success" in response, 'response': response, 'code': data['code']}
    return json.dumps(result)
