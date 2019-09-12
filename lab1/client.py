import requests
import json


def get_token():
    response = requests.get('http://localhost:5000/register')

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    for key, value in json_dict.items():
        if key == 'access_token':
            return value


def parse(route):
    print(route)
    response = requests.get('http://localhost:5000' + route, headers={'X-Access-Token': token})

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    links = json_dict['link']
    for key in links.keys():
        parse(links[key])

    print('\n')


token = get_token()
if token:
    parse('/home')
