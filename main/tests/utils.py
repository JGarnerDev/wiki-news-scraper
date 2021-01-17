
def is_valid_encryption(encryption):
    if encryption and (("encrypt" and "decrypt") in dir(encryption)):
        return True
    return False


def generate_encrypter(key_str, encryption):
    key_is_string = isinstance(key_str, str)
    encryption_is_valid = is_valid_encryption(encryption)
    if not key_is_string:
        raise Exception(
            'First argument of generate_encrypter must be a string')
    if not encryption_is_valid:
        raise Exception(
            'Second argument of generate_encrypter must be a an approved encryption method')
    key = bytes(key_str, 'utf-8')
    return encryption(key)


def is_token_pw_match(token,  pw_str, encrypter):
    if not token or not pw_str or not encrypter:
        return False

    return True


def generate_token_UTF8(key_str, pw_str, encryption):
    encrypter = generate_encrypter(key_str, encryption)
    b_pw = bytes(pw_str, 'utf')
    return encrypter.encrypt(b_pw).decode('utf-8')
