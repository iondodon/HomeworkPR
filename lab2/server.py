import socket
from concurrent.futures import ThreadPoolExecutor
import config
from application import ServerApplication
from transport import ServerTransport


class Server:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.SERVER_PORT
        self.sessions = {}
        self.AES_ciphers = {}
        self.users = {}

        self.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

        self.transport = ServerTransport(self)
        self.application = ServerApplication(self)
        self.transport.set_application(self.application)
        self.application.set_transport(self.transport)

    def listen(self):
        while True:
            recv_dtg, addr = self.transport.receive_datagram()
            # self.executor.submit(self.process_datagram, addr, recv_dtg)
            self.transport.process_datagram(addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
