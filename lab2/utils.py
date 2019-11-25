import pickle
import random
import string

import config
from action import TransportAim
from datagram import Datagram


def randomString(stringLength=config.AES_KEY_LENGTH):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def append_zs(data: bytes):
    while len(data) % 16 != 0:
        data = data + '\0'.encode()
    return data


def send_datagram(dtg, sessions, AES_ciphers, sock):
    print("Sending: ", dtg.aim)
    if dtg.dest_ip in sessions.keys() and sessions[dtg.dest_ip]['secure'] and dtg.aim is not TransportAim.SESSION_PROPOSAL:
        cipher = AES_ciphers[dtg.dest_ip]
        payload: bytes = pickle.dumps(dtg.get_payload())
        payload = append_zs(payload)
        payload = cipher.encrypt(payload)
        dtg.set_payload(payload)
    print("Sending payload: ", dtg.get_payload())
    sock.sendto(Datagram.obj_to_bytes(dtg), (dtg.dest_ip, dtg.dest_port))


def receive_datagram(sessions, AES_ciphers, sock):
    recv_dtg_bin, address = sock.recvfrom(config.RECV_DATA_SIZE)
    print("Received: ", Datagram.bytes_to_obj(recv_dtg_bin).aim, address)
    datagram, addr = Datagram.bytes_to_obj(recv_dtg_bin), address
    print("Received payload: ", datagram.get_payload())
    if datagram.source_ip in sessions.keys() and sessions[datagram.source_ip]['secure'] and datagram.aim is not TransportAim.GET_SESSION:
        cipher = AES_ciphers[datagram.source_ip]
        payload = cipher.decrypt(datagram.get_payload())
        payload = pickle.loads(payload)
        datagram.set_payload(payload)
    print("Received payload: ", datagram.get_payload(), type(datagram.get_payload()))
    return datagram, addr
