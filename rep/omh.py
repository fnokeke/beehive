"""
Connects to Ohmage OMH and fetches PAM data
"""

import requests
import base64
import json
from rep import secret_keys


class OMHOauth(object):
    """
    Provide PAM oauth connection
    """
    CLIENT_ID = secret_keys.OMH_CLIENT_ID
    CLIENT_SECRET = secret_keys.OMH_CLIENT_SECRET
    DSU = 'https://ohmage-omh.smalldata.io/dsu'

    AUTH_CODE_URL = DSU + '/oauth/authorize?client_id={}&response_type=code'.format(CLIENT_ID)
    ACCESS_TOKEN_URL = DSU + '/oauth/token?grant_type=authorization_code&code='
    AUTH = base64.b64encode(CLIENT_ID + ":" + CLIENT_SECRET)
    HEADERS = {'Authorization': 'Basic {}'.format(AUTH)}

    def get_tokens(self, code):
        url = self.ACCESS_TOKEN_URL + code
        r = requests.post(url, headers=self.HEADERS)

        if r.status_code != 200:
            print 'PAM connection failed: {}'.format(r.text)
            return None, None
        else:
            results = json.loads(r.text)
            return results['access_token'], results['refresh_token']

    def is_valid(self, token):
        url = '{}/oauth/check_token?token={}'.format(self.DSU, token)
        r = requests.get(url)

        if r.status_code == 200:
            results = json.loads(r.text)
            if 'client_id' in results:
                return True
        return False

    def refresh_token(self, refresh_token):
        url = '{}/oauth/token?grant_type=refresh_token&refresh_token={}'.format(self.DSU, refresh_token)
        r = requests.post(url, headers=self.HEADERS)
        if r.status_code == 200:
            results = json.loads(r.text)
            if not 'error' in results:
                return results['access_token'], results['refresh_token']

        return None, None


class PAM(object):
    """
    Provide access to fetch user's pam data.
    """

    DSU = 'https://ohmage-omh.smalldata.io/dsu'
    SCHEMA = {'schema_namespace': "cornell", 'schema_name': "photographic-affect-meter-scores", 'schema_version': "1.0"}

    def __init__(self, access_token=None, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def validate_tokens(self):
        if not (self.access_token and self.refresh_token):
            return

        pam_oauth = OMHOauth()
        if not pam_oauth.is_valid(self.access_token):
            self.access_token, self.refresh_token = pam_oauth.refresh_token(self.refresh_token)

    def get_data(self, date):
        """
        Return PAM data for given date
        """
        self.validate_tokens()

        if not self.access_token:
            return '[]'

        bearer = 'Bearer {}'.format(self.access_token)
        headers = {'Authorization': bearer}

        tmin = '{}T00:00:00.000-04:00'.format(date)
        tmax = '{}T23:59:59.999-04:00'.format(date)
        params = {'created_on_or_after': tmin, 'created_before': tmax}

        for key, value in self.SCHEMA.iteritems():
            params[key] = value

        url = self.DSU + '/dataPoints'
        r = requests.get(url, headers=headers, params=params)
        return r.text
