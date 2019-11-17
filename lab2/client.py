import socket

from datagram import Datagram
from aim import Aim


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = 5006
        self.sessions = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def send_datagram(self, dtg):
        print("Sending: ", dtg.aim)
        self.sock.sendto(dtg.obj_to_bin(), (dtg.dest_ip, 5005))

    def receive_datagram(self):
        recv_dtg_bin, address = self.sock.recvfrom(1024)
        print("Received: ", Datagram.bin_to_obj(recv_dtg_bin).aim, address)
        return Datagram.bin_to_obj(recv_dtg_bin), address

    def get_session(self, dest_ip, secure):
        dtg = Datagram(Aim.GET_SESSION, self.ip, dest_ip, secure)
        self.send_datagram(dtg)
        for i in range(5):
            recv_dtg, address = self.receive_datagram()
            if recv_dtg and address:
                return recv_dtg, address
        return None

    def send_public_key(self):
        pass

    def send_fragments_of_data(self, data):
        pass

    def close_session(self):
        pass

    def send_data(self, data, dest_ip, secure):
        if dest_ip not in self.sessions.keys():
            if self.get_session(dest_ip, secure):
                if not self.sessions[dest_ip][secure] or self.send_public_key():
                    if self.send_fragments_of_data(data):
                        self.close_session()
                    else:
                        raise Exception("Error while sending fragments of data")
                else:
                    raise Exception("Could not send public key.")
            else:
                raise Exception("Could not get a session after 5 attempts.")

    def listen(self):
        while True:
            print(self.receive_datagram())


if __name__ == "__main__":
    data = "Eu ma numesc Ion."
    client = Client("127.0.0.1")
    client.send_data(data, "127.0.0.1", True)