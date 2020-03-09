from __future__ import print_function
from datetime import datetime, timedelta
import re
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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

def read(date):
   service = main()
   results = date + 'の予定'
   dateMax = date + 'T23:59:00+09:00'
   date += 'T00:00:00+09:00'

   events_result = service.events().list(calendarId='73t3ahvdjq4vh3dujgosa13868@group.calendar.google.com', timeMin=date, timeMax=dateMax,
                                       maxResults=10, singleEvents=True, orderBy='startTime').execute()
   events = events_result.get('items', [])

   if not events:
       results += 'は見つかりませんでした。'
       return results
   result = []
   for event in events:
       summary = event.get('summary', '未指定') #イベントタイトル
       start = event['start'].get('dateTime', '終日')
       end = ''
       if start != '終日':
           start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
           start = datetime.strftime(start, '%H:%M')
           end = event['end'].get('dateTime')
           end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
           end = datetime.strftime(end, '%H:%M')
       if start == end or start == '終日':
           start_end = start
       else:
           start_end = start + '-' + end
       location = event.get('location', '未指定')
       result.append('予定:'+summary + ' 時間:' + start_end + ' 場所:' + location)
   results += '\n' + '\n'.join(result)
   return results