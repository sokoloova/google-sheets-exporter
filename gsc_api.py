import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/webmasters.readonly'
]

YM_SCOPES = []
YM_TOKEN = 'your_yandex_metrika_token'
YM_COUNTER_ID = '97987159'

def get_gsc_data(site_url):
    """Получение данных из Google Search Console"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('searchconsole', 'v1', credentials=creds)

    request = {
        'startDate': '7daysAgo',
        'endDate': 'today',
        'dimensions': ['query'],
        'rowLimit': 1000
    }
    return service.searchanalytics().query(siteUrl=site_url, body=request).execute()

def get_yandex_metrika_data(counter_id):
    """Получение данных из Яндекс.Метрики"""
    headers = {
        'Authorization': f'OAuth {YM_TOKEN}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': counter_id,
        'metrics': 'ym:s:visits',
        'dimensions': 'ym:s:date',
        'date1': '7daysAgo',
        'date2': 'today',
        'limit': 1000
    }
    response = requests.get('https://api-metrika.yandex.net/stat/v1/data', headers=headers, params=params)
    return response.json()

def write_to_sheets(gsc_data, ym_data, sheet_name):
    """Запись данных в Google Таблицу"""
    gsheets_creds = ServiceAccountCredentials.from_json_keyfile_name(
        'gsheets_credentials.json', ['https://www.googleapis.com/auth/spreadsheets'])
    gsheets_client = gspread.authorize(gsheets_creds)

    spreadsheet = gsheets_client.open_by_key("12miHXFwV5yVbor-dH3iaDoZKcFzkDLmCHyBqjZ0PTMk")
    sheet = spreadsheet.worksheet(sheet_name)

    sheet.clear()
    sheet.append_row(['Запрос', 'Клики', 'Визиты'])

    for gsc_row in gsc_data.get('rows', []):
        query = gsc_row['keys'][0]
        clicks = gsc_row['clicks']
        for ym_row in ym_data.get('data', []):
            if ym_row['dimensions'][0]['name'] == query:
                visits = ym_row['metrics'][0]
                sheet.append_row([query, clicks, visits])

site_url = 'https://example.com'
gsc_data = get_gsc_data(site_url)

ym_data = get_yandex_metrika_data(YM_COUNTER_ID)

write_to_sheets(gsc_data, ym_data, 'Лист1')
