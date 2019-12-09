import pickle
from Crypto.Cipher import AES
import config
import utils
from action import TransportAim
from datagram import Datagram


class Transport:
    def __init__(self, gainer):
        self.gainer = gainer

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        dest_ip = dtg.dest_ip
        dest_port = dtg.dest_port
        dtg: bytes = pickle.dumps(dtg)
        if dest_ip in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[dest_ip]
            dtg = utils.append_zs(dtg)
            dtg = cipher.encrypt(dtg)

        while True:
            print("Waiting for ack")
            self.gainer.sock.sendto(dtg, (dest_ip, dest_port))
            recv_dtg, address = self.gainer.sock.recvfrom(config.RECV_DATA_SIZE)
            print("Received ack")
            print(recv_dtg)
            # if dest_ip in self.gainer.AES_ciphers.keys():
            #     cipher = self.gainer.AES_ciphers[dest_ip]
            #     recv_dtg = cipher.decrypt(recv_dtg)
            recv_dtg: Datagram = pickle.loads(recv_dtg)
            print(recv_dtg.aim)
            if recv_dtg.aim == TransportAim.OK:
                break

    def receive_datagram(self):
        recv_dtg, address = self.gainer.sock.recvfrom(config.RECV_DATA_SIZE)
        print(recv_dtg)
        if address[0] in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[address[0]]
            recv_dtg = cipher.decrypt(recv_dtg)
        recv_dtg: Datagram = pickle.loads(recv_dtg)
        print("Received: ", recv_dtg.aim)

        print("Sending ack")
        if utils.valid_cksm(recv_dtg.get_payload(), recv_dtg.get_cksm()):
            aim = TransportAim.OK
        else:
            aim = TransportAim.CORRUPTED
        dtg = Datagram(
            aim,
            self.gainer.ip,
            self.gainer.port,
            recv_dtg.source_ip,
            recv_dtg.source_port,
            recv_dtg.secure
        )
        dtg = pickle.dumps(dtg)
        # if address[0] in self.gainer.AES_ciphers.keys():
        #     cipher = self.gainer.AES_ciphers[address[0]]
        #     dtg = utils.append_zs(dtg)
        #     dtg = cipher.decrypt(dtg)
        self.gainer.sock.sendto(dtg, address)

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
            config.SERVER_PORT,
            True
        )
        for i in range(config.GET_SESSION_ATTEMPTS):
            self.send_datagram(dtg)
            recv_dtg, address = self.receive_datagram()
            if recv_dtg and address:
                self.gainer.sessions[recv_dtg.source_ip] = recv_dtg.get_payload()
                if self.gainer.sessions[recv_dtg.source_ip]['secure']:
                    key = self.gainer.sessions[recv_dtg.source_ip]['AES_key']
                    self.gainer.AES_ciphers[recv_dtg.source_ip] = AES.new(key.encode(), AES.MODE_ECB)
                return self.gainer.sessions[recv_dtg.source_ip]
        return None


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
            recv_dtg.source_port,
            recv_dtg.secure
        )
        if recv_dtg.source_ip in self.gainer.sessions.keys():
            session = self.gainer.sessions[recv_dtg.source_ip]
            dtg.set_payload(session)
            self.send_datagram(dtg)
        else:
            session = {'session_id': len(self.gainer.sessions), 'server_ip': self.gainer.ip, 'server_port': self.gainer.port,
                       'client_ip': recv_dtg.source_ip, 'client_port': recv_dtg.source_port, 'secure': recv_dtg.secure,
                       'AES_key': utils.random_string()}
            self.gainer.sessions[session['client_ip']] = session

            dtg.set_payload(session)
            self.send_datagram(dtg)

            self.gainer.AES_ciphers[recv_dtg.source_ip] = None
            cipher = AES.new(session['AES_key'].encode(), AES.MODE_ECB)
            self.gainer.AES_ciphers[recv_dtg.source_ip] = cipher
        print("===========================================================")