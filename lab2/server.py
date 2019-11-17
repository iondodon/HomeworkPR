import random
import socket
import string
from concurrent.futures import ThreadPoolExecutor
import config
from aim import Aim
from datagram import Datagram


class Server:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.SERVER_PORT
        self.sessions = {}

        self.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def randomString(self, stringLength=config.AES_KEY_LENGTH):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        self.sock.sendto(Datagram.obj_to_bin(dtg), (dtg.dest_ip, dtg.dest_port))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        return Datagram.bin_to_obj(recv_dtg_bin), address

    def propose_session(self, recv_dtg):
        dtg = Datagram(Aim.SESSION_PROPOSAL, self.ip, self.port, recv_dtg.source_ip, recv_dtg.source_port, recv_dtg.secure)
        if recv_dtg.source_ip in self.sessions.keys():
            session = self.sessions[recv_dtg.source_ip]
        else:
            session = {
                'session_id': len(self.sessions),
                'server_ip': self.ip,
                'client_ip': recv_dtg.source_ip
            }
            if recv_dtg.secure:
                session['AES_key'] = self.randomString()
            self.sessions[session['client_ip']] = session
        dtg.set_payload(session)
        self.send_datagram(dtg)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == Aim.GET_SESSION:
            self.propose_session(recv_dtg)

    def listen(self):
        while True:
            recv_dtg, addr = self.receive_datagram()
            self.executor.submit(self.process_datagram, addr, recv_dtg)


if __name__ == "__main__":
    server = Server(config.LOCALHOST)
    server.listen()
