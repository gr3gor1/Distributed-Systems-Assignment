from block import Block
from wallet import wallet
from blockchain import Blockchain
from transaction import Transaction
import requests
import threading
import json 



headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

ipbootstrap="localhost"
portbootstrap="5000"

no_mine = threading.Event()
no_mine.set()


class node:
	def __init__(self, id, ip, port,participants,bootstrap):
		
		self.ip = ip
		self.port = port
		self.id = id
		self.chain = Blockchain()
		self.wallet = wallet()
		addr="http://" + ipbootstrap + ":"+portbootstrap
		self.ring = [addr] 
		self.participants=participants
		self.public_key_list = []

		if(bootstrap == "yes"):
			self.seen = 0 
			self.public_key_list = [self.wallet.public_key]
			self.chain.genesis_block(participants, self.wallet.address)
			self.wallet.add_transaction(self.chain.list_blocks[0].listOftransactions[0])
		else:
			self.register_new_node()


  
	def register_new_node(self):
		message = {'address' : "http://" + str(self.ip) + ":" + str(self.port) ,'public_key':self.wallet.public_key}
		message = json.dumps(message)
		req = requests.post(self.ring[0]+"/bootstrap/register", data = message, headers=headers)
		return  req
	
 
	def register_node(self, ring, public_key):
		'''
            ring:           String, ring of new registered node (http:// + ip +  : + port)
            public_key:     String
        '''

		self.ring.append(ring)
		self.public_key_list.append(public_key)
		self.seen += 1
		if (self.seen == self.participants):
			print("All in")
		return


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