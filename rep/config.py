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
MOVES_CLIENT_ID = 'qQtk83byVv8v9imPbmXgNLnUwsLx3bRI'
MOVES_CLIENT_SECRET = 'J36mH_2HS990fRT6aIKRB8824w_0Xb7jy_a9fnrl_7vCM0UuQt5gXB3V3EpCApYk'
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
# PAM
###################
PAM_CLIENT_ID = 'io.smalldata.slm'
PAM_CLIENT_SECRET = 'fr2fedsvfQW9Aa7GQtB^CDSn6mf&dY'
PAM_DSU = 'https://ohmage-omh.smalldata.io/dsu'
PAM_ACCESS_TOKEN_URL = PAM_DSU + '/oauth/token?grant_type=authorization_code&code='

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
