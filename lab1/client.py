from threading import Thread
import requests
import json
import time

data = {}
threads = []
token = ''


def convert_and_store(mime_type):
    print(mime_type)
    return


def get_token():
    response = requests.get('http://localhost:5000/register')

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    global token
    for key, value in json_dict.items():
        if key == 'access_token':
            token = value
            return token


def parse(route):
    print(route)
    response = requests.get('http://localhost:5000' + route, headers={'X-Access-Token': token})

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    if 'mime_type' in json_dict.keys():
        convert_and_store(json_dict['mime_type'])

    for key in json_dict.keys():
        if key == 'link':
            for link_key in json_dict['link'].keys():
                thrd = Thread(target=parse, args=[json_dict[key][link_key]])
                threads.append(thrd)
                thrd.start()

    print('\n')


start_time = time.time()

if get_token():
    thread = Thread(target=parse, args=['/home'])
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()
print(end_time - start_time)
