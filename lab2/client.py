import socket
import pickle


class Client:
    def __init__(self):
        self.sessions = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.sendto(str(MESSAGE).encode(), (self.ip, self.udp_port))
        # self.sessions = self.sock.sendto(str(MESSAGE).encode(), (ip, port))

    def get_session(self, ip_string, secure):
        # set secure or not in session
        pass

    def send_public_key(self, ip_string):
        pass

    def send_fragments_of_data(self, data, ip_string):
        pass

    def close_session(self, ip_string):
        pass

    def send_data(self, data, ip_string, secure):
        if ip_string not in self.sessions.keys():
            if self.get_session(ip_string, secure):
                if not self.sessions[ip_string][secure] or self.send_public_key(ip_string):
                    if self.send_fragments_of_data(data, ip_string):
                        self.close_session(ip_string)
                    else:
                        raise Exception("Error while sending fragments of data")
                else:
                    raise Exception("Could not send public key.")
            else:
                raise Exception("Could not get a session after 5 attempts.")


if __name__ == "__main__":
    data = "Eu ma numesc Ion."
    client = Client()
    client.send_data(data, "127.0.0.1", True)