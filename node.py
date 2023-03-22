from block import Block
from wallet import wallet
from transaction import Transaction
import requests
import json
from uuid import uuid4
import threading
import pickle
from datetime import datetime
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii

CAPACITY = 2
MINING_DIFFICULTY = 4

headers={'Content-type':'application/json','Accept':'text/plain'}

class node:
	def __init__(self, id, bootstrap, ip, port, blockchain, total_nodes):
		
		self.id = id
		self.bootstrap = bootstrap
		self.ip = ip
		self.port = port 
		self.blockchain = blockchain
		self.total_nodes = total_nodes
		self.wallet = wallet()
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
		if self.bootstrap == 1:
			self.blockchain.create_genesis_block(self.wallet.address, 500)
			self.ring.append({'id': self.id, 
							  'ip': self.ip, 
							  'port': self.port, 
							  'public_key': self.wallet.public_key})
		else:
			thread = threading.Thread(target = self.share_node_info)
			thread.start()
			#thread.join()

	def share_node_info(self):
		data = {'id': self.id, 
				'ip': self.ip, 
				'port': self.port, 
				'public_key': self.wallet.public_key}

		address = 'http://127.0.0.1:5000/get_ring_info'
		response = requests.post(address, data=json.dumps(data), headers=headers)
		return True

#--------------------------------------NEW BLOCKS/TRANSACTIONS----------------------------------------

	def create_new_block(self, first_transaction):
		print('About to mine...')
		new_block = self.mine_block(first_transaction)
		if new_block.confirmed:
			self.broadcast_block(new_block)
			self.blockchain.add_block(new_block)
		return new_block

	def create_transaction(self, recipient_address, amount, initial_transaction=False):
		#remember to broadcast it
		if initial_transaction:
			new_transaction = Transaction("0", recipient_address=recipient_address, value=amount, transaction_inputs=None)
			new_transaction.transaction_outputs = [{'id':  uuid4().hex,
													'transaction_id': new_transaction.transaction_id,
													'amount': amount,
													'recipient': recipient_address}]
			self.wallet.UTXOs.extend(new_transaction.transaction_outputs)
			return new_transaction
		else:
			sent_amount = 0
			transaction_inputs = []
			flag = False
			to_be_spent = []
			not_to_be_spent = []
			for i, utxo in enumerate(self.wallet.UTXOs):
				if utxo['recipient'] == self.wallet.address:
					to_be_spent.append(self.wallet.UTXOs[i])
					sent_amount += utxo['amount']
					transaction_inputs.append(utxo['id'])
					if sent_amount >= amount:
						flag = True
						break
				else:
					not_to_be_spent.append(self.wallet.UTXOs[i])

			if flag:
				new_transaction = Transaction(self.wallet.address, recipient_address, amount, transaction_inputs)
				new_transaction.transaction_outputs = [{'id':  uuid4().hex,
														'transaction_id': new_transaction.transaction_id,
														'amount': amount,
														'recipient': recipient_address},
													   {'id':  uuid4().hex,
														'transaction_id': new_transaction.transaction_id,
														'amount': sent_amount-amount,
														'recipient': self.wallet.address}]

				new_transaction.sign_transaction(self.wallet.private_key)
				self.wallet.UTXOs = not_to_be_spent.copy()
				self.wallet.UTXOs.extend(new_transaction.transaction_outputs)
				return new_transaction
			
			else:
				print("Invalid transaction (balance is not enough)")
				return False

#--------------------------------------ADDITIONS/REGISTRATIONS-----------------------------------------

	def register_node_to_ring(self, data):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if self.bootstrap ==  1:
			self.ring.append(data)
			return True
		else:
			return False

	def add_transaction_to_block(self, transaction, block):
		#if enough transactions  mine
		if len(block.transactions) == CAPACITY:
			print("00000000")
			self.create_new_block(first_transaction = transaction)
		else:
			print("1111111")
			block.add_transaction(transaction)
		print("Node:",self.id, "Time:", datetime.now())

