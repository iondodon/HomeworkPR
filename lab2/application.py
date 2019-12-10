import config
from action import TransportAim, AppVerb
from datagram import Datagram


class Application:
    def __init__(self, gainer):
        self.gainer = gainer
        self.transport = None

    def set_transport(self, transport):
        self.transport = transport


class ClientApplication(Application):
    def __init__(self, gainer):
        super().__init__(gainer)
        self.gainer = gainer

    def client_send_data(self, app_layer_req, dest_ip):
        if dest_ip not in self.gainer.sessions.keys():
            session = self.gainer.transport.get_session(dest_ip)
            if not session:
                raise Exception("Could not get a session after several attempts.")
        session = self.gainer.sessions[dest_ip]
        print("===========================================================")
        dtg = Datagram(
            TransportAim.APP_REQUEST,
            self.gainer.ip,
            self.gainer.port,
            session['server_ip'],
            config.SERVER_PORT
        )
        dtg.set_payload(app_layer_req)
        self.gainer.transport.send_datagram(dtg)
        recv_dtg, address = self.gainer.transport.receive_datagram()
        print("App response:", recv_dtg.get_payload())

    def construct_app_req(self):
        choice = input("""
        Construct a request...                   
        1: POST
        2: PUT
        3: GET
        4: DELETE

        0: CLOSE SESSION 

        Please enter your choice: """)

        app_layer_req = {}
        if choice == '1':
            app_layer_req['verb'] = AppVerb.POST
            app_layer_req['data'] = {}
            app_layer_req['data']['username'] = input("username: ")
            app_layer_req['data']['age'] = input('age:')
        elif choice == '2':
            app_layer_req['verb'] = AppVerb.PUT
            app_layer_req['data'] = {}
            app_layer_req['data']['username'] = input("username: ")
            app_layer_req['data']['age'] = input('age:')
        elif choice == '3':
            app_layer_req['verb'] = AppVerb.GET
            app_layer_req['data'] = {}
            app_layer_req['data']['username'] = input("username: ")
        elif choice == '4':
            app_layer_req['verb'] = AppVerb.DELETE
            app_layer_req['data'] = {}
            app_layer_req['data']['username'] = input("username: ")
        elif choice == '0':
            app_layer_req['verb'] = AppVerb.CLOSE
            app_layer_req['data'] = {}
            app_layer_req['data']['server_ip'] = None

        return app_layer_req


class ServerApplication(Application):
    def __init__(self, gainer):
        super().__init__(gainer)
        self.gainer = gainer

    def delete_user(self, data, session):
        dtg = Datagram(
            TransportAim.APP_RESPONSE,
            self.gainer.ip,
            self.gainer.port,
            session['client_ip'],
            session['client_port']
        )
        if data['username'] not in self.gainer.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            del self.gainer.users[data['username']]
            app_layer_resp = {'verb': AppVerb.OK, 'message': "User deleted."}
        dtg.set_payload(app_layer_resp)
        self.gainer.transport.send_datagram(dtg)

    def get_user(self, data, session):
        dtg = Datagram(
            TransportAim.APP_RESPONSE,
            self.gainer.ip,
            self.gainer.port,
            session['client_ip'],
            session['client_port']
        )
        if data['username'] not in self.gainer.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            app_layer_resp = {'verb': AppVerb.OK, 'data': self.gainer.users[data['username']]}
        dtg.set_payload(app_layer_resp)
        self.gainer.transport.send_datagram(dtg)

    def put_user(self, data, session):
        dtg = Datagram(
            TransportAim.APP_RESPONSE,
            self.gainer.ip,
            self.gainer.port,
            session['client_ip'],
            session['client_port']
        )
        if data['username'] not in self.gainer.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            self.gainer.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK, 'message': "Successfully updated."}
        dtg.set_payload(app_layer_resp)
        self.gainer.transport.send_datagram(dtg)

    def post_user(self, data, session):
        dtg = Datagram(
            TransportAim.APP_RESPONSE,
            self.gainer.ip,
            self.gainer.port,
            session['client_ip'],
            session['client_port']
        )
        if data['username'] not in self.gainer.users.keys():
            self.gainer.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK}
        else:
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This username already exists in the database."}
        dtg.set_payload(app_layer_resp)
        self.gainer.transport.send_datagram(dtg)

    def handle_app_request(self, payload, session):
        if payload['verb'] == AppVerb.POST:
            self.post_user(payload['data'], session)
        elif payload['verb'] == AppVerb.PUT:
            self.put_user(payload['data'], session)
        elif payload['verb'] == AppVerb.GET:
            self.get_user(payload['data'], session)
        elif payload['verb'] == AppVerb.DELETE:
            self.delete_user(payload['data'], session)
