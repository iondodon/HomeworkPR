import pickle
import socket

from app import App
from datagram import Datagram
from action import TransportAim, AppVerb
import config
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

        self.app = App(self.ip, self.port, [], self.send_datagram)

    def send_datagram(self, dtg, encryption_enabled):
        print("Sending: ", dtg.aim)
        dest_ip = dtg.dest_ip
        dest_port = dtg.dest_port
        dtg: bytes = pickle.dumps(dtg)
        cipher = None
        if encryption_enabled:
            cipher = self.AES_ciphers[dest_ip]
            dtg = utils.append_zs(dtg)
            dtg = cipher.encrypt(dtg)
        while True:
            self.sock.sendto(dtg, (dest_ip, dest_port))
            response_dtg, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
            if encryption_enabled:
                response_dtg = cipher.decrypt(response_dtg)
            response_dtg = pickle.loads(response_dtg)
            print("Recv ack: ", response_dtg.aim)
            if response_dtg.aim == TransportAim.OK:
                break

    def receive_datagram(self, encryption_enabled):
        recv_dtg, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        print(recv_dtg)
        if encryption_enabled:
            cipher = self.AES_ciphers[address[0]]
            recv_dtg = cipher.decrypt(recv_dtg)
        recv_dtg = pickle.loads(recv_dtg)
        return recv_dtg, address

    def get_session(self, dest_ip, secure):
        dtg = Datagram(TransportAim.GET_SESSION, self.ip, self.port, dest_ip, config.SERVER_PORT, secure)
        for i in range(config.GET_SESSION_ATTEMPTS):
            self.send_datagram(dtg, False)
            recv_dtg, address = self.receive_datagram(False)
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
        self.send_datagram(dtg, True & dtg.secure)
        recv_dtg, address = self.receive_datagram(True & dtg.secure)
        print("App response:", recv_dtg.get_payload())

    def close_session(self, app_layer_req):
        server_ip = app_layer_req['data']['server_ip']
        dtg = Datagram(
            TransportAim.APP_REQUEST,
            self.ip, self.port,
            self.sessions[server_ip]['server_ip'],
            self.sessions[server_ip]['server_port'],
            self.sessions[server_ip]['secure']
        )
        dtg.set_payload(app_layer_req)
        self.send_datagram(dtg, self.sessions[server_ip]['secure'])
        dtg, address = self.receive_datagram(self.sessions[server_ip]['secure'])
        print(dtg.aim)
        print(self.sessions)
        del self.sessions[server_ip]
        print(self.sessions)

    def send_data(self, app_layer_req, dest_ip, secure):
        if dest_ip not in self.sessions.keys():
            session = self.get_session(dest_ip, secure)
            if not session:
                raise Exception("Could not get a session after several attempts.")
        session = self.sessions[dest_ip]
        print("===========================================================")
        self.perform_request(session, app_layer_req)

    def run(self):
        print("===========================================================")
        choice = input("secure 0/1: ")
        if choice == '0':
            secure = False
        else:
            secure = True
        while True:
            app_layer_req = self.app.construct_app_req()
            if app_layer_req['verb'] == AppVerb.CLOSE:
                app_layer_req['data']['server_ip'] = client.ip
                client.close_session(app_layer_req)
                break
            else:
                client.send_data(app_layer_req, config.LOCALHOST, secure)


if __name__ == "__main__":
    client = Client(config.LOCALHOST)
    client.run()
