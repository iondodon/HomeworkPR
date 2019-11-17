import socket
from concurrent.futures import ThreadPoolExecutor

from aim import Aim
from datagram import Datagram
from payload import Payload


class Server:
    def __init__(self, ip):
        self.ip = ip
        self.port = 5005
        self.sessions = {}

        self.executor = ThreadPoolExecutor(max_workers=100)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        self.sock.sendto(Datagram.obj_to_bin(dtg), (dtg.dest_ip, 5006))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(1024)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        return Datagram.bin_to_obj(recv_dtg_bin), address

    def offer_session(self, recv_dtg):
        dtg = Datagram(Aim.SESSION_PROPOSAL, self.ip, recv_dtg.source_ip, recv_dtg.secure)
        if recv_dtg.source_ip in self.sessions.keys():
            session = self.sessions[recv_dtg.source_ip]
        else:
            session = {'aa': "aa"}
        payload = Payload(session)
        dtg.set_payload(payload)
        self.send_datagram(dtg)

    def process_datagram(self, addr, recv_dtg):
        if recv_dtg.aim == Aim.GET_SESSION:
            self.offer_session(recv_dtg)

    def listen(self):
        while True:
            recv_dtg, addr = self.receive_datagram()
            self.executor.submit(self.process_datagram, addr, recv_dtg)


if __name__ == "__main__":
    server = Server("127.0.0.1")
    server.listen()
