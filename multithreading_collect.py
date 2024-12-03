from core import *
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests, json
import time, os
import threading

load_dotenv()

API_URL = "https://api.stackexchange.com/2.3/questions"
condition = threading.Condition()
global_backoff = 0  # Controle de backoff global para todas as threads.

def fetch_questions_for_month(access_token, start_date, end_date):
    global global_backoff
    params = {
        "order": "desc",
        "sort": "creation",
        "site": "stackoverflow",
        "pagesize": 100,
        "access_token": access_token,
        "key": os.getenv('STACK_APP_KEY'),
        "fromdate": int(start_date.timestamp()),
        "todate": int(end_date.timestamp())
    }

    has_more = True
    page = 1
    quota_remaining = 10_000

    while has_more and quota_remaining > 0:
        with condition:
            while global_backoff > 0:
                condition.wait()

        params["page"] = page
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            questions = data.get("items", [])
            question_ids = [question["question_id"] for question in questions if "question_id" in question]

            matching_questions = check_matching_questions(question_ids)
            obtained_questions = [
                question for question in questions if question["question_id"] not in matching_questions
            ]

            has_more = data.get("has_more", False)
            quota_remaining = data.get("quota_remaining", 0)

            print(f'{start_date} de {end_date}. {response.status_code} - Página {page}: {len(obtained_questions)}. Quota remaining: {quota_remaining}.')

            if len(obtained_questions) > 0:
                save_questions(obtained_questions)

            page += 1

            if 'backoff' in data:
                backoff = int(data["backoff"])
                print(f'Backoff detectado: {backoff} segundos. Pausando todas as threads.')
                with condition:
                    global_backoff = backoff
                    condition.notify_all()
                time.sleep(backoff + 1)
                with condition:
                    global_backoff = 0
                    condition.notify_all()

            time.sleep(0.5)

        else:
            print(f"Falha ao adquirir dados: {response.status_code}")
            print(f"Erro: {response.text}")
            break

def main():
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    access_token = get_token()

    current_start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    threads = []

    while current_start <= end_date:
        current_end = (current_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)

        if current_end > end_date:
            current_end = end_date.replace(hour=23, minute=59, second=59)

        print(f'Criando thread para o período de {current_start} até {current_end}.')
        thread = threading.Thread(target=fetch_questions_for_month, args=(access_token, current_start, current_end))
        threads.append(thread)

        current_start = current_end + timedelta(days=1)
        current_start = current_start.replace(hour=0, minute=0, second=0, microsecond=0)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
