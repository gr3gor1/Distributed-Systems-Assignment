import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:

	def __init__(self):
		#create private key
		root = RSA.generate(1024)
		self.private_key = root.exportKey().decode()
		#create public key
		self.public_key = root.publickey().exportKey().decode()
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
		
	def stringify(self):
		return str(self.__dict__)


			
