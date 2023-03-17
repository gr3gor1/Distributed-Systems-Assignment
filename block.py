import time
from hashlib import sha256
import json

MINING_DIFFICULTY=1

class Block:
	def __init__(self,index,transactions,previous_hash, nonce=0,timestamp=time.time()):
		self.index=index
		self.previous_hash = previous_hash
		self.timestamp = timestamp
		self.nonce = nonce
		self.listOftransactions = transactions
		self.cur_hash = -1
	
 ## xasaroume to block ###
 
	def myHash(self):
		block_contents = str(self.index)+str(self.timestamp) + str(self.listOftransactions) + str(self.previous_hash) + str(self.nonce)
		block_hash = sha256(block_contents.encode())
		return block_hash.hexdigest()

## prosuetoume ena transaction sto block ##

	def add_transaction(self, transaction):
		#add a transaction to the block
		self.listOftransactions.append(transaction)

	def create_genesis(trans):
		genesis=Block(0,trans,'0')
		return genesis

### mine to block kai proof of work ###

	def mine_block(self,event):
		while self.valid_proof() is False and not event.isSet():
			self.nonce += 1
		self.cur_hash = self.myHash()
		return self

	def valid_proof(self, difficulty = MINING_DIFFICULTY):
		guess_hash = self.myHash()
		return guess_hash[:difficulty] == '0'*difficulty

### theloume to block se json ####

	def print_contents(self):
		content={
		"index": self.index,
		"timestamp":self.timestamp,
		"transactions:": self.listOftransactions,
		"cur_hash:": self.cur_hash,
		"previous_hash:": self.previous_hash}
		return content
  
	def print_cont(self):
		print("index", self.index)
		print("timestamp",self.timestamp)
		print("transactions:", self.listOftransactions)
		print("current hash:", self.hash)
		print("previous hash:", self.previous_hash)
