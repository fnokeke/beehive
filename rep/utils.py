"""
utility functions
"""

from functools import wraps
from flask import request, Response
import secret_keys
import json
from datetime import datetime


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.
    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }
    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

# ================================================
# = basic auth view wrapper below
# ================================================


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == secret_keys.RESEARCHER_USERNAME and password == secret_keys.RESEARCHER_PASSWORD


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_basic_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def to_json(param):
    if not param: return {}
    return json.loads(str(param))


def to_json_list(param):
    if not param: return []
    return [to_json(p) for p in param]


def to_datetime(date_str, fmt=None):
    if not date_str or date_str == "": 
        return None
    if not fmt:
        fmt = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_str, fmt)


def get_state(method, protocols):
    state = False
    for p in protocols:
        if p.method == method:
            state = True
            break
    return state


