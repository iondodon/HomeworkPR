#!/usr/bin/python3

import requests
import json

response = requests.get('http://localhost:5000/register')

json_data = response.content.decode('utf8').replace("'", '"')
print(json_data + '\n')

data = json.loads(json_data)
print(data)
print('\n') 

s = json.dumps(data, indent=4, sort_keys=True)
print(s + '\n')

for key, value in data.items():
    if key == "access_token" in data:
        token = value
        print(token)


response = requests.get(
    'http://localhost:5000/home',
    params={'q': 'requests+language:python'},
    headers={'X-Access-Token': token},
)
print(response)

json_data = response.content.decode('utf8').replace("'", '"')
print(json_data)
