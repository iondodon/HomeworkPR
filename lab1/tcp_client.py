import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 9999

client_socket.connect((host, port))

client_socket.send(str('hello, I\'m client').encode())

msg_received = client_socket.recv(1024)
print(msg_received.decode('ascii'))

client_socket.close()
