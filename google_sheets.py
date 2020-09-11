import csv
import logging

import os.path
import pickle
from datetime import date

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime


def get_current_UTC_date():
    t = datetime.datetime.utcnow()
    return datetime.datetime(t.year, t.month, t.day, 0, 0, 0, 0)


def get_current_date():
    return date.today().strftime('%Y-%m-%d')


def get_current_month():
    return date.today().strftime('%Y-%m')


def get_last_12_months_UTC():
    t = datetime.datetime.utcnow()
    datetime.datetime(t.year - 1, t.month, 1, 0, 0, 0, 0)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def harvest_sheet_tsv_http(path, name, url, range_name, columns):
    """
    Generic function to read google spreadsheet
    :param path: path to write to
    :param name: filename
    :param url: Google Sheet URL, treated as secret.
    :param range_name: range to import
    :param columns: column number in array to import or use []
    :return: <nothing>
    """
    return


def harvest_sheet_tsv(path, name, sheet_id, range_name, columns):
    """
    Generic function to read google spreadsheet
    :param path: path to write to
    :param name: filename
    :param sheet_id: Google Sheet ID
    :param range_name: range to import
    :param columns: column number in array to import or use []
    :return: <nothing>
    """

    logging.info('Harvesting google sheet %s' % name)
    path_and_metric_file = path + name + ".tsv"

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

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=range_name).execute()
    values = result.get('values', [])
    if not values:
        logging.warning('No data found.')
    else:

        with open(path_and_metric_file, 'w') as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            for row in values:
                row_to_write = []

                if not columns:  # import all:
                    for c in range(0, len(row)):
                        row_to_write.append(row[c])
                else:
                    for c in columns:
                        if c < len(row):
                            row_to_write.append(row[c])
                writer.writerow(row_to_write)
