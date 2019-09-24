from threading import Thread
import requests
import json

import xml.etree.ElementTree as ET
import csv

store = {}
threads = []
token = ''


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
    with open('help_file', mode='w', newline='') as xmlfile:
        xmlfile.write(xmldata_string)

    with open('help_file', mode='r', newline='') as xmlfile:
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        print(root)


def store_csv(csvdata_string):
    with open('help_file', mode='w', newline='') as csvfile:
        csvfile.write(csvdata_string)

    with open('help_file', mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)


def convert_and_store(route, mime_type, json_dict):
    data = json_dict['data']
    if mime_type == 'application/xml':
        store_xml(data)
    if mime_type == 'text/csv':
        store_csv(data)


def parse(route):
    response = requests.get('http://localhost:5000' + route, headers={'X-Access-Token': token})

    json_str = response.content.decode('utf8')
    json_dict = json.loads(json_str)

    if 'mime_type' in json_dict.keys():
        convert_and_store(route, json_dict['mime_type'], json_dict)

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
