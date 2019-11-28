from action import AppVerb


def construct_app_req():
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
        app_layer_req['data']['server_ip'] = input("server ip: ")

    return app_layer_req
