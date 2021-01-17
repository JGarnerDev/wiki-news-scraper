
from cryptography.fernet import Fernet
import cryptography
import random
import unittest

from utils import *


# Encryption
#   Input: key (str), password (pw), encryption_method
#   Output: token (str, matches encrypted password (token) at wiki-news-wrangler API)
#   Pass: the output token matches the token at the API reliably
#   Fail: the output token does not match, or unreliably matches, the token at the API

# -------------------------------


# -------


class TestIsValidEncryption(unittest.TestCase):
    def test_bad_args(self):
        bad_args = [False, True, None, 0, 1,
                    "bad arg", b'bad arg', {}, []]
        for bad_arg in bad_args:
            result = is_valid_encryption(bad_arg)
            self.assertFalse(result)

    def test_good_args(self):
        good_args = [Fernet]
        for good_arg in good_args:
            result = is_valid_encryption(good_arg)
            self.assertTrue(result)

# -------


class TestGenerateEncrypter(unittest.TestCase):
    def test_bad_args(self):

        bad_args = [False, True, None, 0, 1, b'bad arg', {}, []]
        for _ in bad_args:
            bad_key_str = random.choice(bad_args)
            bad_method = random.choice(bad_args)
            with self.assertRaises(Exception):
                generate_encrypter(bad_key_str, bad_method)

    def test_good_args(self):
        good_key_args = [Fernet.generate_key(
        ), Fernet.generate_key(), Fernet.generate_key()]
        good_encryption_arg = Fernet

        for good_key in good_key_args:
            good_key_str = good_key.decode('utf-8')
            result = generate_encrypter(
                good_key_str, good_encryption_arg)
            self.assertIsInstance(result, cryptography.fernet.Fernet)

# -------


class TestIsTokenPWMatch(unittest.TestCase):
    def test_should_match(self):
        input_pw_str = "aaaa"
        api_pw_str = input_pw_str
        key_str = Fernet.generate_key().decode('utf-8')

        encrypter = generate_encrypter(key_str, Fernet)

        token = generate_token_UTF8(key_str, input_pw_str, Fernet)

        result = is_token_pw_match(token, api_pw_str, encrypter)

        self.assertTrue(result)

    # -------


class TestGenerateTokenUTF8(unittest.TestCase):
    def test_bad_pw_str_args(self):
        bad_pw_str_args = [False, True, None, 0, 1, b'bad arg', {}, []]

        good_key_arg = Fernet.generate_key().decode('utf-8')
        good_encryption_arg = Fernet

        for bad_pw_str_arg in bad_pw_str_args:
            with self.assertRaises(Exception):
                generate_token_UTF8(
                    good_key_arg, bad_pw_str_arg, good_encryption_arg)

    def test_bad_key_args(self):
        bad_key_args = [Fernet.generate_key(), False, True,
                        None, 0, 1, {}, []]

        good_pw_str_arg = "2350789tjigdbdsgf798h45u"

        good_encryption_arg = Fernet

        for bad_key_arg in bad_key_args:
            with self.assertRaises(Exception):
                generate_token_UTF8(
                    bad_key_arg, good_pw_str_arg, good_encryption_arg)

    def test_bad_encription_args(self):
        good_key_arg = Fernet.generate_key().decode('utf-8')

        good_pw_str_arg = "2350789tjigdbdsgf798h45u"

        bad_encryption_args = [cryptography.fernet, False,
                               True, None, 0, 1, b'bad arg', {}, []]

        for bad_encryption_arg in bad_encryption_args:
            with self.assertRaises(Exception):
                generate_token_UTF8(
                    good_key_arg, good_pw_str_arg, bad_encryption_arg)


if __name__ == '__main__':
    unittest.main()
