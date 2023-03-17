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

		key = RSA.generate(2048)
		public_key = key.publickey()
		self.public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
		self.private_key = binascii.hexlify(key.exportKey(format='DER')).decode('ascii')
		self.address = self.public_key
		self.transactions = []
		self.UTXOs = []

	def add_transaction(self, transaction):
		self.transactions.append(transaction)

	def balance(self):
		return 0


