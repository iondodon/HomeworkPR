from lab1.grabber import store
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 5001

server_socket.bind((host, port))
server_socket.listen()

try:
    while True:
        client_socket, client_addr = server_socket.accept()
        print("Got a connection from %s" % str(client_addr))

        msg = 'Thank you for connecting' + "\r\n"
        client_socket.send(msg.encode('ascii'))
        client_socket.close()
except Exception as e:
    print(e)
finally:
    server_socket.close()
