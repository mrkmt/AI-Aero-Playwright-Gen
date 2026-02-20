import requests
import json

try:
    url = "http://127.0.0.1:8000/api/v1/recorder/start"
    payload = {"url": "https://google.com", "session_name": "test-script"}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
