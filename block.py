from time import time
import hashlib
import blockchain




class Block:
<<<<<<< Updated upstream
	def __init__(self):
		#self.previousHash
		#self.timestamp
		#self.hash
		#self.nonce
		#self.listOfTransactions
=======
	def __init__(self,previousHash):
		self.previousHash = previousHash
		self.timestamp = time.time()
		self.hash = myHash()
		self.nonce=0
		self.listOfTransactions=[]
>>>>>>> Stashed changes
	
	def myHash:
		


	def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block