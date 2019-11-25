import random
import string
import config


def randomString(stringLength=config.AES_KEY_LENGTH):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def append_zs(data: bytes):
    while len(data) % 16 != 0:
        data = data + '\0'.encode()
    return data