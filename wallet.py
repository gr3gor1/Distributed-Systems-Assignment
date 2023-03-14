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


class Wallet:

	def __init__(self):
		random = Crypto.Random.new().read()
		#create private key
		self.private_key = RSA.generate(1024,random)
		#create public key
		self.public_key = self.private_key.publickey()
		#hex public key
		self.public_key_hex = hashlib.sha256(self.public_key.exportKey(format='DER')).hexdigest()
		self.private_key_hex = hashlib.sha256(self.private_key.exportKey(format='DER')).hexdigest()
		#wallet address is equal to the SHA256 hash of the public key in hexadecimal format
		self.address = self.public_key_hex
		#transaction of the wallet
		self.transactions = []


		def balance(self):
			#sum of the UTXOs according to the assignment
			sum = 0
			for transaction in self.transactions:
				for out in transaction.transaction_out :
					if out.unspent and out.recipient_address == self.public_key:
						sum += out.amount

			return sum


			
