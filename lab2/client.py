import pickle
import socket
from datagram import Datagram
from action import TransportAim
import config
import req_constructor
from Crypto.Cipher import AES


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.CLIENT_PORT
        self.sessions = {}
        self.AES_ciphers = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def append_zs(self, data: bytes):
        print(data)
        while len(data) % 16 != 0:
            data = data + '\0'.encode()
        print(data)
        return data

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        if dtg.dest_ip in self.sessions.keys() and self.sessions[dtg.dest_ip]['secure'] and dtg.aim is not TransportAim.GET_SESSION:
            cipher = self.AES_ciphers[dtg.dest_ip]
            payload: bytes = pickle.dumps(dtg.get_payload())
            payload = self.append_zs(payload)
            payload = cipher.encrypt(payload)
            dtg.set_payload(payload)
        print("Sending payload: ", dtg.get_payload())
        self.sock.sendto(dtg.obj_to_bin(), (dtg.dest_ip, config.SERVER_PORT))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        datagram, addr = Datagram.bin_to_obj(recv_dtg_bin), address
        print("Received payload: ", datagram.get_payload())
        if datagram.source_ip in self.sessions.keys() and self.sessions[datagram.source_ip]['secure']:
            cipher = self.AES_ciphers[datagram.source_ip]
            payload = cipher.decrypt(datagram.get_payload())
            payload = pickle.loads(payload)
            datagram.set_payload(payload)
        print("Received payload: ", datagram.get_payload())
        return datagram, addr

    def get_session(self, dest_ip, secure):
        dtg = Datagram(TransportAim.GET_SESSION, self.ip, self.port, dest_ip, config.SERVER_PORT, secure)
        for i in range(config.GET_SESSION_ATTEMPTS):
            self.send_datagram(dtg)
            recv_dtg, address = self.receive_datagram()
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
        self.send_datagram(dtg)
        recv_dtg, address = self.receive_datagram()
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
