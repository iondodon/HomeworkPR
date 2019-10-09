import socket
from threading import Thread
import json

threads = []
sockets = []

host = "127.0.0.1"
port = 9999


def make_request(index):
    client_socket = sockets[index]
    client_socket.connect((host, port))

    request_dict = {'type': 'select', 'column_name': 'username'}
    request_json = json.dumps(request_dict)
    client_socket.send(request_json.encode())

    msg_received = client_socket.recv(1024)
    print(msg_received.decode('ascii'))

    client_socket.close()


for i in range(1):
    sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    thrd = Thread(target=make_request, args=[i])
    threads.append(thrd)
    thrd.start()

for thread in threads:
    thread.join()
