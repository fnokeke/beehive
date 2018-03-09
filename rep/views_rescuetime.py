from rep import app
from flask import render_template

import json
import time
import os
import httplib2

from flask import redirect, url_for, session, render_template, request
from flask_login import login_user, current_user

from apiclient import discovery
from datetime import date, timedelta
from rep.models import RescuetimeUser, RescuetimeData
from rep.rescuetime import RescueTime
from oauth2client.client import OAuth2WebServerFlow


@app.route('/login-rescuetime-user')
def login_rescuetime_user():
    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_PARTICIPANT'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'login_rescuetime_user', _external=True))

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
    user = RescuetimeUser.from_profile(profile)
    user.update_field('google_credentials', credentials.to_json())

    login_user(user)
    session['user_type'] = 'rescuetime_user'
    return redirect(url_for('rescuetime_home'))


@app.route('/rescuetime')
def rescuetime_home():
    if not current_user.is_authenticated:
        return render_template('/rtime/rtime-index.html')

    if 'code' in request.args:
        code = request.args.get('code')
        return redirect(url_for('auth_rt', code=code))

    if 'error' in request.args:
        error = request.args.get('error')
        return redirect(url_for('auth_rt', error=error))

    ctx = {'rtime_user': RescuetimeUser.query.get(current_user.email)}
    return render_template('/rtime/rtime-home.html', **ctx)




# Dashboard RescueTime summary
@app.route('/rescuetime/stats')
def rescuetime_stats():
    days = request.args.get('days')

    if days:
        num_days = int(days)
    else:
        num_days = 7;

    # Check value is in range
    if num_days < 7 or num_days > 45:
        num_days = 7;

    date_yesterday = date.today() - timedelta(days=1)
    users = RescuetimeUser.get_all_users_data()

    # print "Current year: ", date_yesterday.strftime("%Y")
    # print "Month of year: ", date_yesterday.strftime("%B")
    # print "Week number of the year: ", date_yesterday.strftime("%W")
    # print "Weekday of the week: ", date_yesterday.strftime("%w")
    # print "Day of year: ", date_yesterday.strftime("%j")
    # print "Day of the month : ", date_yesterday.strftime("%d")
    # print "Day of week: ", date_yesterday.strftime("%A")

    data = []
    for user in users:
        count = 0
        days = []
        for num in range (2, num_days+2):
            created_date = date.today() - timedelta(days=num)
            try:
                count_rows = RescuetimeData.query.filter_by(email=user['email'], created_date=created_date).count()
                if(count_rows>0):
                    days.append("true")
                    count = count + 1;
                else:
                    days.append("")
            except:
                days.append("")

        user['days'] = days
        user['count'] = count
        del user['access_token']
        data.append(user)

    dates = []
    for num in range(2, num_days+2):
        created_date = date.today() - timedelta(days=num)
        month = created_date.strftime("%B")
        date_formatted = month[:3] + " "+  created_date.strftime("%d")
        dates.append(date_formatted)
    ctx = {'users': data, 'dates': dates}
    # store_rescuetime_data will be added to taskqueue managed by the apscheduler
    return render_template('/rtime/rtime-stats.html', **ctx)



# Note that ther is similar function defined above for the path ('/rescuetime-dashboard/<code>')
# Dashboard for all user RescueTime stats
@app.route('/rescuetime/dash')
def dashboard_rescuetime():
    date_yesterday = date.today() - timedelta(days=2)
    users = RescuetimeUser.get_all_users_data()

    data = []
    for user in users:
        try:
            # "row_headers":["Rank","Time Spent (seconds)","Number of People","Activity","Category","Productivity"],
            json_data = json.loads(RescueTime.fetch_daily_activity_rank(user['access_token'], date_yesterday))
            json_data = json_data['rows']
            json_data = json_data[0:5]
            user['data'] = json_data
        except:
            no_data = ["", "", "", "", "", ""]
            user['data'] = no_data
            print "dashboard_rescuetime:", "SKIP - no data for user,", user['email']

        del user['access_token']
        data.append(user)

    ctx = {'users': data, 'date': date_yesterday}
    # store_rescuetime_data will be added to taskqueue managed by the apscheduler
    return render_template('/rtime/rtime-dashboard.html', **ctx)



def store_rescuetime_data():
    print "store_rescuetime_data:", time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    BASE_DIR = "./rescuetime/"
    date_yesterday = date.today() - timedelta(days=2)

    try:
        # Sanity check if RescuetimeUser exists
        users = RescuetimeUser.get_all_users_data()
    except:
        print "store_rescuetime_data:", "FAILED - rescuetime_user table not found!"
        return

    try:
        # Sanity check to avoid database data duplication
        count_rows = RescuetimeData.query.filter_by(created_date=date_yesterday).count()
        if count_rows:
            print "store_rescuetime_data: Data already available in database for date:", date_yesterday
            return
    except:
        print "store_rescuetime_data:", "FAILED - rescuetime_data table not found!"
        return

    # Download JSON data and store in a file
    print "###############################################################################################"
    print "store_rescuetime_data: Running RescueTime data collection procedure for date:", date_yesterday
    data = []
    count = 0
    saved = 0
    for user in users:
        count = count + 1
        directory = BASE_DIR + user['email']
        file_path = directory + "/" + str(date_yesterday)

        if not os.path.exists(directory):
            os.makedirs(directory)

        # "row_headers":["Rank","Time Spent (seconds)","Number of People","Activity","Category","Productivity"]
        try:
            csv_data = RescueTime.fetch_daily_activity_interval_minute(user['access_token'], date_yesterday, 'csv')
            # Write to file
            file = open(file_path, "w+");
            file.write(str(csv_data))
            file.close()

            # Write to database
            json_data = json.loads(
                RescueTime.fetch_daily_activity_interval_minute(user['access_token'], date_yesterday, 'json'))
            rows = json_data['rows']
            data = {}
            for row in rows:
                data['email'] = user['email']
                data['created_date'] = date_yesterday
                data['date'] = row[0]
                data['time_spent'] = row[1]
                data['num_people'] = row[2]
                data['activity'] = row[3]
                data['category'] = row[4]
                data['productivity'] = row[5]
                status, response, _ = RescuetimeData.add(data)
            saved = saved + 1
        except:
            print "store_rescuetime_data: JSON parse error for user", user['email']

    print "store_rescuetime_data: Data saved for",saved, "of", count, "RescueTime users."
    print "store_rescuetime_data: RescueTime Data collection completed!"
    print "###############################################################################################"
