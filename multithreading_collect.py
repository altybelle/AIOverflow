from core import *
import threading
import time
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.stackexchange.com/2.3/questions"

pause_event = threading.Event()  
lock = threading.Lock()  

def fetch_all_questions_multithread(access_token=None, from_date=None, to_date=None):
    print(f"Iniciando thread {threading.current_thread().name}")
    print(f"Obtendo questões de {from_date} até {to_date}.")

    try:
        fetch_all_questions(access_token=access_token, from_date=from_date, to_date=to_date)
    except Exception as err:
        print(f"Erro na thread {threading.current_thread().name}: {str(err)}.")

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
            print(f"Thread {threading.current_thread().name} aguardando fim do backoff...")
            pause_event.wait()

            params["page"] = page
            response = requests.get(API_URL, params=params)

            if response.status_code == 200:
                data = response.json()

                printf(f"{threading.current_thread().name} - {response.status_code}!")

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
                    pause_event.set()
                    time.sleep(backoff + 1)
                    pause_event.clear()

                if not has_more:
                    print(f"Acabadas páginas do período de {from_date} até {to_date}.")
                    break

                time.sleep(1 / max_requests_per_second)
            else:
                raise Exception(f"Erro ao adquirir dados: {response.status_code} - {response.text}")

if __name__ == "__main__":
    start_date = datetime(2023, 3, 1)
    end_date = datetime(2023, 12, 31)
    access_token = get_token()

    threads = []
    n_threads = 0

    current_start = start_date
    while current_start <= end_date:
        current_end = (current_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)
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

    for thread in threads:
        thread.join()

    print("Todas as threads concluíram.")
