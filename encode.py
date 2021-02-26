# Password Encoder for demo users

import hashlib

x = input("> ")
result = hashlib.sha256(x.encode())
print(result.hexdigest())