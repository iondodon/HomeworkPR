# from grabber import store
import socket
from threading import Thread

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 9999

server_socket.bind((host, port))
server_socket.listen()

threads = []


def wait_for_request():
    try:
        print("Listening on port " + str(port))
        client_socket, client_addr = server_socket.accept()
        print("Got a connection from %s" % str(client_addr))

        # prepare thread for the next request
        thrd = Thread(target=wait_for_request, args=[])
        threads.append(thrd)
        thrd.start()

        msg_received = client_socket.recv(1024)
        print(msg_received.decode('ascii'))

        client_socket.send(str('msg back').encode())
    except Exception as e:
        print(e)


wait_for_request()

for thread in threads:
    thread.join()

server_socket.close()
