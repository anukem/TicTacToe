import requests
import time
import json
params = {"ts": time.time(), "name" : "John Anukem"}
r = requests.post('http://2564cb9d.ngrok.io/index', data=params)
print r.status_code
print r.content
