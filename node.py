from uuid import uuid4
from block import Block
from wallet import wallet
from blockchain import Blockchain
from transaction import Transaction
import requests
import threading
import json 
import time 
import copy
import pickle

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
		#########################################################
		self.auto_run = threading.Event()
		self.auto_run.clear()
		thread3 = threading.Thread(target=self.run_all_trans)  # target to auto run trans
		thread3.start()
		
  

		if(bootstrap == "yes"):
			self.seen = 0 
			self.public_key_list = [self.wallet.public_key]
			self.chain.genesis_block(participants, self.wallet.address)
			self.wallet.add_transaction(self.chain.list_blocks[0].listOftransactions[0])
			transaction_outputs = {					'id':  uuid4().hex,
													'transactions_id': self.chain.list_blocks[0].listOftransactions[0]["transaction_id"],
													'value': self.chain.list_blocks[0].listOftransactions[0]["value"],
													'recipient': self.chain.list_blocks[0].listOftransactions[0]["recipient_address"]}
			#print(transaction_outputs)
			self.wallet.UTXOs.append(transaction_outputs)
			
   
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
		#time.sleep(1)
		self.seen += 1
		if (self.seen == self.participants):
			print("All in")
			self.child.set()
		return


	def send_the_ring(self):
		self.child.wait()
		
		time.sleep(2)
		for i, ring in enumerate(self.ring[1:]):
			self.send(i+1, ring)
		time.sleep(2)
		#time.sleep(3)

		self.chain.get_addresses(self.ring,self.ip,self.port)
	
		self.wallet_dict={}
   
		for public_key in self.public_key_list:
			self.wallet_dict[public_key] = []
   
		for i, ring in enumerate(self.ring[1:]):
			if  not no_mine.isSet():
				no_mine.wait()
			self.send_transactions(i+1,self.public_key_list[i+1])
			
		return
  
  
	def send(self, identity,ring):
		print("Bootstrap send to Node with identity {}".format(identity))
		#time.sleep(3)
		data = {
            'id': identity,
            'ring': self.ring,
            'public_key_list': self.public_key_list,
            'genesis': self.chain.list_blocks[0].block_to_json() 
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
		self.chain.get_addresses(self.ring,self.ip,self.port)
		self.public_key_list = copy.deepcopy(pub)
  
		self.wallet_dict={}
		for public_key in self.public_key_list:
			self.wallet_dict[public_key] = []
		
		genesis = json.loads(genesis)
		#print(genesis)
		new_index=genesis['index']
		new_trans=genesis['transactions']
		new_pre=genesis['previous_hash']
		gen = Block(new_index, new_trans, new_pre)
		gen.nonce=genesis['nonce']
		gen.timestamp=genesis['timestamp']
		self.chain.list_blocks.append(gen)
		trans_block_list = genesis['transactions'][0] # list
		trans = trans_block_list 
		#self.chain.list_transactions.append(trans)

		current_trans = {
            'transaction_id': trans['transaction_id'],
            'value': trans['value'],
            'receiver': trans['recipient_address']
        }

		self.wallet_dict[self.public_key_list[0]].append(current_trans)
		self.auto_run.set()
		return

   
	def send_transactions(self,i,receiver_address):
		print("send 100 to {} node".format(i))
		self.create_transaction(self.public_key_list[0],receiver_address,100)
		print("Boss balance", self.wallet.mybalance())
		self.auto_run.set()
   
#--------------------------------------TRANSACTIONS----------------------------------------
 
	def create_transaction(self, sender,receiver_address, value):
		#remember to broadcast it
		sent_value = 0
		transaction_inputs = []
		flag = False
		for i, utxo in enumerate(self.wallet.UTXOs):
			if utxo['recipient'] == self.wallet.address:
				sent_value += utxo['value']
				transaction_inputs.append(utxo['id'])
				if sent_value >= value:
					try:
						self.wallet.UTXOs = self.wallet.UTXOs[i+1:]
					except:
						self.wallet.UTXOs = []
					flag = True
					break
		
		if flag:
			new_transaction = Transaction(sender,receiver_address, value, transaction_inputs)
			new_transaction.transaction_outputs = [{'id':  uuid4().hex,
													'transactions_id': new_transaction.transaction_id,
													'value': value,
													'recipient': receiver_address},
												   {'id':  uuid4().hex,
													'transactions_id': new_transaction.transaction_id,
													'value': sent_value-value,
													'recipient':sender}]
			
			self.wallet.UTXOs.extend(new_transaction.transaction_outputs)
			self.wallet_dict[receiver_address].append(new_transaction.transaction_outputs[0])
			new_transaction.Signature = new_transaction.sign_transaction(self.wallet.private_key,new_transaction)
   

			self.broadcast_transaction(new_transaction)
			self.chain.add_transaction(new_transaction)

   		
			return 
		
		else:
			print("Invalid transaction (balance is not enough)")
			return False

#--------------------------------------BROADCASTS-----------------------------------------------------

	def broadcast_transaction(self, transaction):
		data=json.dumps(transaction.transaction_to_json())
		for rin in self.ring:
			address = rin + '/broadcast/transaction'
			if rin != ("http://" + str(self.ip) + ":"+ str(self.port)):
				response = requests.post(address, data=data,headers=headers)
				if response.status_code != 200:
					return False
		return True
#--------------------------------------VALIDATIONS-----------------------------------------------------

	def validate_tran(self,tran):
		val_tran=Transaction(tran["sender"], tran["receiver"], tran["value"],tran["inputs"])

		val_tran.transaction_outputs = tran["outputs"]
		val_tran.Signature = tran["signature"]
		val_tran.transaction_id=tran["tran_id"]
		if (val_tran.verify_signature(val_tran.sender_address,tran["signature"],val_tran)==True):
			print("verify -> ok")

			self.wallet.UTXOs.extend(val_tran.transaction_outputs)
			self.wallet.transactions.append(val_tran)
			self.chain.add_transaction(val_tran)
   		
			return True 
		else:	
			print("verify -> not ok")
			return False

	def validate_block(self,block):
		block = json.loads(block)
		#print(block['previous_hash'])
		if  block['previous_hash'] != self.chain.list_blocks[-1].myHash():
			print("valid block -> not ok")
			no_mine.set()
			self.auto_run.wait()
			self.chain.mine.set()
			self.consesus = threading.Event()
			self.consesus.clear()
			thread3 = threading.Thread(target=self.valid_chain)  # target to auto run trans
			thread3.start()
			return False
		else:
			new_block = Block(block['index'],block['transactions'],block['previous_hash'])
			new_block.timestamp = block['timestamp']
			new_block.nonce=block['nonce']
			if new_block.myHash()==(block['cur_hash']):
				self.chain.mine.set()
				#print(2)
				print("valid block -> ok")
				self.chain.add_block(new_block)
				return True
			else:
				return False

#--------------------------------------CONSENSUS-----------------------------------------------------
	def valid_chain(self):
		self.auto_run.wait()
		#check for the longer chain across all nodes
		chains = []
		for rin in self.ring:
			address = rin + '/send_chain'
			if rin != ("http://" + str(self.ip) + ":"+ str(self.port)):
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
		self.chain.list_blocks=self.valid_chain()
		return self.auto_run.set()

#--------------------------------------VIEWS-----------------------------------------------------

	def view_transactions(self):
		return self.chain.list_blocks[-1].listOftransactions

	def view_balance(self):
		return self.wallet.mybalance()



#---------AYTO RUN-------#



	def run_all_trans(self):
     
		self.auto_run.wait()  # w8 until trigger
		time.sleep(5)
		print('Check if genesis got in..')
		if not no_mine.isSet():
			no_mine.wait()
      
		print('Starting auto...')
        
		with open('/Users/tassos/Desktop/22-23/Distributed-Systems-Assignment/transactions /5nodes/transactions' + str(self.id) + '.txt', 'r') as fd:
			for line in fd:  # go through all lines and make transactions
				rec, ammount = (line.strip('\n')).split(' ')
				n=self.id	
				time.sleep(n)
				url = 'http://' + str(self.ip) + ':' + str(self.port) + "/create_transaction"
				payload = {'address': rec[2], 'amount': ammount}  # give data as in cli form, [id, ammount]
				payload = json.dumps(payload)
				response = requests.post(url, data=payload,
                                         headers={'Content-type': 'application/json',
                                                  'Accept': 'text/plain'})  # hit API
                # print(response.json())
			time.sleep(1)  # sleep 1 sec and repeat

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