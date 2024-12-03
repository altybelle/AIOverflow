from core import *

from dotenv import load_dotenv
from datetime import datetime, timedelta

import requests, json
import time, os

load_dotenv()

API_URL = "https://api.stackexchange.com/2.3/questions"

def fetch_all_questions(tags=None, sort="creation", min_score=None, from_date=None, to_date=None, start_page=None):
    obtained_questions = []
    params = {
        "order": "desc",
        "sort": sort,
        "site": "stackoverflow",
        "pagesize": 100,
        "access_token": get_token(),
        "key": os.getenv('STACK_APP_KEY'),
    }

    if tags:
        params["tagged"] = ";".join(tags)
    if min_score is not None:
        params["min"] = min_score
    if from_date:
        params["fromdate"] = int(from_date.timestamp())
    if to_date:
        params["todate"] = int(to_date.timestamp())

    has_more = True
    quota_remaining = 10_000 
    max_requests_per_second = 28

    page = start_page if start_page else 1

    while has_more and quota_remaining > 0:
        params["page"] = page
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            
            questions = data.get("items", [])
            question_ids = [ question["question_id"] for question in questions if "question_id" in question ]

            matching_questions = check_matching_questions(question_ids)

            obtained_questions = [
                question for question in questions if question["question_id"] not in matching_questions
            ]

            has_more = data.get("has_more", False)
            quota_remaining = data.get("quota_remaining", 0)

            if len(obtained_questions) > 0:
                save_questions(obtained_questions)
                obtained_questions = []
            
            page += 1

            if 'backoff' in data:
                backoff = int(data["backoff"])
                print(f'Aguardando por {backoff + 1} segundos.')
                time.sleep(backoff + 1)

            if not has_more or quota_remaining <= 0:
                break
            
            time.sleep(1 / max_requests_per_second)
        else:
            print(f"Falha ao adquirir dados: {response.status_code}")
            print(f"Erro: {response.text}")
            break

    return quota_remaining

if __name__ == '__main__':
    start_date = datetime(2023, 3, 1)  
    end_date = datetime(2023, 12, 31)  
    current_start = start_date

    while current_start < end_date:
        current_end = (current_start + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        
        if current_end > end_date:
            current_end = end_date

        print(f'Obtendo questões de {current_start} até {current_end}:')
        quota_remaining = fetch_all_questions(from_date=current_start, to_date=current_end)
        
        if quota_remaining > 0:
            current_start = current_end + timedelta(seconds=1)
        else: 
            break
