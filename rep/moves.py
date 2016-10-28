"""
fetches moves app data
"""

import requests


class Moves(object):
    """
    Provide access to fetch user's moves data.
    """

    MOVES_BASE_URL = 'https://api.moves-app.com/api/1.1'
    MOVES_DAILY_SUMMARY = '%s/user/summary/daily/' % MOVES_BASE_URL
    MOVES_STORYLINE_DAILY = '%s/user/storyline/daily/' % MOVES_BASE_URL
    MOVES_PLACE_SUMMARY = '%s/user/places/daily/' % MOVES_BASE_URL

    def __init__(self, user_access_token):
        self.access_token = user_access_token

    def get_moves_storyline(self, date):
        """
        Return in text format moves storyline for given date.
        """
        if not self.access_token:
            return '[]'

        url = self.MOVES_STORYLINE_DAILY + date
        bearer = 'Bearer {}'.format(self.access_token)
        headers = {'Authorization': bearer}

        r = requests.get(url, headers=headers)
        return r.text
