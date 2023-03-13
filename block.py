from datetime import datetime
from hashlib import sha256
import json

MINING_DIFFICULTY=2

class Block:
	def __init__(self,index,transactions,previous_hash, nonce=0):
		self.index=index
		self.previous_hash = previous_hash
		self.timestamp = datetime.now()
		self.nonce = nonce
		self.listOftransactions = transactions
		self.hash = self.myHash()
		self.cur_hash = -1
	
	def myHash(self):
		block_contents = str(self.index)+str(self.timestamp) + str(self.listOftransactions) + str(self.previous_hash) + str(self.nonce)
		block_hash = sha256(block_contents.encode())
		return block_hash.hexdigest()


	def add_transaction(self, transaction):
		#add a transaction to the block
		self.listOftransactions.append(transaction)

	def create_genesis(trans):
		genesis=Block(0,trans,'0')
		return genesis

	def mine_block(self,event):
		while self.valid_proof() is False and not event.isSet():
			self.nonce += 1
		self.cur_hash = self.myHash()
		return self

	def valid_proof(self, difficulty = MINING_DIFFICULTY):
		guess_hash = self.myHash()
		return guess_hash[:difficulty] == '0'*difficulty

	def print_contents(self):
		print("index", self.index)
		print("timestamp",self.timestamp)
		print("transactions:", self.listOftransactions)
		print("current hash:", self.hash)
		print("previous hash:", self.previous_hash)
  
  	
	def block_to_json(self):
		result = json.dumps(dict(
      	index = self.index,
		timestamp = self.timestamp.__str__(),
		transactions = self.listOftransactions,
		nonce = self.nonce,
		current_hash = self.cur_hash,
		previous_hash = self.previous_hash
		), sort_keys = True)
		return(result)