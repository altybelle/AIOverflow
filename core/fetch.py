from .logger import log

import requests, os, logging
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('API_URL')

def fetch_questions_for_month(access_token, start_date, end_date, page):
    session = requests.Session()
    params = {
        'order': 'desc',
        'sort': 'creation',
        'site': 'stackoverflow',
        'pagesize': 100,
        'access_token': access_token,
        'key': os.getenv('STACK_APP_KEY'),
        'fromdate': int(start_date.timestamp()),
        'todate': int(end_date.timestamp()),
        'page': page
    }

    response = session.get(API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        log(f'Error while trying to fetch data: {response.status_code} - {response.text}', logging.ERROR)
        return None