import pickle
import random
import socket
import string
from concurrent.futures import ThreadPoolExecutor
import json
import config
from action import TransportAim, AppVerb
from datagram import Datagram
from Crypto.Cipher import AES


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

    def randomString(self, stringLength=config.AES_KEY_LENGTH):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def append_zs(self, data: bytes):
        while len(data) % 16 != 0:
            data = data + '\0'.encode()
        return data

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        if dtg.dest_ip in self.sessions.keys() and self.sessions[dtg.dest_ip]['secure'] and dtg.aim is not TransportAim.SESSION_PROPOSAL:
            cipher = self.AES_ciphers[dtg.dest_ip]
            payload: bytes = pickle.dumps(dtg.get_payload())
            payload = self.append_zs(payload)
            payload = cipher.encrypt(payload)
            dtg.set_payload(payload)
        print("Sending payload: ", dtg.get_payload())
        self.sock.sendto(Datagram.obj_to_bin(dtg), (dtg.dest_ip, dtg.dest_port))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        datagram, addr = Datagram.bin_to_obj(recv_dtg_bin), address
        print("Received payload: ", datagram.get_payload())
        if datagram.source_ip in self.sessions.keys() and self.sessions[datagram.source_ip]['secure'] and datagram.aim is not TransportAim.GET_SESSION:
            cipher = self.AES_ciphers[datagram.source_ip]
            payload = cipher.decrypt(datagram.get_payload())
            payload = pickle.loads(payload)
            datagram.set_payload(payload)
        print("Received payload: ", datagram.get_payload(), type(datagram.get_payload()))
        return datagram, addr

    def propose_session(self, recv_dtg):
        dtg = Datagram(TransportAim.SESSION_PROPOSAL, self.ip, self.port, recv_dtg.source_ip, recv_dtg.source_port, recv_dtg.secure)
        if recv_dtg.source_ip in self.sessions.keys():
            session = self.sessions[recv_dtg.source_ip]
        else:
            session = {
                'session_id': len(self.sessions),
                'server_ip': self.ip,
                'server_port': self.port,
                'client_ip': recv_dtg.source_ip,
                'client_port': recv_dtg.source_port,
                'secure': recv_dtg.secure,
            }
            if recv_dtg.secure:
                session['AES_key'] = self.randomString()
                self.AES_ciphers[recv_dtg.source_ip] = {}
                cipher = AES.new(session['AES_key'].encode(), AES.MODE_ECB)
                self.AES_ciphers[recv_dtg.source_ip] = cipher
            self.sessions[session['client_ip']] = session
            print(session)
        dtg.set_payload(session)
        self.send_datagram(dtg)
        print("===========================================================")

    def post_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK}
        else:
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This username already exists in the database."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def put_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK, 'message': "Successfully updated."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def get_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            app_layer_resp = {'verb': AppVerb.OK, 'data': self.users[data['username']]}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def delete_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            del self.users[data['username']]
            app_layer_resp = {'verb': AppVerb.OK, 'message': "User deleted."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def handle_app_request(self, payload, session):
        if payload['verb'] == AppVerb.POST:
            self.post_user(payload['data'], session)
        elif payload['verb'] == AppVerb.PUT:
            self.put_user(payload['data'], session)
        elif payload['verb'] == AppVerb.GET:
            self.get_user(payload['data'], session)
        elif payload['verb'] == AppVerb.DELETE:
            self.delete_user(payload['data'], session)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == TransportAim.GET_SESSION:
            self.propose_session(recv_dtg)
        elif recv_dtg.aim == TransportAim.APP_REQUEST:
            self.handle_app_request(recv_dtg.get_payload(), self.sessions[recv_dtg.source_ip])

    def listen(self):
        while True:
            print("===========================================================")
            recv_dtg, addr = self.receive_datagram()
            self.executor.submit(self.process_datagram, addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
