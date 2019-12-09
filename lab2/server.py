import socket
from concurrent.futures import ThreadPoolExecutor
import config
from action import TransportAim, AppVerb
from application import Application
from transport import Transport


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

        self.transport = Transport(self)
        self.application = Application(self)

    def handle_app_request(self, payload, session):
        if payload['verb'] == AppVerb.POST:
            self.application.post_user(payload['data'], session)
        elif payload['verb'] == AppVerb.PUT:
            self.application.put_user(payload['data'], session)
        elif payload['verb'] == AppVerb.GET:
            self.application.get_user(payload['data'], session)
        elif payload['verb'] == AppVerb.DELETE:
            self.application.delete_user(payload['data'], session)
        elif payload['verb'] == AppVerb.CLOSE:
            self.application.server_close_session(session)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == TransportAim.GET_SESSION:
            self.transport.propose_session(recv_dtg)
        elif recv_dtg.aim == TransportAim.APP_REQUEST:
            self.handle_app_request(recv_dtg.get_payload(), self.sessions[recv_dtg.source_ip])
        elif recv_dtg.aim == TransportAim.CORRUPTED:
            print("Message corrupted.")

    def listen(self):
        while True:
            print("===========================================================")
            recv_dtg, addr = self.transport.receive_datagram()
            # self.executor.submit(self.process_datagram, addr, recv_dtg)
            self.process_datagram(addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
