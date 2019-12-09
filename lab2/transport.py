import pickle
import config
import utils


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
        self.gainer.sock.sendto(dtg, (dest_ip, dest_port))

    def receive_datagram(self):
        recv_dtg, address = self.gainer.sock.recvfrom(config.RECV_DATA_SIZE)
        print(recv_dtg)
        if address[0] in self.gainer.AES_ciphers.keys():
            cipher = self.gainer.AES_ciphers[address[0]]
            recv_dtg = cipher.decrypt(recv_dtg)
        recv_dtg = pickle.loads(recv_dtg)
        print("Received: ", recv_dtg.aim)
        return recv_dtg, address
