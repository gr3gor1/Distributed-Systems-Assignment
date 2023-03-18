import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):
		##set

		self.private_key,self.public_key= self.generate_wallet()
		self.address=self.public_key
		self.transactions=[]
		self.UTXOs = []
  
  
	def generate_wallet(self):	
		priv=RSA.generate(2048)
		pub = priv.publickey()
  
		return binascii.hexlify(priv.exportKey(format='DER')).decode('ascii'), binascii.hexlify(pub.exportKey(format='DER')).decode('ascii')
	
     
	def balance(self):
		amount =0
		for i in range(0,len(self.transactions)):
			amount=amount+self.transactions[i]['value']
		
		return amount
	
	def add_transaction(self, transaction):
		#add a transaction to the block
		self.transactions.append(transaction)
  
  
	def mybalance(self):
		balance = 0
		for utxo in self.UTXOs:
			if utxo['recipient'] == self.address:
				balance += utxo['value']
		return balance