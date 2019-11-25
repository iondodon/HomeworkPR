import pickle


class Datagram:
    def __init__(self, aim, source_ip, source_port, dest_ip, dest_port, secure):
        self.aim = aim
        self.source_ip = source_ip
        self.source_port = source_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.__payload = None
        self.secure = secure

    def set_payload(self, payload):
        self.__payload = payload

    def get_payload(self):
        return self.__payload

    def obj_to_bytes(self):
        return pickle.dumps(self)

    @staticmethod
    def bytes_to_obj(datagram_bin):
        return pickle.loads(datagram_bin)
