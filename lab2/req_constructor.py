from action import AppVerb


def construct_app_req():
    choice = input("""
    Construct a request...                   
    1: POST
    2: PUT
    3: GET
    4: DELETE

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

    return app_layer_req
