import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		random = Crypto.Random.new().read()
		#create private key
		self.private_key = RSA.generate(1024,random)
		#create public key
		self.public_key = self.private_key.publickey()
		#hex public key
		self.public_key_hex = binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')
		#wallet address is equal to the SHA256 hash of the public key iin hexadecimal format
		self.address = hashlib.sha256(self.public_key_hex.encode('ascii')).hexdigest()
		#transaction of the wallet
		self.transactions = []
