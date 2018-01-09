from rep import app
from flask import render_template, request, Response

import json

from rep.models import Experiment_v2, ProtocolPushNotif
from rep.utils import to_json


@app.route('/mobile/fetchstudy', methods=["POST"])
def fetch_study():
    data = json.loads(request.data) if request.data else request.form.to_dict()
    code = data.get('code')
    experiment = Experiment_v2.query.filter_by(code=code).first()
    protocols = ProtocolPushNotif.query.filter_by(exp_code=code).all()  # FIXME: consistent using exp_code or code for models
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

