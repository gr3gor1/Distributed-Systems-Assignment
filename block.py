from time import time
import json
from hashlib import sha256

class Block:
	def __init__(self,index,previousHash,nonce):
		self.index = index
		self.previousHash = previousHash
		self.timestamp = time.time()
		self.hash = self.myHash()
		self.nonce=nonce
		self.listOfTransactions=[]
	
	def myHash(self):
		#compute hash of block
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()


	def add_transaction(self,transaction):
		#add a transaction to the block
		self.listOfTransactions.append(transaction)
