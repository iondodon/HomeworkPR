import socket
from threading import Thread
import json

THREADS = []
SOCKETS = []


def make_request(client_socket):
    client_socket.connect(('localhost', 9999))

    request_dict = {'type': 'select', 'column_name': 'username', 'glob_pattern': '*mi'}
    request_json = json.dumps(request_dict)
    client_socket.send(request_json.encode())
    print(request_json.encode())

    msg_received = client_socket.recv(1024)
    print(msg_received.decode('ascii'))

    client_socket.close()


def run_requests():
    global THREADS, SOCKETS

    for i in range(1):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKETS.append(client_socket)
        thrd = Thread(target=make_request, args=[client_socket])
        THREADS.append(thrd)
        thrd.start()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    run_requests()
