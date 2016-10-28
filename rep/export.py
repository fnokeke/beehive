"""
export data
"""

from rep import app
from rep.moves import Moves
from rep.pam import PAM
from rep.rescuetime import RescueTime
from rep.gcal import Calendar, EventFactory


def to_cal(calname, access_token, date, credentials=None):
    events = []

    if calname == app.config['LOCATION']:
        moves = Moves(access_token)
        results = moves.get_moves_storyline(date)
        events = EventFactory.from_moves(results, date)

    elif calname == app.config['MOOD']:
        pam = PAM(access_token)
        results = pam.get_data(date)
        events = EventFactory.from_pam(results, date)

    elif calname == app.config['SN']:
        rt = RescueTime(access_token)
        results = rt.get_feed_by_date(date)
        events = EventFactory.from_rescuetime(results, date)

    cal = Calendar(calname, credentials)
    resp = cal.insert_event(events)
    return resp
