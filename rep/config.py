"""
config settings for flask app
"""

from rep import secret_keys

###################
# app settings
###################
SECRET_KEY = secret_keys.SECRET_KEY
SESSION_TYPE = 'redis'
SQLALCHEMY_DATABASE_URI = secret_keys.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

###################
# google config
###################
GOOGLE_CLIENT_ID = secret_keys.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = secret_keys.GOOGLE_CLIENT_SECRET
BASE_SCOPE = 'https://www.googleapis.com/auth'
GOOGLE_SCOPE = '{}/userinfo.email {}/calendar.readonly {}/calendar'.format(BASE_SCOPE, BASE_SCOPE, BASE_SCOPE)
GOOGLE_SCOPE_RESEARCHER = '{}/userinfo.email'.format(BASE_SCOPE)
GOOGLE_SCOPE_PARTICIPANT = '{}/userinfo.email'.format(BASE_SCOPE)

###################
# celery app config
###################
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
# because apparently everything else is insecure :|
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

###################
# MOVES
###################
MOVES_ACCESS_TOKEN_URL = 'https://api.moves-app.com/oauth/v1/access_token?grant_type=authorization_code&code='
MOVES_CLIENT_ID = secret_keys.MOVES_CLIENT_ID
MOVES_CLIENT_SECRET = secret_keys.MOVES_CLIENT_SECRET
MOVES_SCOPE = 'location activity'
MOVES_WEB_URL = 'https://api.moves-app.com/oauth/v1/authorize?response_type=code'

MOVES_BASE_URL = 'https://api.moves-app.com/api/1.1'
MOVES_CHECK_TOKEN_URL = 'https://api.moves-app.com/oauth/v1/tokeninfo?access_token='
MOVES_DAILY_SUMMARY = '%s/user/summary/daily/' % MOVES_BASE_URL
MOVES_STORYLINE_DAILY = '%s/user/storyline/daily/' % MOVES_BASE_URL
MOVES_PLACE_SUMMARY = '%s/user/places/daily/' % MOVES_BASE_URL
# MOVES_REDIRECT_URI = 'http://slm.smalldata.io/auth-moves'
MOVES_REDIRECT_URI = 'http://localhost:5000/auth-moves'
MOVES_REFRESH_TOKEN_URL = 'https://api.moves-app.com/oauth/v1/access_token?grant_type=refresh_token'

###################
# MTURK MOVES
###################
MTURK_MOVES_CLIENT_ID = secret_keys.MTURK_MOVES_CLIENT_ID
MTURK_MOVES_CLIENT_SECRET = secret_keys.MTURK_MOVES_CLIENT_SECRET
MTURK_MOVES_REDIRECT_URI = 'http://localhost:5000/mturk-auth-moves'


###################
# RESCUETIME
###################
RT_CLIENT_ID = secret_keys.RT_CLIENT_ID
RT_CLIENT_SECRET = secret_keys.RT_CLIENT_SECRET
RT_BASE_URL = 'https://www.rescuetime.com/oauth/authorize?client_id=' + RT_CLIENT_ID

# CONSTANTS
LOCATION = 'Location (SLM)'
MOOD = 'Mood (SLM)'
SN = 'Social-Networks (SLM)'

# FILE UPLOADS
UPLOADED_PHOTOS_DEST = secret_keys.UPLOAD_FOLDER
