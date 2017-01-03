"""
fetches RescueTimePAM data
"""

import requests
import json


class RescueOauth2(object):
    """
    Provide oauth2 access

    The following scopes are currently supported:
        time_data: Access activity history and summary time data for the authorizing user
        category_data: Access how much time the authorizing user spent in specific categories
        productivity_data: Access how much time the authorizing user spent in different productivity levels
        alert_data: Access the authorizing user's alert history
        highlight_data: Read from and post to the authorizing user's daily highlights list
        focustime_data: Access the authorizing user's FocusTime history and control their FocusTime sessions
    """

    app_id = 'de68608c52e71e5f3669b53afdf1e26a1d460bb83f0ac736382c525b2e5dbe37'
    app_secret = '4a8a8623c5a650e63562ec971f9d8e968280853bc92334e8f81591f6c74b4635'
    base_url = 'https://www.rescuetime.com/oauth/authorize?client_id=' + app_id
    redirect_url = 'https://slm.smalldata.io'
    scope = 'time_data category_data productivity_data alert_data highlight_data focustime_data'
    auth_url = '%(base_url)s&redirect_uri=%(redirect_url)s&response_type=code&scope=%(scope)s' % {
        'base_url': base_url,
        'redirect_url': redirect_url,
        'scope': scope
    }
    access_token_url = 'https://www.rescuetime.com/oauth/token'

    def fetch_access_token(self, code):
        if not code:
            raise ValueError("Invalid request code in set_access_token")

        data = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_url
        }

        r = requests.post(self.access_token_url, data=data)
        if r.status_code == 200:
            results = json.loads(r.text)
            return results['access_token']


class RescueTime(object):
    """
    Provide access to fetch user's RescueTime data.
    """

    def __init__(self, access_token):
        self.access_token = access_token

    def fetch_all_feeds(self):
        """
        Return RescueTime data for given date
        """
        if not self.access_token:
            return '[]'

        daily_feed_url = 'https://www.rescuetime.com/api/oauth/daily_summary_feed'
        params = {'access_token': self.access_token}
        r = requests.get(daily_feed_url, params=params)
        return r.text

    def get_feed_by_date(self, date):
        """
        Returns rescuetime stats for given date
        date: yyyy-mm-dd
        """
        summary = {
            'date': date,
            'productivity_pulse': 'no time',
            #
            'social_networking_duration_formatted': 'no time',
            'social_networking_hours': 'no time',
            'social_networking_percentage': 'no time',
            #
            'software_development_duration_formatted': 'no time',
            'software_development_hours': 'no time',
            'software_development_percentage': 'no time',
            #
            'all_distracting_duration_formatted': 'no time',
            'all_distracting_hours': 'no time',
            'all_distracting_percentage': 'no time',
            #
            'all_productive_duration_formatted': 'no time',
            'all_productive_hours': 'no time',
            'all_productive_percentage': 'no time'
        }

        results = json.loads(self.fetch_all_feeds())
        for row in results:
            if row['date'] == date:

                for key in summary:
                    summary[key] = row[key]
                break

        return json.dumps(summary)

    @staticmethod
    def fetch_intv_feed(access_token, date):
        rt = RescueTime(access_token)
        json_result = rt.get_feed_by_date(date)
        return {'rt_feed': json_result}
