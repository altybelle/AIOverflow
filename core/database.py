from pymongo import MongoClient
from dotenv import load_dotenv

import os

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)

db = client['tp1_ccf492']
collection = db['questions']

def check_matching_questions(question_ids):
    found_questions = collection.find({ "question_id": { "$in": question_ids }}, { "question_id": 1})
    found_ids = [ question["question_id" ] for question in found_questions ]
    return found_ids

def save_questions(questions):
    collection.insert_many(questions)