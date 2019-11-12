import socket
import pickle


class Client:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.udp_port = 5005

        self.session = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.sendto(str(MESSAGE).encode(), (self.ip, self.udp_port))

    def get_session(self, ip, port):
        MESSAGE = "Hello"
        self.session = self.sock.sendto(str(MESSAGE).encode(), (ip, port))


if __name__ == "__main__":
    pass