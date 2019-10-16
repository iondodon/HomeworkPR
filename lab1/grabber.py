from threading import Thread
import requests
import json
import yaml
import re
import xml.etree.ElementTree as ET
import csv


def safe_request(route, headers):
    response = None
    try:
        response = requests.get(route, headers=headers)
    except requests.ConnectionError as e:
        print(e)
    return response


def get_token():
    response = safe_request('http://localhost:5000/register', {})
    if not response:
        return

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    for key, value in json_dict.items():
        if key == 'access_token':
            return value


def store_xml(xmldata_string, STORE):
    tree = ET.fromstring(xmldata_string)
    for record in tree:
        item = {}
        for field in record:
            item[field.tag] = field.text
        STORE.append(item)


def store_csv(csvdata_string, STORE):
    with open('help_file', mode='w', newline='') as csvfile:
        csvfile.write(csvdata_string)

    with open('help_file', mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {}
            for key in row:
                item[key] = row[key]
            STORE.append(item)


def store_yaml(yamldata_string, STORE):
    data = yaml.load(yamldata_string)
    for item in data:
        STORE.append(item)


def store_json(jsondata_string, STORE):

    regex = r'''(?<=[}\]"']),(?!\s*[{["'])'''
    jsondata_string = re.sub(regex, "", jsondata_string, 0)

    json_list = json.loads(jsondata_string)
    for item in json_list:
        STORE.append(item)


def convert_and_store(json_dict, STORE, mime_type='application/json',):
    data = json_dict['data']

    if mime_type == 'application/xml':
        store_xml(data, STORE)
    elif mime_type == 'text/csv':
        store_csv(data, STORE)
    elif mime_type == 'application/x-yaml':
        store_yaml(data, STORE)
    elif mime_type == 'application/json':
        store_json(data, STORE)


def parse(route, STORE, THREADS, TOKEN):
    response = safe_request('http://localhost:5000' + route, {'X-Access-Token': TOKEN})
    if not response:
        return

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    if 'data' in json_dict.keys():
        if 'mime_type' in json_dict.keys():
            thrd = Thread(target=convert_and_store, args=(json_dict, STORE, json_dict['mime_type']))
            THREADS.append(thrd)
            thrd.start()
        else:
            thrd = Thread(target=convert_and_store, args=(json_dict, STORE))
            THREADS.append(thrd)
            thrd.start()

    for key in json_dict.keys():
        if key == 'link':
            for link_key in json_dict['link'].keys():
                thrd = Thread(target=parse, args=(json_dict[key][link_key], STORE, THREADS, TOKEN))
                THREADS.append(thrd)
                thrd.start()


def grab_data():
    THREADS = []
    STORE = []
    TOKEN = get_token()

    if TOKEN:
        thread = Thread(target=parse, args=('/home', STORE, THREADS, TOKEN))
        THREADS.append(thread)
        thread.start()

    for thread in THREADS:
        thread.join()

    for i in range(len(STORE)):
        for key in STORE[i].keys():
            STORE[i][key] = str(STORE[i][key])

    return STORE
