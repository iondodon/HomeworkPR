import pickle
import socket
import utils
from concurrent.futures import ThreadPoolExecutor
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

    def send_datagram(self, dtg, encryption_enabled):
        print("Sending: ", dtg.aim)
        dest_ip = dtg.dest_ip
        dest_port = dtg.dest_port
        dtg: bytes = pickle.dumps(dtg)
        if encryption_enabled:
            cipher = self.AES_ciphers[dest_ip]
            dtg = utils.append_zs(dtg)
            dtg = cipher.encrypt(dtg)
        self.sock.sendto(dtg, (dest_ip, dest_port))

    def receive_datagram(self):
        recv_dtg, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        cipher = None
        print(self.sessions)
        if address[0] in self.sessions.keys() and self.sessions[address[0]]['secure']:
            cipher = self.AES_ciphers[address[0]]
            recv_dtg = cipher.decrypt(recv_dtg)
        recv_dtg = pickle.loads(recv_dtg)
        print("Received: ", recv_dtg.aim)

        if not utils.valid_cksm(recv_dtg.get_payload(), recv_dtg.get_cksm()):
            response_dtg = Datagram(TransportAim.CORRUPTED, self.ip, self.port, recv_dtg.source_ip, recv_dtg.source_port, recv_dtg.secure)
            print("Sending ack: ", response_dtg.aim)
            response_dtg = pickle.dumps(response_dtg)
            if address[0] in self.sessions.keys() and self.sessions[address[0]]['secure']:
                response_dtg = utils.append_zs(response_dtg)
                response_dtg = cipher.encrypt(response_dtg)
            self.sock.sendto(response_dtg, address)
            return response_dtg, address
        else:
            response_dtg = Datagram(TransportAim.OK, self.ip, self.port, recv_dtg.source_ip, recv_dtg.source_port, recv_dtg.secure)
            print("Sending ack: ", response_dtg.aim)
            response_dtg = pickle.dumps(response_dtg)
            if address[0] in self.sessions.keys() and self.sessions[address[0]]['secure']:
                response_dtg = utils.append_zs(response_dtg)
                response_dtg = cipher.encrypt(response_dtg)
            self.sock.sendto(response_dtg, address)

        return recv_dtg, address

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
                session['AES_key'] = utils.randomString()
                self.AES_ciphers[recv_dtg.source_ip] = None
                cipher = AES.new(session['AES_key'].encode(), AES.MODE_ECB)
                self.AES_ciphers[recv_dtg.source_ip] = cipher
            self.sessions[session['client_ip']] = session
        dtg.set_payload(session)
        self.send_datagram(dtg, False)
        print("===========================================================")

    def post_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK}
        else:
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This username already exists in the database."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg, True & dtg.secure)

    def put_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK, 'message': "Successfully updated."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg, True & dtg.secure)

    def get_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            app_layer_resp = {'verb': AppVerb.OK, 'data': self.users[data['username']]}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg, True & dtg.secure)

    def delete_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            del self.users[data['username']]
            app_layer_resp = {'verb': AppVerb.OK, 'message': "User deleted."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg, True & dtg.secure)

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
        elif recv_dtg.aim == TransportAim.CORRUPTED:
            print("Message corrupted.")

    def listen(self):
        while True:
            print("===========================================================")
            recv_dtg, addr = self.receive_datagram()
            self.executor.submit(self.process_datagram, addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
