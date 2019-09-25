from threading import Thread
import pprint
import requests
import json
import yaml
import re
import xml.etree.ElementTree as ET
import csv

store = []
items = 0
threads = []
token = ''
pp = pprint.PrettyPrinter(indent=4)


def get_token():
    response = requests.get('http://localhost:5000/register')

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    global token
    for key, value in json_dict.items():
        if key == 'access_token':
            token = value
            return token


def store_xml(xmldata_string):
    tree = ET.fromstring(xmldata_string)
    for record in tree:
        item = {}
        for field in record:
            item[field.tag] = field.text
        store.append(item)


def store_csv(csvdata_string):
    with open('help_file', mode='w', newline='') as csvfile:
        csvfile.write(csvdata_string)

    with open('help_file', mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {}
            for key in row:
                item[key] = row[key]
            store.append(item)


def store_yaml(yamldata_string):
    data = yaml.load(yamldata_string)
    for item in data:
        store.append(item)


def store_json(jsondata_string):
    regex = r'''(?<=[}\]"']),(?!\s*[{["'])'''
    jsondata_string = re.sub(regex, "", jsondata_string, 0)

    json_list = json.loads(jsondata_string)
    for item in json_list:
        store.append(item)


def convert_and_store(json_dict, mime_type='application/json'):
    data = json_dict['data']
    if mime_type == 'application/xml':
        store_xml(data)
    elif mime_type == 'text/csv':
        store_csv(data)
    elif mime_type == 'application/x-yaml':
        store_yaml(data)
    elif mime_type == 'application/json':
        store_json(data)


def parse(route):
    response = requests.get('http://localhost:5000' + route, headers={'X-Access-Token': token})

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    if 'data' in json_dict.keys():
        if 'mime_type' in json_dict.keys():
            convert_and_store(json_dict, json_dict['mime_type'])
        else:
            convert_and_store(json_dict)

    for key in json_dict.keys():
        if key == 'link':
            for link_key in json_dict['link'].keys():
                thrd = Thread(target=parse, args=[json_dict[key][link_key]])
                threads.append(thrd)
                thrd.start()


if get_token():
    thread = Thread(target=parse, args=['/home'])
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

pp.pprint(store)
