from .fetch import fetch_questions_for_month
from .database import save_questions, check_matching_questions
from .logger import log
from concurrent.futures import ThreadPoolExecutor

import time, logging

def filter_questions(questions):
    fetch_ids = [ q['question_id'] for q in questions.get('items', [])]
    existing_ids = check_matching_questions(fetch_ids)
    return [ q for q in questions.get('items', []) if q['question_id'] not in existing_ids ]

def sequential(access_token, intervals, initial_page):
    max_requests_per_second = 27
    page = initial_page
    exclusion = []

    while len(exclusion) < len(intervals):
        for index, interval in enumerate(intervals):
            if index not in exclusion:
                start_date, end_date = interval['start_date'], interval['end_date']

                log(f'Requesting questions from {start_date} to {end_date}, page = {page}.', level=logging.INFO)
                response = fetch_questions_for_month(access_token, start_date, end_date, page)

                questions = filter_questions(response)

                if len(questions) > 0:
                    save_questions(questions)
                    log(f'{len(questions)} registered in the database.', level=logging.INFO)
                else:
                    log(f'Requested questions from {start_date} to {end_date} - No questions acquired.', level=logging.INFO)

                if response['quota_remaining'] == 0:
                    log(f'Reached end of quota.', level=logging.WARN)
                    return

                if response.get('has_more') == False:
                    log(f'Questions from {start_date} to {end_date} ended. Adding index {index} to exclusion list.', level=logging.WARN)
                    exclusion.append(index)

                if 'backoff' in response:
                    log(f'Received backoff of {response["backoff"]} seconds.', level=logging.WARN)
                    time.sleep(response['backoff'] + 1)

            time.sleep(1 / max_requests_per_second)
        page += 1

    log("All intervals have been processed.", level=logging.INFO)

def multithreading(access_token, intervals, initial_page):
    tasks = []
    with ThreadPoolExecutor(max_workers=12) as tpe:
        tasks.append(tpe.submit())

    return 0

