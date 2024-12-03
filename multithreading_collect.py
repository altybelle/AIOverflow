from core import *
from datetime import datetime, timedelta
from dotenv import load_dotenv

import threading
import requests
import json
import time
import os

load_dotenv()

pause_event = threading.Event() 
lock = threading.Lock()

API_URL = "https://api.stackexchange.com/2.3/questions"

def fetch_all_questions_multithread(access_token=None, from_date=None, to_date=None):
    print(f"Iniciando thread {threading.current_thread().name} - de {from_date} até {to_date}.")

    try:
        fetch_all_questions(access_token=access_token, from_date=from_date, to_date=to_date)
    except Exception as err:
        print(f"Uma exceção ocorreu na thread {threading.current_thread().name}: {str(err)}.")

def fetch_all_questions(access_token=None, tags=None, sort="creation", min_score=None, from_date=None, to_date=None, start_page=None):
    obtained_questions = []

    params = {
        "order": "desc",
        "sort": sort,
        "site": "stackoverflow",
        "pagesize": 100,
        "access_token": access_token,
        "key": os.getenv("STACK_APP_KEY"),
    }

    if from_date:
        params["fromdate"] = int(from_date.timestamp())
    if to_date:
        params["todate"] = int(to_date.timestamp())

    has_more = True
    quota_remaining = 10_000
    max_requests_per_second = 28

    page = start_page if start_page else 1

    while has_more and quota_remaining > 0:
        if pause_event.is_set():
            print(f"Thread {threading.current_thread().name} aguardando o fim do backoff...")
            pause_event.wait()

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

            if len(obtained_questions) > 0:
                save_questions(obtained_questions)
                obtained_questions = []

            page += 1

            if "backoff" in data:
                backoff = int(data["backoff"])
                print(f"Backoff detectado: aguardando por {backoff + 1} segundos.")
                pause_event.set()  # Sinaliza pausa para todas as threads
                time.sleep(backoff + 1)
                pause_event.clear()  # Libera as threads após o backoff

            if not has_more:
                print(f"Acabadas páginas do período de {from_date} até {to_date}.")
                break

            if quota_remaining <= 0:
                raise Exception("Cota de requisições excedida. Mude de IP ou aguarde por 24 horas para reutilizar o serviço.")

            time.sleep(1 / max_requests_per_second)
        else:
            raise Exception(f"Falha ao adquirir dados: {response.status_code} - {response.text}")

    return quota_remaining

if __name__ == "__main__":
    start_date = datetime(2023, 3, 1)
    end_date = datetime(2023, 12, 31)
    access_token = get_token()

    threads = []
    n_threads = 0

    current_start = start_date
    while current_start <= end_date:
        current_end = (current_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        if current_end > end_date:
            current_end = end_date

        thread = threading.Thread(
            target=fetch_all_questions_multithread,
            name=f"thread_{n_threads}",
            args=(access_token, current_start, current_end),
        )

        threads.append(thread)
        n_threads += 1

        current_start = current_end + timedelta(days=1)

    for thread in threads:
        thread.start()

    while any(thread.is_alive() for thread in threads):
        if pause_event.is_set():
            print("Parando todas as threads devido ao backoff...")
            time.sleep(1)

    for thread in threads:
        thread.join()

    print("Todas as threads concluídas.")
