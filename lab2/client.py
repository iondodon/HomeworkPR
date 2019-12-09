import socket
from application import Application
from datagram import Datagram
from action import TransportAim, AppVerb
import config
from transport import Transport


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.CLIENT_PORT
        self.sessions = {}
        self.AES_ciphers = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

        self.transport = Transport(self)
        self.application = Application(self)

    def run(self):
        print("===========================================================")
        while True:
            app_layer_req = self.application.construct_app_req()
            if app_layer_req['verb'] == AppVerb.CLOSE:
                app_layer_req['data']['server_ip'] = self.ip
                self.application.client_close_session(app_layer_req)
                break
            else:
                self.application.client_send_data(app_layer_req, config.LOCALHOST)


if __name__ == "__main__":
    client = Client(config.LOCALHOST)
    client.run()