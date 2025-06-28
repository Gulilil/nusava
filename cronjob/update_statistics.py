import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Try get current user_id
user_id = None
try:
  url = f"{os.getenv('LLM_URL')}/status"
  headers = {}
  response = requests.request("GET", url, headers=headers)
  if (response.status_code == 200):
    status_data = response.json()["response"]
    user_id = status_data["user"]["user_id"]
    username = status_data["user"]["username"]
    print(f"[GET CURRENT USER ID] Current user id: {user_id} under username: {username}")
  else:
    print(f"[FAILED GET CURRENT USER ID] Failed getting current user id. Status code: {response.status_code}. Response: {response.text}")

except Exception as e:
  print(f"[FAILED GET CURRENT USER ID] Failed getting current user id: {e}")

# Update statistics
if (user_id):
  try:
    url = f"{os.getenv('AUTOMATION_URL')}/api/stats/update/"
    payload = json.dumps({
      "user_id": user_id
    })
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    if (response.status_code == 200):
      print(f"[UPDATE STATISTICS] Response: {response.text}")
    else:
      print(f"[FAILED UPDATE STATISTICS] Failed doing update statistics. Status code: {response.status_code}. Response: {response.text}")

  except Exception as e:
    print(f"[FAILED UPDATE STATISTICS] Failed doing update statistics: {e}")