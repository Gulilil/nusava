import requests
import json

try:
  # TODO Add get current user.id from server

  url = "https://nusava-production.up.railway.app/action"
  payload = json.dumps({
    "user_id": 1
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  if (response.status_code == 200):
    print(f"[INTERNAL ACTION] Response: {response.text}")
  else:
    print(f"[FAILED INTERNAL ACTION] Failed doing internal action. Status code: {response.status_code}. Response: {response.text}")

except Exception as e:
  print(f"[FAILED INTERNAL ACTION] Failed doing internal action: {e}")