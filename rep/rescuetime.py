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
        print '**********************'
        print r.text
        print '**********************'
        if r.status_code == 200:
            results = json.loads(r.text)
            return results['access_token']


class RescueTime(object):
    """
    Provide access to fetch user's RescueTime data.
    """

    @staticmethod
    def fetch_all_summary(access_token):
        """
        The Daily Summary Feed API returns an array of JSON for each day logged by the user in the previous two weeks.
        It does not include the current day, and new summaries for the previous day are available at 12:01 am in the user's local time zone.
        """
        if not access_token: return '[]'
        daily_feed_url = 'https://www.rescuetime.com/api/oauth/daily_summary_feed'
        params = {'access_token': access_token}
        r = requests.get(daily_feed_url, params=params)
        return r.text

    @staticmethod
    def get_default_summary(date):
        return {
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

    @staticmethod
    def fetch_summary(access_token, date):
        """
        Returns rescuetime stats for given date
        date: yyyy-mm-dd
        """
        summary = RescueTime.get_default_summary(date)
        all_summary = json.loads(RescueTime.fetch_all_summary(access_token))
        for row in all_summary:
            if row['date'] == date:
                for key in summary:
                    summary[key] = row[key]
                break
        return json.dumps(summary)

    @staticmethod
    def fetch_activity(access_token, date):
        """ Can fetch current activities from RescueTime server (updated every 5 mins by RescueTime) """
        if not access_token: return '[]'
        activity_url = 'https://www.rescuetime.com/api/oauth/data'
        params = {
            'access_token': access_token,
            'restrict_begin': date,
            'restrict_end': date,
            'perspective': 'interval',
            'restrict_kind': 'activity',
            'interval': 'hour',
            'format': 'json',
            'resolution_time': 'minute'
        }
        r = requests.get(activity_url, params=params)
        return r.text

    # data resolution/interval is hour.
    @staticmethod
    def fetch_daily_activity(access_token, date):
        """ Can fetch daily activities from RescueTime server """
        if not access_token: return '[]'
        activity_url = 'https://www.rescuetime.com/api/oauth/data'
        params = {
            'access_token': access_token,
            'restrict_begin': date,
            'restrict_end': date,
            'perspective': 'rank',
            'restrict_kind': 'activity',
            'interval': 'day',
            'format': 'json'
        }
        r = requests.get(activity_url, params=params)
        return r.text
