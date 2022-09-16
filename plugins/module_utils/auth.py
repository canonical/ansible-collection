from secrets import randbelow
import time
from random import SystemRandom


rand_instance = SystemRandom()


def get_timestamp():
    return str(int(time.time()))


def get_nonce(timestamp: str):
    return str(rand_instance.getrandbits(64)) + timestamp

       
def combine_item(key, value):
    return f"{key}=\"{value}\""


def get_oauth_header(client_key, token_key, token_signature):
    timestamp = get_timestamp()
    nonce = get_nonce(timestamp)

    params = [
        ('oauth_nonce', nonce),
        ('oauth_timestamp', timestamp),
        ('oauth_version', '1.0'),
        ('oauth_signature_method', "PLAINTEXT"),
        ('oauth_consumer_key', client_key),
        ('oauth_token', token_key),
        ('oauth_signature', f"%26{token_signature}"),
    ]

    partial = ', '.join(combine_item(k, v) for k, v in params)
    return f"OAuth {partial}"
