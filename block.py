import time
import json
from hashlib import sha256

class Block:
	def __init__(self,index,previousHash):
		self.index = index
		self.previousHash = previousHash
		self.timestamp = time.time()
		self.hash = None
		self.nonce=None
		self.listOfTransactions=[]
	
	def myHash(self):
		#compute hash of block based on the attributes of the block minus the self.hash value
		listOf = [id.transaction_id for id in self.listOfTransactions]
		hashtext = [self.previousHash,self.nonce,listOf,self.timestamp] 
		block_string = json.dumps(hashtext)
		return sha256(block_string.encode()).hexdigest()

	def add_transaction(self,transaction,capacity):
		#add a transaction to the block but we need to know whether it is full or not
		self.listOfTransactions.append(transaction)
		if len(self.listOfTransactions) == capacity:
			return True
		return False
		
	def check_equality(self,other):
		#check whether two blocks are equal
		return self.hash == other.hash

	def stringify(self):
		return str(self.__dict__)