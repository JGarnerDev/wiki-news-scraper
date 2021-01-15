from cryptography.fernet import Fernet


# so we're sending a password called token

pw = "password"
pw = bytes(pw, 'utf-8')


# we have an encryption function, generated from a key

key = 'GhRBmc9f8JMvIxWzoE5G4Are8Pq20wc0XELcULKO6oc='
key = bytes(key, 'utf-8')
f = Fernet(key)

# Password is converted to a token
token = f.encrypt(pw).decode('utf-8')

# ... and can be decrypted later

b = f.decrypt(bytes(token, 'utf-8'))
result = b.decode('utf-8')

print(result)
