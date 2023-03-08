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
		##set

		key = RSA.generate(2048)
		public_key = key.publickey()
		self.public_key = public_key
		self.private_key = key
		self.address = self.public_key
		#self.transactions

	def balance():

