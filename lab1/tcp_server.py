from grabber import store
import socket
from threading import Thread
import json
import fnmatch

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 9999

server_socket.bind((host, port))
server_socket.listen()

threads = []


def process_query(query_dict):
    result = []

    if query_dict['type'] == 'select':
        column_name = query_dict['column_name']
        for entity in store:
            if column_name in entity.keys():
                result.append(entity[column_name])
    
    if 'glob_pattern' in query_dict.keys():
        glob_pattern = query_dict['glob_pattern']
        new_result = []
        for value in result:
            if fnmatch.fnmatch(value, glob_pattern):
                new_result.append(value)
        result = new_result

    return result


def wait_for_request():
    try:
        print("Listening on port " + str(port))
        client_socket, client_addr = server_socket.accept()
        print("Got a connection from %s" % str(client_addr))

        # prepare thread for the next request
        thrd = Thread(target=wait_for_request, args=[])
        threads.append(thrd)
        thrd.start()

        request_json_string = client_socket.recv(1024)
        request_dict = json.loads(request_json_string.decode('ascii'))
        query_result_dict = process_query(request_dict)
        query_result_json = json.dumps(query_result_dict)

        client_socket.send(str(query_result_json).encode())
    except Exception as e:
        print(e)


wait_for_request()

for thread in threads:
    thread.join()

server_socket.close()
