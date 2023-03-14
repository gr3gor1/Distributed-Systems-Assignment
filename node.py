from block import Block
from wallet import wallet
from transaction import Transaction
import requests

CAPACITY = 2
MINING_DIFFICULTY = 2

class node:
	def __init__(self, ip, port, chain, current_id_count):
		
		self.ip = ip
		self.port = port 
		self.chain = chain
		self.current_id_count = current_id_count
		self.NBCs = 100
		self.wallet = self.create_wallet()
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def create_new_block(self):
		return Block(len(self.chain),transactions = [],previous_hash = self.chain[-1].hash)

	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		return wallet()

	def register_node_to_ring(self, node):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.ring.append([node.current_id_count, node.ip, node.port, node.wallet.public_key, node.wallet.balance])


	def create_transaction(sender, receiver, signature):
		#remember to broadcast it


	def broadcast_transaction(self, transaction):
		for node in self.ring:
			try:
				node.send(transaction)
			except requests.ConnectionError:
				print("Connection Error")
				pass

	def validate_transaction(self, transaction):
		#use of signature and NBCs balance


	def add_transaction_to_block(self, transaction, block):
		#if enough transactions  mine
		if len(block.transactions) == CAPACITY:
			new_block = self.mine_block()
			new_block.add_transaction(transaction)
		else:
			block.add_transaction(transaction)

	def mine_block(self):    
		new_block = self.create_new_block()
		proof = self.proof_of_work(new_block)
		return new_block, proof 

	def broadcast_block(self, block):
		for node in self.ring:
			try:
				node.send(block)
			except requests.ConnectionError:
				print("Connection Error")
				pass
		

	def valid_proof(self, proof, difficulty=MINING_DIFFICULTY):
		return proof[:difficulty] == difficulty*'0'


	def proof_of_work(self, block, difficulty=MINING_DIFFICULTY):
		proof = block.generate_hash()
		while proof[:difficulty] != "0"*difficulty:
			block.nonce += 1
			proof = block.generate_hash()
			block.nonce = 0
		return proof

	def validate_chain(self):
		for i in range(1, len(self.chain)):
			current = self.chain[i]
			previous = self.chain[i-1]
			if(current.hash != current.generate_hash()):
				print("Current hash does not equal generated hash")
				return False
			if(current.previous_hash != previous.generate_hash()):
				print("Previous block's hash got changed")
				self.resolve_conflicts()

		return True

	#consensus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain