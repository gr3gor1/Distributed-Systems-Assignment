from block import Block
from wallet import wallet
from transaction import Transaction
import requests
import json
from uuid import uuid4

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
		if self.bootstrap == False:
			self.share_node_info()


	def share_node_info(self):
		data = {'id': self.id, 
				'ip': self.ip, 
				'port': self.port, 
				'public_key': self.wallet.public_key,
				'balance': self.wallet.balance()}
		
		address = 'https://127.0.0.1:5000/get_ring_info'
		response = requests.post(address, data=json.dumps(data))
		print(response.json())


		


#--------------------------------------NEW BLOCKS/TRANSACTIONS----------------------------------------

	def create_new_block(self):
		new_block, proof = self.mine_block()
		self.broadcast(new_block)
		return new_block

	def create_transaction(self, receiver_address, amount):
		#remember to broadcast it
		sent_amount = 0
		transaction_inputs = []
		flag = False
		for i, utxo in enumerate(self.wallet.UTXOs):
			sent_amount += utxo['amount']
			transaction_inputs.append(utxo['id'])
			if sent_amount >= amount:
				try:
					self.wallet.UTXOs = self.wallet.UTXOs[i+1:]
				except:
					self.wallet.UTXOs = []
				flag = True
				break
		
		if flag:
			new_transaction = Transaction(self.wallet.address, self.wallet.private_key, receiver_address, amount, transaction_inputs)
			new_transaction.transaction_outputs = [{'id':  uuid4().hex,
													'transactions_id': new_transaction.transaction_id,
													'amount': amount,
													'recipient': receiver_address},
												   {'id':  uuid4().hex,
													'transactions_id': new_transaction.transaction_id,
													'amount': sent_amount-amount,
													'recipient': self.wallet.address}]

			self.add_transaction_to_block(new_transaction, self.chain[-1])
			self.broadcast_transaction(new_transaction)
			return new_transaction
		
		else:
			print("Invalid transaction (balance is not enough)")
			return False
	
#--------------------------------------ADDITIONS/REGISTRATIONS-----------------------------------------

	def register_node_to_ring(self, node):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if self.bootstrap:
			self.ring.append({'id': node.id, 
							  'ip': node.ip, 
							  'port': node.port, 
							  'public_key': node.wallet.public_key,
							  'balance': node.wallet.balance()})
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

	def broadcast_transaction(self, transaction, endpoint = '/broadcast/transaction'):
		for node in self.ring:
			address = 'https://' + str(node['ip']) + ':' + str('port')
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(transaction))
				if response.status_code != 200:
					return False
		return True
	
	def broadcast_block(self, block, endpoint = '/broadcast/block'):
		for node in self.ring:
			address = 'https://' + str(node['ip']) + ':' + str(node['port'])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(block))
				if response.status_code != 200:
					return False
		return True


	def broadcast_ring(self, endpoint = '/broadcast/ring'):
		for node in self.ring:
			address = 'https://' + str(node.ring['ip']) + ':' + str(node['port'])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(self.ring))
				if response.status_code != 200:
					return False
		return True
	
	def broadcast_chain(self, endpoint = '/broadcast/chain'):
		for node in self.ring:
			address = 'https://' + str(node['ip']) + ':' + str(node['port'])
			if node[id] != node.id:
				response = requests.post(address + endpoint, data=json.dumps(self.chain))
				if response.status_code != 200:
					return False
		return True

#--------------------------------------VALIDATIONS-----------------------------------------------------

	def validate_transaction(self, transaction):
		#use of signature and NBCs balance
		return transaction.verify_transaction(transaction.sender_address)

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

#--------------------------------------VIEWS-----------------------------------------------------

	def view_transactions(self):
		return self.chain[-1].transactions

	def view_balance(self):
		return self.wallet.balance()