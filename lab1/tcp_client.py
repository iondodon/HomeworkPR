import socket
from threading import Thread
import json
import sys


def make_request(client_socket, request_json_string):
    client_socket.connect(('localhost', 9999))

    request_dict = json.loads(request_json_string)
    request_json = json.dumps(request_dict)
    client_socket.send(request_json.encode())

    msg_received = client_socket.recv(1024)
    print(msg_received.decode('ascii'))

    client_socket.close()


def run_requests():
    THREADS = []
    SOCKETS = []

    for i in range(1):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKETS.append(client_socket)
        thrd = Thread(target=make_request, args=(client_socket, sys.argv[1]))
        THREADS.append(thrd)
        thrd.start()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    run_requests()
