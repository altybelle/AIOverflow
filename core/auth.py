from dotenv import load_dotenv
import requests, json
import os

load_dotenv()

def get_token():
    payload = {
        'code': os.getenv('OAUTH_CODE'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'redirect_uri': os.getenv('REDIRECT_URI'),
    }
    
    response = requests.post('https://stackoverflow.com/oauth/access_token/json', payload)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Error fetching token: {response.status_code} - {response.text}")
        return None