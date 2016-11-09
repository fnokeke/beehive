"""
fetches moves app data
"""

import requests
from datetime import date, timedelta
import json


class Moves(object):
    """
    Provide access to fetch user's moves data.
    """

    MOVES_BASE_URL = 'https://api.moves-app.com/api/1.1'
    MOVES_STORYLINE_DAILY = '%s/user/storyline/daily' % MOVES_BASE_URL

    def __init__(self, user_access_token=''):
        self.access_token = user_access_token

    @staticmethod
    def get_stats(access_token, **kwargs):
        results = Moves.get_user_storyline(access_token, **kwargs)
        summary = Moves.summarize(results)
        return summary

    @staticmethod
    def get_user_storyline(access_token, **kwargs):
        """
        Return in text format moves storyline using user's access_token.
        @params: day (single date), begin/end (start and end date)
        """
        if not access_token:
            return '[]'

        bearer = 'Bearer {}'.format(access_token)
        headers = {'Authorization': bearer}

        if kwargs.get('begin') and kwargs.get('end'):
            url = Moves.MOVES_STORYLINE_DAILY
            params = {'from': kwargs['begin'], 'to': kwargs['end']}
        else:
            yesterday = date.today() - timedelta(1)
            yesterday = yesterday.strftime('%Y%m%d')
            day = kwargs.get('day') or yesterday

            url = Moves.MOVES_STORYLINE_DAILY + '/' + day
            params = {}

        r = requests.get(url, headers=headers, params=params)
        return r.text

    @staticmethod
    def summarize(text):
        results = {'calories': 0, 'steps': 0, 'duration': 0}

        rows = json.loads(text)
        if 'error' in rows:
            print 'Error in summarize: {}'.format(rows)
            return results

        for row in rows:
            results['calories'] += row['caloriesIdle']

            if not row['summary']:
                continue

            for summary in row['summary']:
                if summary.get('calories'):
                    results['calories'] += summary['calories']
                    results['steps'] += summary['steps']
                    results['duration'] += summary['duration']

        return results
