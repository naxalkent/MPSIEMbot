import requests
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "https://<IP>:3334/connect/token"
payload = {
    "client_id": "mpx",
    "client_secret": "***",
    "grant_type": "password",
    "response_type": "code id_token token",
    "scope": "offline_access mpx.api ptkb.api",
    "username": "***",
    "password": "***"
}

response = requests.post(url, data=payload, verify=False)  # verify=False для игнорирования проверки сертификата, используйте осторожно
data = response.json()
access_token = data.get('access_token')

if access_token:
    print("Access token:", access_token)
else:
    print("Не удалось получить access token. Код ошибки:", response.status_code)
