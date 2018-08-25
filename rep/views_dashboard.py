from rep import app
from flask import render_template

from rep.models import Experiment, InAppAnalytics, MobileSurvey, MobileUser
from rep.models import PAM, Protocol, RescuetimeUser, TP_FgAppLog, TP_ScreenLog

from datetime import datetime
import utils


@app.route('/survey-events/display/<code>')
def display_survey(code):
    ctx = get_exp_context(code)
    ctx['survey_events'] = MobileSurvey.query.filter_by(code=code).all()
    return render_template('experiment/experiment-survey.html', **ctx)


@app.route('/ipam-events/display/<code>')
def display_ipam(code):
    ctx = get_exp_context(code)
    ctx['pam_events'] = PAM.query.filter_by(code=code).all()
    return render_template('experiment/experiment-ipam.html', **ctx)


@app.route('/app-usage/display/<code>')
def display_app_usage(code):
    ctx = get_exp_context(code)
    ctx['app_usage'] = TP_FgAppLog.query.filter_by(code=code).order_by('created_at desc').limit(500).all()
    return render_template('experiment/experiment-app-usage.html', **ctx)


@app.route('/screen-events/display/<code>')
def display_screen_events(code):
    ctx = get_exp_context(code)
    ctx['screen_events'] = TP_ScreenLog.query.filter_by(code=code).order_by('created_at desc').limit(500).all()
    return render_template('experiment/experiment-screen-events.html', **ctx)


@app.route('/app-analytics/display/<code>')
def display_app_analytics(code):
    ctx = get_exp_context(code)
    ctx['inapp_events'] = InAppAnalytics.query.filter_by(code=code).order_by('created_at desc').limit(500).all()
    return render_template('experiment/experiment-app-analytics.html', **ctx)


@app.route('/contexts/display/<code>')
def display_contexts(code):
    ctx = get_exp_context(code)
    return render_template('experiment/experiment-protocols.html', **ctx)


@app.route('/participants/display/<code>')
def display_participants(code):
    ctx = get_exp_context(code)
    ctx['participants'] = MobileUser.query.filter_by(code=code).all()
    ctx['rescuetime_participants'] = RescuetimeUser.query.filter_by(code=code).all()
    return render_template('experiment/experiment-participants.html', **ctx)


def get_exp_context(code):
    ctx = {
        'user_type': 'researcher',
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'experiment': Experiment.query.filter_by(code=code).first(),
        'protocols': Protocol.query.filter_by(exp_code=code).all(),
        'dashboard_page': True
    }
    ctx['show_pam'] = utils.get_state("pam", ctx['protocols'])
    ctx['show_survey'] = utils.get_state("push_survey", ctx['protocols'])
    return ctx
