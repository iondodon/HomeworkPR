import socket
from threading import Thread

threads = []
sockets = []

# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 9999

# client_socket.connect((host, port))


def make_request(index):
    client_socket = sockets[index]
    client_socket.connect((host, port))
    client_socket.send(str('hello, I\'m client').encode())

    msg_received = client_socket.recv(1024)
    print(msg_received.decode('ascii'))

    client_socket.close()


for i in range(100000):
    sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    thrd = Thread(target=make_request, args=[i])
    threads.append(thrd)
    thrd.start()

for thread in threads:
    thread.join()
