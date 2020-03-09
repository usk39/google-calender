from __future__ import print_function
from datetime import datetime, timedelta
import re
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def extract_words(str):
   m = re.match('(.+)\n(.*)\n(\d{8})\n(\d{4})\n(\d{4})', str)
   if m is None:
       return
   mg = list(m.groups())
   mg[3] = mg[2] + " " + mg[3]
   mg[4] = mg[2] + " " + mg[4]
   mg.pop(2)
   return mg

def write(title, location, start, end):
   if start[4:] == '0000' and end[4:] == '2400':
       start = datetime.strptime(start[:8], '%Y%m%d')
       start = datetime.strftime(start, '%Y-%m-%d')
       end = datetime.strptime(end[:8], '%Y%m%d')
       end = datetime.strftime(end, '%Y-%m-%d')
       event = {
           'summary': title,
           'location': location,
           'start': {
               'date': start
           },
           'end': {
               'date': end
           }
       }
   else:
       start = datetime.strptime(start, '%Y%m%d %H%M')
       start = datetime.strftime(start, '%Y-%m-%dT%H:%M:%S+09:00')
       try:
           end = datetime.strptime(end, '%Y%m%d %H%M')
           end = datetime.strftime(end, '%Y-%m-%dT%H:%M:%S+09:00')
       except ValueError: #24時の場合は翌日の0時に変換
           end = datetime.strptime(end[:8], '%Y%m%d')
           end = end + timedelta(days=1)
           end = datetime.strftime(end, '%Y-%m-%dT00:00:00+09:00')
       event = {
           'summary': title,
           'location': location,
           'start': {
               'dateTime': start
           },
           'end': {
               'dateTime': end
           }
       }
   service = main()
   event = service.events().insert(calendarId='73t3ahvdjq4vh3dujgosa13868@group.calendar.google.com', body=event).execute()
   msg = event.get('htmlLink')
   return msg