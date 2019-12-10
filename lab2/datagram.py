import pickle

from Crypto.Hash import SHA256


class Datagram:
    def __init__(self, aim, source_ip, source_port, dest_ip, dest_port):
        self.aim = aim
        self.source_ip = source_ip
        self.source_port = source_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.__payload = None
        self.__cksm = None

    def set_payload(self, payload):
        self.__payload = payload
        hash_obj = SHA256.new(pickle.dumps(self.__payload))
        self.__cksm = hash_obj.hexdigest()

    def get_payload(self):
        return self.__payload

    def get_cksm(self):
        return self.__cksm