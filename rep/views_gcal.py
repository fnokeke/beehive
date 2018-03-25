import json
import os, time
import httplib2, requests

from rep import app
from flask import render_template, flash
from flask import redirect, url_for, session, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

from apiclient import discovery
from datetime import date, timedelta
from rep.models import  Researcher, GcalUser

from oauth2client.client import OAuth2WebServerFlow
from sendgrid.helpers.mail import *


@app.route('/login-gcal-user')
def login_gcal_user():
    flow = OAuth2WebServerFlow(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=app.config['GOOGLE_SCOPE_PARTICIPANT'],
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for(
            'login_gcal_user', _external=True))

    auth_code = request.args.get('code')
    if not auth_code:
        print " login-gcal-user: No Code"
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

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

