from block import Block
from wallet import wallet
from transaction import Transaction
import requests
import json

CAPACITY = 2
MINING_DIFFICULTY = 2

class node:
	def __init__(self, id, bootstrap, ip, port, chain):
		
		self.id = id
		self.bootstrap = bootstrap
		self.ip = ip
		self.port = port 
		self.chain = chain
		self.wallet = wallet()
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

#--------------------------------------NEW BLOCKS/TRANSACTIONS----------------------------------------

	def create_new_block(self):
		new_block, proof = self.mine_block()
		self.broadcast(new_block)
		return new_block

	def create_transaction(self, receiver_address, amount):
		#remember to broadcast it
		sent_amount = 0
		for i, utxo in enumerate(self.wallet.UTXOs):
			sent_amount += utxo
			if sent_amount >= amount:
				try:
					self.wallet.UTXOs = self.wallet.UTXOs[i+1:]
				except:
					self.wallet.UTXOs = []
				break
		



		new_transaction = Transaction(self.wallet.address, self.wallet.private_key, receiver_address, amount, transaction_inputs, transaction_outputs)

#--------------------------------------ADDITIONS/REGISTRATIONS-----------------------------------------

	def register_node_to_ring(self, node):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if self.bootstrap:
			self.ring.append([node.id, node.ip, node.port, node.wallet.public_key, node.wallet.balance()])
			return True
		else:
			return False

	def add_transaction_to_block(self, transaction, block):
		#if enough transactions  mine
		if len(block.transactions) == CAPACITY:
			new_block = self.create_new_block()
			new_block.add_transaction(transaction)
		else:
			block.add_transaction(transaction)

#--------------------------------------BROADCASTS-----------------------------------------------------

	def broadcast_transaction(self, transaction, endpoint):
		for node in self.ring:
			address = 'https://' + str(node[1]) + ':' + str(node[2])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(transaction.stringify()))
				if response.status_code != 200:
					return False
		return True
	
	def broadcast_block(self, block, endpoint):
		for node in self.ring:
			address = 'https://' + str(node[1]) + ':' + str(node[2])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(block.stringify()))
				if response.status_code != 200:
					return False
		return True


	def broadcast_ring(self, endpoint):
		for node in self.ring:
			address = 'https://' + str(node[1]) + ':' + str(node[2])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(self.ring))
				if response.status_code != 200:
					return False
		return True
	
	def broadcast_chain(self, endpoint):
		for node in self.ring:
			address = 'https://' + str(node[1]) + ':' + str(node[2])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(self.chain))
				if response.status_code != 200:
					return False
		return True

#--------------------------------------VALIDATIONS-----------------------------------------------------

	def validate_transaction(self, transaction):
		#use of signature and NBCs balance


	def valid_proof(self, proof, difficulty=MINING_DIFFICULTY):
		return proof[:difficulty] == difficulty*'0'

	def validate_chain(self):
		for i in range(1, len(self.chain)):
			current = self.chain[i]
			previous = self.chain[i-1]
			if(current.hash != current.myHash()):
				print("Current hash does not equal generated hash")
				return False
			if(current.previous_hash != previous.myHash()):
				print("Previous block's hash got changed")
				self.resolve_conflicts()
		return True

#--------------------------------------MINING-----------------------------------------------------

	def mine_block(self):    
		new_block = Block(previous_hash = self.chain[-1].hash, transactions = [])
		proof = self.proof_of_work(new_block)
		return new_block, proof 

	def proof_of_work(self, block, difficulty=MINING_DIFFICULTY):
		proof = block.myHash()
		while proof[:difficulty] != "0"*difficulty:
			block.nonce += 1
			proof = block.myHash()
			block.nonce = 0
		return proof

#--------------------------------------CONSENSUS-----------------------------------------------------
	def valid_chain(self):
		#check for the longer chain across all nodes
		chains = []
		for node in self.ring:
			if node[0] != self.id:
				address = 'http://' + node[1] + ':' + node[2]
				response = requests.get(address + "/send_chain")
				chains.append(response._content)
		
		max_length = 0
		for chain in chains:
			if len(chain) > max_length:
				max_length = len(chain)
				longer_chain = chain
		
		return longer_chain

	def resolve_conflicts(self):
		#resolve correct chain
		valid_chain = self.valid_chain()
		for node in self.ring:
			if node[0] != self.id:
				address = 'http://' + node[1] + ':' + node[2]
				response = requests.post(address + "/send_chain", data=json.dumps(valid_chain))
				if response.status_code != 200:
					return False
		return True