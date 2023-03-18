from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import time
time.clock = time.time

# Generate an RSA key pair
key1 = RSA.generate(1024, randfunc=get_random_bytes)

# Print the private key in PEM format
private_key1 = key1.exportKey()
#print("Private Key:\n", private_key.decode())

# Print the public key in PEM format
public_key1 = key1.publickey().exportKey()
print("Public Key:\n", public_key1.decode('ISO-8859-1'))

key2 = RSA.generate(1024, randfunc=get_random_bytes)

# Print the private key in PEM format
private_key2 = key2.exportKey()
#print("Private Key:\n", private_key.decode())

# Print the public key in PEM format
public_key2 = key2.publickey().exportKey()
print("Public Key:\n", public_key2.decode('ISO-8859-1'))