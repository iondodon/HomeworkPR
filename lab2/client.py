import socket
from datagram import Datagram
from action import TransportAim
import config
import req_constructor
from Crypto.Cipher import AES
import utils


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.CLIENT_PORT
        self.sessions = {}
        self.AES_ciphers = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def get_session(self, dest_ip, secure):
        dtg = Datagram(TransportAim.GET_SESSION, self.ip, self.port, dest_ip, config.SERVER_PORT, secure)
        for i in range(config.GET_SESSION_ATTEMPTS):
            utils.send_datagram(dtg, self.sessions, self.AES_ciphers, self.sock)
            recv_dtg, address = utils.receive_datagram(self.sessions, self.AES_ciphers, self.sock)
            if recv_dtg and address:
                self.sessions[recv_dtg.source_ip] = recv_dtg.get_payload()
                if self.sessions[recv_dtg.source_ip]['secure']:
                    key = self.sessions[recv_dtg.source_ip]['AES_key']
                    self.AES_ciphers[recv_dtg.source_ip] = AES.new(key.encode(), AES.MODE_ECB)
                return self.sessions[recv_dtg.source_ip]
        return None

    def perform_request(self, session, app_layer_req):
        dtg = Datagram(TransportAim.APP_REQUEST, self.ip, self.port, session['server_ip'], config.SERVER_PORT, session['secure'])
        dtg.set_payload(app_layer_req)
        utils.send_datagram(dtg, self.sessions, self.AES_ciphers, self.sock)
        recv_dtg, address = utils.receive_datagram(self.sessions, self.AES_ciphers, self.sock)
        print("App response:", recv_dtg.get_payload())
        pass

    def close_session(self):
        pass

    def send_data(self, app_layer_req, dest_ip, secure):
        if dest_ip not in self.sessions.keys():
            session = self.get_session(dest_ip, secure)
            if not session:
                raise Exception("Could not get a session after several attempts.")
        session = self.sessions[dest_ip]
        print(session)
        print("===========================================================")
        self.perform_request(session, app_layer_req)


if __name__ == "__main__":
    app_layer_req = req_constructor.construct_app_req()
    client = Client(config.LOCALHOST)
    client.send_data(app_layer_req, config.LOCALHOST, True)
