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
import time
from random import randint
import sys

CAPACITY = 5
MINING_DIFFICULTY = 4

statistics = {"Throughput": [],
			  "Block time": []}

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
		#print('About to mine...')
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
						not_to_be_spent.extend(self.wallet.UTXOs[i+1:])
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
			self.create_new_block(first_transaction = transaction)
		else:
			block.add_transaction(transaction)

#--------------------------------------BROADCASTS-----------------------------------------------------

	def broadcast_transaction(self, transaction):
		def broadcast(transaction):
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/transaction'
			response = requests.post(address, data=pickle.dumps(transaction))
			if response.status_code != 200:
				print("Failed to broadcast a transaction!")

		threads = []
		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast, args=(transaction,))
				threads.append(thread)
				thread.start()
		
		for thread in threads:
			thread.join()

		return True
	
	def broadcast_block(self, block):
		#print('broadcasting mined block...')
		def broadcast(block):
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/block'
			response = requests.post(address, data=pickle.dumps(block))
			if response.status_code != 200:
				print("Failed to broadcast a block!")

		threads = []
		for node in self.ring[::-1]:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast, args=(block,))
				threads.append(thread)
				thread.start()
		
		for thread in threads:
			thread.join()

		return True

	def broadcast_ring(self):
		for node in self.ring:
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/ring'
			if node['id'] != self.id:
				response = requests.post(address, data=json.dumps(self.ring))
				if response.status_code != 200:
					return False
		return True

	def broadcast_init_finished(self):
		def broadcast():
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/init_finished'
			response = requests.post(address, data=json.dumps({"data": "Initialization finished, start reading transactions!"}))
			if response.status_code != 200:
				print("Failed to broadcast that initialization finished!")

		threads = []
		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target = broadcast)
				threads.append(thread)
				thread.start()
		
		for thread in threads:
			thread.join()

		return True

	def broadcast_statistics(self):
		address = 'http://' + str(self.ring[0]['ip']) + ':' + str(self.ring[0]['port']) + '/broadcast/statistics'
		response = requests.post(address, data=json.dumps(statistics))
		if response.status_code != 200:
			print("Failed to broadcast statistics!")



#--------------------------------------VALIDATIONS-----------------------------------------------------

	def verify_signature(self, transaction):
        # Load public key and verify message
		hash_obj = transaction.to_dict()
		hash_obj = SHA.new(str(hash_obj).encode())
		public_key = RSA.importKey(binascii.unhexlify(transaction.sender_address))
		verifier = PKCS1_v1_5.new(public_key)
		return verifier.verify(hash_obj, binascii.unhexlify(transaction.signature))

	def valid_proof(self, proof, difficulty=MINING_DIFFICULTY):
		return proof[:difficulty] == difficulty*'0'
	
	def validate_block(self, block):
		return self.valid_proof(block.hash) and self.blockchain.chain[-1].hash == block.previous_hash

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
		#print('started mining:', block.nonce, datetime.now())
		start = time.time()
		while proof[:difficulty] != "0"*difficulty and len(self.blockchain.chain) == chain:
			block.nonce += 1
			proof = block.myHash()
		#print('stopped mining:', block.nonce, datetime.now(), proof)
		end = time.time()
		block.hash = proof
		if self.valid_proof(proof):
			statistics["Block time"].append(end-start)
			block.confirmed = True
		block.nonce = 0
		return proof

#--------------------------------------CONSENSUS-----------------------------------------------------
	def valid_chain(self):
		#check for the longer chain across all nodes
		def get_chains():
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/send_chain'
			response = requests.get(address)
			chains.append(pickle.loads(response._content))

		chains = []
		threads = []
		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target=get_chains)
				threads.append(thread)
				thread.start()

		for thread in threads:
			thread.join()
		
		max_length = 0
		for chain in chains:
			if len(chain) > max_length:
				max_length = len(chain)
				longest_chain = chain

		return longest_chain

	def resolve_conflicts(self):
		#resolve correct chain
		def broadcast_chain():
			address = 'http://' + str(node['ip']) + ':' + str(node['port']) + '/broadcast/chain'
			response = requests.post(address, data=pickle.dumps(valid_chain))
			if response.status_code != 200:
				print('Failed to broadcast the longest chain (consensus)!')

		valid_chain = self.valid_chain()
		threads = []
		for node in self.ring:
			if node['id'] != self.id:
				thread = threading.Thread(target=broadcast_chain)
				threads.append(thread)
				thread.start()

		for thread in threads:
			thread.join()
				
		return True

#--------------------------------------VIEWS-----------------------------------------------------

	def read_transactions(self):
		transactions = []
		with open("transactions/{}nodes/transactions{}.txt".format(self.total_nodes, self.id), "r") as file:
			content = file.readlines()
			for line in content:
				id, amount = line.split()
				transactions.append([int(id[2]), int(amount)])
	
		time.sleep(self.id*0.1)
		for i, transaction in enumerate(transactions):
			for node in self.ring:
				if transaction[0] == node['id']:
					start = time.time()
					new_transaction = self.create_transaction(node['public_key'],  transaction[1])
					if not new_transaction:
						break
					self.broadcast_transaction(new_transaction)
					self.add_transaction_to_block(new_transaction, self.blockchain.chain[-1])
					end = time.time()
					statistics["Throughput"].append(end-start)
					break

			time.sleep(1)

		if self.id != 0:
			self.broadcast_statistics()

		return self.resolve_conflicts()

	def view_transactions(self):
		return self.blockchain.chain[-1].transactions

	def view_balance(self):
		return self.wallet.balance()