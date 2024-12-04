from core import Staget_token, save_questions, check_matching_questions, logger
from dotenv import load_dotenv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import requests
import time
import os
import threading

load_dotenv()
state = StateManager()

def fetch_questions_for_month(access_token, start_date, end_date):
    session = requests.Session()
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
    page = 787

    while has_more:
        state.wait_for_backoff()
        if not state.has_quota():
            log(f"Quota esgotada. Encerrando processamento para {start_date} - {end_date}.", logging.WARNING)
            break

        params["page"] = page
        response = session.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            process_response(data, start_date, end_date, page)
            has_more = data.get("has_more", False)
            page += 1
        else:
            log(f"Erro ao buscar dados: {response.status_code} - {response.text}", logging.ERROR)
            break

        time.sleep(3)

def process_response(data, start_date, end_date, page):
    questions = data.get("items", [])
    question_ids = [q["question_id"] for q in questions if "question_id" in q]

    matching_questions = check_matching_questions(question_ids)
    obtained_questions = [q for q in questions if q["question_id"] not in matching_questions]

    if obtained_questions:
        save_questions(obtained_questions)

    log(f'[{start_date} - {end_date}] Página {page}: {len(obtained_questions)} perguntas salvas.')

    state.update_quota(data.get("quota_remaining", state.quota_remaining))
    log(f"Quota restante: {state.quota_remaining}.")

    if 'backoff' in data:
        backoff_time = int(data["backoff"])
        log(f"Backoff detectado: {backoff_time} segundos.", logging.WARNING)
        state.update_backoff(backoff_time)
        time.sleep(backoff_time + 1)
        state.update_backoff(0)

def main():
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    access_token = os.getenv("STACK_ACCESS_TOKEN")

    current_start = start_date
    tasks = []

    with ThreadPoolExecutor(max_workers=12) as executor:

        # FIXME: This is generating wrong dates
        while current_start <= end_date:
            current_end = (current_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)
            if current_end > end_date:
                current_end = end_date

            log(f"Criando tarefa para {current_start} até {current_end}.")
            tasks.append(executor.submit(fetch_questions_for_month, access_token, current_start, current_end))
            current_start = current_end + timedelta(days=1)

        for task in tasks:
            task.result()

if __name__ == "__main__":
    main()
