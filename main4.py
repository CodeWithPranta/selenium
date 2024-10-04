import requests

try:
    response = requests.get('https://www.google.com')
    print("HTTPS request successful:", response.status_code)
except requests.exceptions.SSLError as e:
    print("SSL Error:", e)

