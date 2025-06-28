import requests
import os
from dotenv import load_dotenv
load_dotenv()

try:
  url = f"{os.getenv('LLM_URL')}/check_schedule"
  payload = ""
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  if (response.status_code == 200):
    print(f"[CHECK SCHEDULE] Response: {response.text}")
  else:
    print(f"[FAILED CHECK SCHEDULE] Failed doing check schedule. Status code: {response.status_code}. Response: {response.text}")

except Exception as e:
  print(f"[FAILED CHECK SCHEDULE] Failed doing check schedule: {e}")