import socket


class Server:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.udp_port = 5005
        self.sessions = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.udp_port))

        # while True:
        #     data, addr = self.sock.recvfrom(2)
        #     print("Received message:", data.decode('ascii'))


if __name__ == "main":
    pass