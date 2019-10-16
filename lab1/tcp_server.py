import grabber
import socket
from threading import Thread
import json
import fnmatch


def process_query(query_dict, STORE):
    result = []

    if query_dict['type'] == 'select':
        column_name = query_dict['column_name']
        for entity in STORE:
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


def wait_for_request(server_socket, THREADS, STORE):
    try:
        print('Listening...')
        client_socket, client_addr = server_socket.accept()
        print('Got a connection from %s' % str(client_addr))

        # prepare a new thread for the next request
        thrd = Thread(target=wait_for_request, args=(server_socket, THREADS, STORE))
        THREADS.append(thrd)
        thrd.start()

        request_json_string = client_socket.recv(1024)
        request_dict = json.loads(request_json_string.decode('ascii'))
        query_result_dict = process_query(request_dict, STORE)
        query_result_json = json.dumps(query_result_dict)

        client_socket.send(str(query_result_json).encode())
    except Exception as e:
        print(e)


def serve():
    THREADS = []
    STORE = grabber.grab_data()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen()

    wait_for_request(server_socket, THREADS, STORE)

    for thread in THREADS:
        thread.join()

    server_socket.close()


if __name__ == '__main__':
    serve()
