import requests

try:
  url = "https://nusava.onrender.com/api/stats/update/"
  payload = ""
  headers = {}

  response = requests.request("POST", url, headers=headers, data=payload)

  if (response.status_code == 200):
    print(f"[UPDATE STATISTICS] Response: {response.text}")
  else:
    print(f"[FAILED UPDATE STATISTICS] Failed doing update statistics. Status code: {response.status_code}. Response: {response.text}")

except Exception as e:
  print(f"[FAILED UPDATE STATISTICS] Failed doing update statistics: {e}")