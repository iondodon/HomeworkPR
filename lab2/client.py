import socket
from application import ClientApplication
from action import AppVerb
import config
from transport import ClientTransport


class Client:
    def __init__(self, ip):
        self.ip = ip
        self.port = config.CLIENT_PORT
        self.sessions = {}
        self.AES_ciphers = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

        self.transport = ClientTransport(self)
        self.application = ClientApplication(self)
        self.transport.set_application(self.application)
        self.application.set_transport(self.transport)

    def run(self):
        while True:
            app_layer_req = self.application.construct_app_req()
            if app_layer_req['verb'] == AppVerb.CLOSE:
                app_layer_req['data']['server_ip'] = self.ip
                self.transport.client_close_session(app_layer_req)
                break
            else:
                self.application.client_send_data(app_layer_req, config.LOCALHOST)


if __name__ == "__main__":
    client = Client(config.LOCALHOST)
    client.run()