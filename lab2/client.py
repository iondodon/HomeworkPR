import socket

from datagram import Datagram
from aim import Aim
import config


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.CLIENT_PORT
        self.sessions = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        self.sock.sendto(dtg.obj_to_bin(), (dtg.dest_ip, config.SERVER_PORT))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(config.RECV_DATA_SIZE)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        return Datagram.bin_to_obj(recv_dtg_bin), address

    def get_session(self, dest_ip, secure):
        dtg = Datagram(Aim.GET_SESSION, self.ip, self.port, dest_ip, config.SERVER_PORT, secure)
        for i in range(config.GET_SESSION_ATTEMPTS):
            self.send_datagram(dtg)
            recv_dtg, address = self.receive_datagram()
            if recv_dtg and address:
                self.sessions[recv_dtg.source_ip] = recv_dtg.get_payload()
                return recv_dtg, address
        return None

    def send_fragments_of_data(self, data):
        pass

    def close_session(self):
        pass

    def send_data(self, data, dest_ip, secure):
        if dest_ip not in self.sessions.keys():
            if self.get_session(dest_ip, secure):
                print(self.sessions)
            else:
                raise Exception("Could not get a session after several attempts.")
            

if __name__ == "__main__":
    data = "Eu ma numesc Ion."
    client = Client(config.LOCALHOST)
    client.send_data(data, config.LOCALHOST, True)