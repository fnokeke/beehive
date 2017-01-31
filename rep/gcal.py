"""
Calendar operations for adding multiple datastreams to their respective calendars
e.g. location, emotion(PAM)
"""

from flask_login import current_user
from oauth2client import client
from apiclient import discovery

import httplib2
import json


class CalendarService(object):
    """
    Provide calendar service for Google calendar operations
    """

    @staticmethod
    def create_service(credentials):
        """ Returns google service using given google_credentials or flask.current_user google_credentials"""
        google_credentials = client.OAuth2Credentials.from_json(credentials)
        http = httplib2.Http()
        if google_credentials.access_token_expired:
            google_credentials.refresh(http)

        http_auth = google_credentials.authorize(http)
        service = discovery.build('calendar', 'v3', http=http_auth)
        return service

    @staticmethod
    def fetch_id(calname, service):
        """ Returns cal_id if calendar name exists else create new calendar and return the id. """
        calendar_list = service.calendarList().list().execute()
        for cal in calendar_list['items']:
            if cal['summary'] == calname:
                return cal['id']

        new_cal_info = {'summary': calname}
        created_calendar = service.calendars().insert(body=new_cal_info).execute()
        return created_calendar['id']


class Calendar(object):
    """
    Perform Google Calendar Operations
    """

    def __init__(self, calname, cal_id=None, credentials=None):
        self.service = CalendarService.create_service(credentials or current_user.google_credentials)
        self.cal_id = cal_id or CalendarService.fetch_id(calname, self.service)
        self.calname = calname

    def get_all_events(self, date):
        tmin = '{}T00:00:00-00:00'.format(date)
        tmax = '{}T23:59:59-00:00'.format(date)
        filtered_events = self.service.events().list(calendarId=self.cal_id, timeMin=tmin, timeMax=tmax).execute()
        stored_events = []
        for ev in filtered_events['items']:
            if self.is_same_date(ev['start'], ev['end'], tmin):
                stored_events.append(ev)

        return filtered_events['items']

    def is_same_date(self, start, end, tmin):
        if start.get('dateTime'):
            startTime = start['dateTime']
            endTime = end['dateTime']
            return True
        else:
            return True

    def insert_event(self, events):
        """
        desc:         insert list of events into calendar
        event (list): list of events(list of json)
        return (str): response from inserting event
        """
        resp = self.batch('insert', events)
        return resp

    def batch(self, op, items):
        """
        desc:         perform calendar operation in batch mode
        op (str):     calendar operation e.g. insert, delete
        items (list): list of item [json format for insert/ event_id for event_id / cal_id for calendar event)
                      e.g. event_id: [{'start': {'date': u'2016-10-18'}, 'end': {'date': u'2016-10-18'}, 'summary': '11:25:00 secs: 245,55'}
                      NB: start.date/end.date could be replaced with start.dateTime/end.dateTime
        """
        if op == 'insert':  # remove any event on given dates before batch inserting new ones
            event_dates = [x['start'].get('date') or x['start']['dateTime'].split('T')[0] for x in items]
            event_dates = set(event_dates)
            self.delete_event_by_date(event_dates)

        batch_request = self.service.new_batch_http_request()
        for item in items:
            ev = None

            if op == 'insert':
                ev = self.service.events().insert(calendarId=self.cal_id, body=item)
                print 'item: {}'.format(item)

            elif op == 'delete':
                ev = self.service.events().delete(calendarId=self.cal_id, eventId=item)

            elif op == 'delete-calendar':
                ev = self.service.calendars().delete(calendarId=item)

            batch_request.add(ev)

        resp = batch_request.execute(http=httplib2.Http())
        return resp or 'successfully inserted {} event(s).'.format(len(items))

    def reset_calendar(self):
        all_events = self.service.events().list(calendarId=self.cal_id).execute()
        ids_to_delete = [x['id'] for x in all_events['items']]
        resp = self.batch('delete', ids_to_delete)
        return resp

    def delete_calendar(self):
        """Recursively delete any calendar with current calname. """
        calendar_list = self.service.calendarList().list().execute()
        ids_to_delete = set()

        for cal in calendar_list['items']:
            if cal['summary'].lower() == self.calname.lower():
                ids_to_delete.add(cal['id'])

        resp = self.batch('delete-calendar', ids_to_delete)
        self.calname, self.cal_id = None, None
        return resp

    def delete_event_by_date(self, event_dates):
        """
        desc:                        delete all events that occur on their start date
        event_dates (list of str):   event date(YYYY-mm-dd)
        return (str):                response from delete
        """
        ids_to_delete = []
        for date in event_dates:
            tmin = '{}T00:00:00-00:00'.format(date)
            tmax = '{}T23:59:59-00:00'.format(date)
            stored_events = self.service.events().list(calendarId=self.cal_id, timeMin=tmin, timeMax=tmax).execute()
            ids = [x['id'] for x in stored_events['items']]
            ids_to_delete.extend(ids)

        resp = self.batch('delete', ids_to_delete)
        return resp


class EventFactory(object):
    """
    Create events for different services
    """

    @classmethod
    def from_moves(cls, results, date):
        json_results = json.loads(results)
        events = []

        for row in json_results:
            if row['segments']:
                segments = row['segments']
                events = cls.segments_to_events(segments)
        return events

    @classmethod
    def segments_to_events(cls, segments):
        events = []

        for seg in segments:
            if seg['type'] == 'place':
                place_name = seg['place'].get('name', 'No Place Label')
                ev = {'summary': place_name,
                      'start': {'dateTime': cls.to_cal_date(seg['startTime'])},
                      'end': {'dateTime': cls.to_cal_date(seg['endTime'])}}
                events.append(ev)

        return events

    @classmethod
    def to_cal_date(cls, movesdate):
        yr, mo, day, = movesdate[:4], movesdate[4:6], movesdate[6:8]
        hr, mins, secs = movesdate[9:11], movesdate[11:13], movesdate[13:15]
        tz1, tz2 = movesdate[16:18], movesdate[18:]
        date = '{}-{}-{}T{}:{}:{}-{}:{}'.format(yr, mo, day, hr, mins, secs, tz1, tz2)
        return date

    @classmethod
    def from_pam(cls, results, date):
        json_results = json.loads(results)
        assert 'error' not in json_results, 'PAM error: {}'.format(json_results)

        events = []
        for row in json_results:
            summary = 'Mood: {}'.format(row['body']['mood'])
            ev = {'summary': summary, 'start': {'date': date}, 'end': {'date': date}}
            events.append(ev)
        return events

    @classmethod
    def from_rescuetime(cls, results, date):
        """
        convert results (str) to calendar event (json)
        return: list of events (event: {summary: val, start: '', end: ''})
        """
        results = json.loads(results)
        events = []
        for key, value in results.iteritems():
            summary = '{}: {}'.format(key, value)
            ev = {'summary': summary, 'start': {'date': date}, 'end': {'date': date}}
            events.append(ev)
        return events
