"""
rep views for flask application
"""

from rep.utils import ReverseProxied

from flask import Flask
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config.from_pyfile('config.py')

login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category = 'warning'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, (photos,))

import rep.views
import rep.models
