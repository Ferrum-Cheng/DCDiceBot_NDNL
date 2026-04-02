from flask import Flask
from threading import Thread
import time
import requests

app = Flask('')
@app.route('/')
def home():
    return "不可以骰骰 is ready"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def ping():
    APP_URL = 'https://bu-ke-yi-tou-tou.onrender.com/'
    INTERVAL = 10 * 60
    while True:
        try:
            response = requests.get(APP_URL)
            print(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}: Pinged {APP_URL} - Status {response.status_code}")
        except Exception as err:
            print(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}: Error pinging {APP_URL}: {err}")
        time.sleep(INTERVAL)