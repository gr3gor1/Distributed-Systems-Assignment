from block import Block
from wallet import wallet
from blockchain import Blockchain
from transaction import Transaction
import requests
import threading

no_mine = threading.Event()
no_mine.set()


class node:
	def __init__(self, id, ip, port):
		
		self.ip = ip
		self.port = port
		self.id = id
		self.chain = Blockchain()
		self.wallet = wallet()
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


	def register_node_to_ring(self, node):
		ring={
			"id":self.id,
			"ip":self.port,
			"port":self.port,
			"balance":self.wallet.balance()
		}
		self.ring.append(ring)


	'''def create_transaction(sender, receiver, signature):
		#remember to broadcast it


	def broadcast_transaction(self, transaction):

	def validate_transaction(self, transaction):
		#use of signature and NBCs balance



	def broadcast_block(self, block):
		



	def validate_chain(self):
		for i in range(1, len(self.chain.chain)):
			current = self.chain.chain[i]
			previous = self.chain.chain[i-1]
			if(current.cur_hash != current.generate_hash()):
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
		#resolve correct chain '''