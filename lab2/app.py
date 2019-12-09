from action import TransportAim, AppVerb
from datagram import Datagram


class App:
    def __init__(self, ip, port, users, send_datagram):
        self.ip = ip
        self.port = port
        self.users = users
        self.send_datagram = send_datagram

    def post_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK}
        else:
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This username already exists in the database."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def put_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            self.users[data['username']] = data
            app_layer_resp = {'verb': AppVerb.OK, 'message': "Successfully updated."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def get_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            app_layer_resp = {'verb': AppVerb.OK, 'data': self.users[data['username']]}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

    def delete_user(self, data, session):
        dtg = Datagram(TransportAim.APP_RESPONSE, self.ip, self.port, session['client_ip'], session['client_port'], session['secure'])
        if data['username'] not in self.users.keys():
            app_layer_resp = {'verb': AppVerb.ERR, 'message': "This user doe not exists in the database."}
        else:
            del self.users[data['username']]
            app_layer_resp = {'verb': AppVerb.OK, 'message': "User deleted."}
        dtg.set_payload(app_layer_resp)
        self.send_datagram(dtg)

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
