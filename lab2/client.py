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

    def perform_request(self, session, app_layer_req):
        dtg = Datagram(TransportAim.APP_REQUEST, self.ip, self.port, session['server_ip'], config.SERVER_PORT, session['secure'])
        dtg.set_payload(app_layer_req)
        self.transport.send_datagram(dtg)
        recv_dtg, address = self.transport.receive_datagram()
        print("App response:", recv_dtg.get_payload())

    def send_data(self, app_layer_req, dest_ip):
        if dest_ip not in self.sessions.keys():
            session = self.transport.get_session(dest_ip)
            if not session:
                raise Exception("Could not get a session after several attempts.")
        session = self.sessions[dest_ip]
        print("===========================================================")
        self.perform_request(session, app_layer_req)

    def run(self):
        print("===========================================================")
        while True:
            app_layer_req = self.application.construct_app_req()
            if app_layer_req['verb'] == AppVerb.CLOSE:
                app_layer_req['data']['server_ip'] = self.ip
                self.application.client_close_session(app_layer_req)
                break
            else:
                self.send_data(app_layer_req, config.LOCALHOST)


if __name__ == "__main__":
    client = Client(config.LOCALHOST)
    client.run()