from time import time
import hashlib
import transaction

class Block:

	def __init__(self,index,previousHash):
		self.index = index
		self.previousHash = previousHash
		self.timestamp = time.time()
		self.hash = self.myHash()
		self.nonce=0
		self.listOfTransactions=[]
	
	def myHash(self):
		#compute hash of block
		content =  str(self.previousHash) + str(self.timestamp) + str(self.listOfTransactions) + str(self.nonce)
		con_hash = hashlib.sha256(content.encode()).hexdigest()
		return con_hash

	def add_transaction(self,transaction transaction):
		#add a transaction to the block
		self.listOfTransactions.append(transaction)
