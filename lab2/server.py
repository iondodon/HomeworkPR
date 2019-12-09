import socket
import utils
from concurrent.futures import ThreadPoolExecutor
import config
from action import TransportAim, AppVerb
from app import App
from datagram import Datagram
from Crypto.Cipher import AES
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
        self.app = App(self)

    def propose_session(self, recv_dtg):
        dtg = Datagram(TransportAim.SESSION_PROPOSAL, self.ip, self.port, recv_dtg.source_ip, recv_dtg.source_port, recv_dtg.secure)
        if recv_dtg.source_ip in self.sessions.keys():
            session = self.sessions[recv_dtg.source_ip]
            dtg.set_payload(session)
            self.transport.send_datagram(dtg)
        else:
            session = {'session_id': len(self.sessions), 'server_ip': self.ip, 'server_port': self.port,
                       'client_ip': recv_dtg.source_ip, 'client_port': recv_dtg.source_port, 'secure': recv_dtg.secure,
                       'AES_key': utils.random_string()}
            self.sessions[session['client_ip']] = session

            dtg.set_payload(session)
            self.transport.send_datagram(dtg)

            self.AES_ciphers[recv_dtg.source_ip] = None
            cipher = AES.new(session['AES_key'].encode(), AES.MODE_ECB)
            self.AES_ciphers[recv_dtg.source_ip] = cipher
        print("===========================================================")

    def handle_app_request(self, payload, session):
        if payload['verb'] == AppVerb.POST:
            self.app.post_user(payload['data'], session)
        elif payload['verb'] == AppVerb.PUT:
            self.app.put_user(payload['data'], session)
        elif payload['verb'] == AppVerb.GET:
            self.app.get_user(payload['data'], session)
        elif payload['verb'] == AppVerb.DELETE:
            self.app.delete_user(payload['data'], session)
        elif payload['verb'] == AppVerb.CLOSE:
            self.close_session(session)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == TransportAim.GET_SESSION:
            self.propose_session(recv_dtg)
        elif recv_dtg.aim == TransportAim.APP_REQUEST:
            self.handle_app_request(recv_dtg.get_payload(), self.sessions[recv_dtg.source_ip])
        elif recv_dtg.aim == TransportAim.CORRUPTED:
            print("Message corrupted.")

    def close_session(self, session):
        print(self.sessions)
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        app_layer_resp = {'verb': AppVerb.ERR, 'message': "Session closed."}
        dtg.set_payload(app_layer_resp)
        self.transport.send_datagram(dtg)
        del self.sessions[session['client_ip']]
        print(self.sessions)

    def listen(self):
        while True:
            print("===========================================================")
            recv_dtg, addr = self.transport.receive_datagram()
            self.executor.submit(self.process_datagram, addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
