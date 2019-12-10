import pickle
import random
import string
import config
from Crypto.Hash import SHA256


def random_string(stringLength=config.AES_KEY_LENGTH):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def append_zs(data: bytes):
    while len(data) % 16 != 0:
        data = data + '\0'.encode()
    return data


def valid_cksm(payload, recv_cksm):
    if payload is None:
        print("No payload received.")
        return True

    hash_obj = SHA256.new(pickle.dumps(payload))
    print("Recv cksm: ", recv_cksm)
    if hash_obj.hexdigest() != recv_cksm:
        return False
    print("Calc cksm: ", hash_obj.hexdigest())

    return True


def write(action, text):
    print(config.color_start + action + config.color_end, text)