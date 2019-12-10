import pickle
from Crypto.Cipher import AES
import config
import utils
from action import TransportAim, AppVerb
from datagram import Datagram
import time


class Transport:
    def __init__(self, gainer):
        self.gainer = gainer
        self.application = None

    def set_application(self, application):
        self.application = application

    def send_datagram(self, dtg):
        time.sleep(10)
        print("=====================================================================")
        utils.write("Sending: ", dtg.aim)
        dest_ip = dtg.dest_ip
        dest_port = dtg.dest_port
        dtg: bytes = pickle.dumps(dtg)
        if dest_ip in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[dest_ip]
            dtg = utils.append_zs(dtg)
            dtg = cipher.encrypt(dtg)

        while True:
            utils.write("Waiting for ack", "")
            self.gainer.sock.sendto(dtg, (dest_ip, dest_port))
            ack_dtg, address = self.gainer.sock.recvfrom(config.RECV_DATA_SIZE)
            utils.write("Received ack", "")
            if dest_ip in self.gainer.AES_ciphers.keys():
                utils.write("Encrypted ack: ", ack_dtg)
                cipher = self.gainer.AES_ciphers[dest_ip]
                ack_dtg = cipher.decrypt(ack_dtg)
            ack_dtg: Datagram = pickle.loads(ack_dtg)
            utils.write("Received ack: ", ack_dtg)
            utils.write("Received ack aim: ", ack_dtg.aim)
            if ack_dtg.aim == TransportAim.OK:
                break
        print("=====================================================================")

    def receive_datagram(self):
        time.sleep(10)
        print("=====================================================================")
        recv_dtg, address = self.gainer.sock.recvfrom(config.RECV_DATA_SIZE)
        utils.write("Received dtg: ", recv_dtg)
        if address[0] in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[address[0]]
            recv_dtg = cipher.decrypt(recv_dtg)
            utils.write("Decrypted recv dtg: ", recv_dtg)
        recv_dtg: Datagram = pickle.loads(recv_dtg)
        utils.write("Received dtg aim: ", recv_dtg.aim)

        time.sleep(5)

        utils.write("Sending ack", "")
        if utils.valid_cksm(recv_dtg.get_payload(), recv_dtg.get_cksm()):
            aim = TransportAim.OK
        else:
            aim = TransportAim.CORRUPTED
        utils.write("Sending as ack: ", aim)
        ack_dtg = Datagram(
            aim,
            self.gainer.ip,
            self.gainer.port,
            recv_dtg.source_ip,
            recv_dtg.source_port
        )
        ack_dtg = pickle.dumps(ack_dtg)
        utils.write("Ack dtg encoded: ", ack_dtg)
        if address[0] in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[address[0]]
            ack_dtg = utils.append_zs(ack_dtg)
            ack_dtg = cipher.encrypt(ack_dtg)
            utils.write("Encrypted ack dtg: ", ack_dtg)
        self.gainer.sock.sendto(ack_dtg, address)
        print("=====================================================================")
        return recv_dtg, address


class ClientTransport(Transport):
    def __init__(self, gainer):
        super().__init__(gainer)
        self.gainer = gainer

    def get_session(self, dest_ip):
        dtg = Datagram(
            TransportAim.GET_SESSION,
            self.gainer.ip,
            self.gainer.port,
            dest_ip,
            config.SERVER_PORT
        )
        for i in range(config.GET_SESSION_ATTEMPTS):
            self.send_datagram(dtg)
            recv_dtg, address = self.receive_datagram()
            if recv_dtg and address:
                self.gainer.sessions[recv_dtg.source_ip] = recv_dtg.get_payload()
                key = self.gainer.sessions[recv_dtg.source_ip]['AES_key']
                self.gainer.AES_ciphers[recv_dtg.source_ip] = AES.new(key.encode(), AES.MODE_ECB)
                return self.gainer.sessions[recv_dtg.source_ip]
        return None

    def client_close_session(self, app_layer_req):
        server_ip = app_layer_req['data']['server_ip']
        dtg = Datagram(
            TransportAim.CLOSE,
            self.gainer.ip, self.gainer.port,
            self.gainer.sessions[server_ip]['server_ip'],
            self.gainer.sessions[server_ip]['server_port']
        )
        dtg.set_payload(app_layer_req)
        self.send_datagram(dtg)
        dtg, address = self.gainer.transport.receive_datagram()
        print(dtg.aim)
        print(self.gainer.sessions)
        del self.gainer.sessions[server_ip]
        print(self.gainer.sessions)


class ServerTransport(Transport):
    def __init__(self, gainer):
        super().__init__(gainer)
        self.gainer = gainer

    def propose_session(self, recv_dtg):
        dtg = Datagram(
            TransportAim.SESSION_PROPOSAL,
            self.gainer.ip,
            self.gainer.port,
            recv_dtg.source_ip,
            recv_dtg.source_port
        )
        if recv_dtg.source_ip in self.gainer.sessions.keys():
            session = self.gainer.sessions[recv_dtg.source_ip]
            dtg.set_payload(session)
            self.send_datagram(dtg)
        else:
            session = {'session_id': len(self.gainer.sessions), 'server_ip': self.gainer.ip, 'server_port': self.gainer.port,
                       'client_ip': recv_dtg.source_ip, 'client_port': recv_dtg.source_port, 'AES_key': utils.random_string()}
            self.gainer.sessions[session['client_ip']] = session

            dtg.set_payload(session)
            self.send_datagram(dtg)

            self.gainer.AES_ciphers[recv_dtg.source_ip] = None
            cipher = AES.new(session['AES_key'].encode(), AES.MODE_ECB)
            self.gainer.AES_ciphers[recv_dtg.source_ip] = cipher

    def server_close_session(self, session):
        print("Before closing session:", self.gainer.sessions)
        dtg = Datagram(
            TransportAim.CLOSE,
            self.gainer.ip,
            self.gainer.port,
            session['client_ip'],
            session['client_port']
        )
        app_layer_resp = {'verb': AppVerb.CLOSE, 'message': "Session closed."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)
        del self.gainer.sessions[session['client_ip']]
        print("After closing session:", self.gainer.sessions)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == TransportAim.GET_SESSION:
            self.propose_session(recv_dtg)
        elif recv_dtg.aim == TransportAim.APP_REQUEST:
            self.application.handle_app_request(recv_dtg.get_payload(), self.gainer.sessions[recv_dtg.source_ip])
        elif recv_dtg.aim == TransportAim.CLOSE:
            self.server_close_session(self.gainer.sessions[addr[0]])
        elif recv_dtg.aim == TransportAim.CORRUPTED:
            print("Message corrupted.")