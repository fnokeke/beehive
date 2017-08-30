# change file name to secret_keys.py

import os

SECRET_KEY = 'repsecret'
SQLALCHEMY_DATABASE_URI = 'postgresql://repadmin:reppassword@localhost/repdb'

###################
# google config
###################
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''

###################
# moves config
###################
MOVES_CLIENT_ID = ''
MOVES_CLIENT_SECRET = ''

###################
# mturk moves config
###################
MTURK_MOVES_CLIENT_ID = ''
MTURK_MOVES_CLIENT_SECRET = ''

###################
# PAM config
###################
PAM_CLIENT_ID = ''
PAM_CLIENT_SECRET = ''

###################
# RescueTime config
###################
RT_CLIENT_ID = ''
RT_CLIENT_SECRET = ''
RT_CLIENT_ID = ''

###################
# Firebase Key
###################
FIREBASE_KEY = ''

######################################
# Researcher Username
######################################
RESEARCHER_USERNAME = 'researcher'
RESEARCHER_PASSWORD = 'password'


######################################
# FILE UPLOADS
######################################
CUR_DIR = os.getcwd()
UPLOAD_FOLDER = '{}/uploads/'.format(CUR_DIR)