#--------------------------------------BROADCASTS-----------------------------------------------------

	def broadcast_transaction(self, transaction):
		if transaction.sender_address == "0":
			print('broadcasting initial transaction...')
		else:
			print('broadcasting transaction...', datetime.now())
		#cnt = 0
		def broadcast(transaction):
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/transaction'
			response = requests.post(address, data=pickle.dumps(transaction))
			if response.status_code != 200:
				#cnt += 1
				print("Failed to broadcast a transaction!")

		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast, args=(transaction,))
				thread.start()
		
		return True
	
	def broadcast_block(self, block):
		print('broadcasting mined block...')
		#cnt = 0
		def broadcast(block):
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/block'
			response = requests.post(address, data=pickle.dumps(block))
			if response.status_code != 200:
				#cnt += 1
				print("Failed to broadcast a block!")

		for node in self.ring[::-1]:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast, args=(block,))
				thread.start()
		
		return True

	def broadcast_ring(self):
		for node in self.ring:
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/ring'
			if node['id'] != self.id:
				response = requests.post(address, data=json.dumps(self.ring))
				if response.status_code != 200:
					return False
		return True
	
	def broadcast_chain(self):
		for node in self.ring:
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/chain'
			if node['id'] != self.id:
				response = requests.post(address, data=json.dumps(self.blockchain.chain))
				if response.status_code != 200:
					return False
		return True

	def broadcast_init_finished(self):
		def broadcast():
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/init_finished'
			response = requests.post(address, data=json.dumps({"data": "Initialization finished, start reading transactions!"}))
			if response.status_code != 200:
				#cnt += 1
				print("Failed to broadcast that initialization finished!")

		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast)
				thread.start()


#--------------------------------------VALIDATIONS-----------------------------------------------------

	def validate_transaction(self, transaction):
		#use of signature and NBCs balance
		return transaction.verify_transaction(transaction.sender_address)

	def verify_signature(self, transaction):
        # Load public key and verify message
		hash_obj = transaction.to_dict()
		hash_obj = SHA.new(str(hash_obj).encode())
		public_key = RSA.importKey(binascii.unhexlify(transaction.sender_address))
		verifier = PKCS1_v1_5.new(public_key)
		return verifier.verify(hash_obj, binascii.unhexlify(transaction.signature))

	def valid_proof(self, proof, difficulty=MINING_DIFFICULTY):
		return proof[:difficulty] == difficulty*'0'

	def validate_chain(self):
		for i in range(1, len(self.blockchain.chain)):
			current = self.blockchain.chain[i]
			previous = self.blockchain.chain[i-1]
			if(current.hash != current.myHash()):
				print("Current hash does not equal generated hash")
				return False
			if(current.previous_hash != previous.myHash()):
				print("Previous block's hash got changed")
				self.resolve_conflicts()
		return True

#--------------------------------------MINING-----------------------------------------------------

	def mine_block(self, first_transaction):   
		new_block = Block(index = self.blockchain.chain[-1].index+1, previous_hash = self.blockchain.chain[-1].hash, transactions = [first_transaction])
		self.proof_of_work(new_block)
		return new_block

	def proof_of_work(self, block, difficulty=MINING_DIFFICULTY):
		proof = block.myHash()
		chain = len(self.blockchain.chain)
		print('started mining:', block.nonce, datetime.now())
		while proof[:difficulty] != "0"*difficulty and len(self.blockchain.chain) == chain:
			block.nonce += 1
			proof = block.myHash()
		print('stopped mining:', block.nonce, datetime.now(), proof)
		block.hash = proof
		if self.valid_proof(proof):
			block.confirmed = True
		block.nonce = 0
		return proof

#--------------------------------------CONSENSUS-----------------------------------------------------
	def valid_chain(self):
		#check for the longer chain across all nodes
		chains = []
		for node in self.ring:
			if node['id'] != self.id:
				address = 'http://' + node['ip'] + ':' + node['port']
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
			if node['id'] != self.id:
				address = 'http://' + node['ip'] + ':' + node['port']
				response = requests.post(address + "/send_chain", data=json.dumps(valid_chain))
				if response.status_code != 200:
					return False
		return True

#--------------------------------------VIEWS-----------------------------------------------------

	def read_transactions(self):
		transactions = []	
		with open("transactions/{}nodes/transactions{}.txt".format(self.total_nodes, self.id), "r") as file:
			content = file.readlines()
			for line in content:
				id, amount = line.split()
				transactions.append([int(id[2]), int(amount)])
			print(transactions)
		return transactions


	def view_transactions(self):
		return self.blockchain.chain[-1].transactions

	def view_balance(self):
		return self.wallet.balance()