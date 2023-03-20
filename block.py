from datetime import datetime
from hashlib import sha256



class Block:
	def __init__(self, index, previous_hash, transactions, nonce=0):
		self.index = index
		self.previous_hash = previous_hash
		self.timestamp = datetime.now()
		self.nonce = nonce
		self.transactions = transactions
		self.hash = self.myHash()
		self.confirmed = False
	
	def myHash(self):
		block_contents = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
		block_hash = sha256(block_contents.encode())
		return block_hash.hexdigest()

	def add_transaction(self, transaction):
		self.transactions.append(transaction)
