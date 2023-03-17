from block import Block
from wallet import wallet
from blockchain import Blockchain
from transaction import Transaction
import requests
import threading
import json 
import time 
import copy


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
			
   
   ####----orizoume to threat pou tha kanei thn ktelesei tou bootstrap ---###
   
			self.child = threading.Event()
			self.child.clear()
			t2 = threading.Thread( target = self.send_the_ring)
			t2.start()
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
		time.sleep(1)
		self.seen += 1
		if (self.seen == self.participants):
			print("All in")
			self.child.set()
		return


	def send_the_ring(self):
		self.child.wait()
		for i, ring in enumerate(self.ring[1:]):
			self.send(i+1, ring)
		
		time.sleep(3)

		self.chain.get_addresses(self.ring)
  
		for i, ring in enumerate(self.ring[1:]):
			self.wallet_dict={}
			for public_key in self.public_key_list:
				self.wallet_dict[public_key] = []
			if  no_mine.isSet():
				#no_mine.wait()
				self.send_transactions(i+1,self.public_key_list[i+1])
			
		return
  
  
	def send(self, identity,ring):
		print("Bootstrap send to Node with identity {}".format(identity))
		time.sleep(3)
		data = {
            'id': identity,
            'ring': self.ring,
            'public_key_list': self.public_key_list,
            'genesis': self.chain.list_blocks[0].print_contents()  
        }

		message = json.dumps(data)

		return requests.post(ring + '/child/register', data=message, headers=headers)
	
	def recieve(self,myid,ring,pub,genesis):
		print("Boss i reaceive the packet")
		if (myid==self.id):
			print("yes i am the rigth child")
		else:
			print("i am not this child")
		self.ring = copy.deepcopy(ring)
		self.chain.get_addresses(self.ring)
		self.public_key_list = copy.deepcopy(pub)
  
		self.wallet_dict={}
		for public_key in self.public_key_list:
			self.wallet_dict[public_key] = []

		gen = Block(genesis['index'], genesis['transactions'],genesis['nonce'], genesis['prev_hash'], genesis['timestamp'])
		self.chain.list_of_blocks.append(gen)
		trans_block_list = json.loads(genesis['transactions'])  # list
		trans = trans_block_list  

		current_trans = {
            'transaction_id': trans['transaction_id'],
            'amount': trans['amount'],
            'receiver': trans['recipient_address']
        }

        # Adding the father's transanction to trans_dict (father is the sender)
		self.wallet_dict[self.public_keys[0]].append(current_trans)

   
	def send_transactions(self,i,receiver_address):
		print("send 100 to {} node".format(i))
		#self.create_transaction(self.public_key_list[0],receiver_address,100)
		print(self.public_key_list[0],receiver_address,100)
		print("my balance father", self.wallet.balance())
   
		
 
 
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