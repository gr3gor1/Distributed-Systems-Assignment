import blockchain
from datetime import datetime
from hashlib import sha256



class Block:
	def __init__(self, previous_hash, transactions, nonce=0):
		##set

		self.previous_hash = previous_hash
		self.timestamp = datetime.now()
		self.hash = self.myHash()
		self.nonce = nonce
		self.transactions = transactions
	
	def myHash(self):
		#calculate self.hash
		block_contents = str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
		block_hash = sha256(block_contents.encode())
		return block_hash.hexdigest()


	def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block