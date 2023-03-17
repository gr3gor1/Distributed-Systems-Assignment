import requests
import json
from threading import Thread, Lock
from copy import deepcopy
import itertools


from blockchain import Blockchain
from wallet import Wallet
from block import Block
from transaction import Transaction
from transactionIn import TransactionInput


CAPACITY = 4
DIFFICULTY = 2

class Node:
	def __init__(self):
		self.id = None
		self.blockchain = Blockchain()
		self.NBCs = 0;
		self.wallet = Wallet()
		self.active_block = None
		self.mining_flag = False 
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
		self.to_check = [] #blocks that need to be checked

		#locks we will need to make sure certain data are manipulated simultaneously
		self.lock_block = Lock()
		self.lock_chain = Lock()
		self.lock_temp = Lock()
	
	def create_new_block(self):
		#if blockchain is empty then we create genesis block
		if len(self.blockchain.chain) == 0:
			index = 0
			previous_hash = 1
			self.active_block = Block(index,previous_hash)
		else:
			#we create a block instance that will be updated later on
			self.active_block = Block(None,None)
		return self.active_block

	def register_node_to_ring(self,ip,id,port,pub,balance):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.ring.append({'ip':ip,'port':port,'id':id,'balance':balance,'pub':pub})
	
	def create_transaction(self,r_id, r_address, value):
		#remember to broadcast it
		transaction_ins = []
		transaction_ids = []
		amount_sent = 0
		#add the UTXOs up to this point in the transaction inputs list
		for transaction in self.wallet.transactions:
			for out in transaction.transaction_outputs:
				if(out.recipient == self.wallet.public_key.hex & out.unspent):
					transaction_ins.append(TransactionInput(transaction.transaction_id))
					transaction_ids.append(transaction.transaction_id)
					out.unspent = False
					amount_sent += out.value
			#if we have enough money to sent then break
			if amount_sent >= value :
				break

			#if we dont we turn the transactions to unspent
			if amount_sent < value :
				for transaction in self.wallet.transactions:
					for out in transaction.transaction_outputs:
						if out.transactionId in transaction_ins:
							out.unspent = True

				return False
			
			#create Transaction
			transaction = Transaction(
				sender_address=self.wallet.public_key_hex,
				sender_id= self.id,
				recipient_address= r_address,
				recipient_id= r_id,
				value = value,
				transactionIn=transaction_ins,
				NBCs = amount_sent
			)

			transaction.sign_transaction(self.wallet.private_key_hex)

			if (self.broadcast_transaction(transaction) != True):
				for transaction in self.wallet.transactions:
					for out in transaction.transaction_outputs:
						if out.transaction_id in transaction_ids:
							out.unspent = True
				return False
			
			return True
	
	def broadcast_transaction(self,transaction):
	#we will create a function and then we will create N threads
	#and then we will hit the same endpoint on each node in the network
	#at first we seek validation of th transaction
		def dummy(peer,res,endpoint):
			if peer['id'] != self.id:
				address = "http://" + peer['ip'] + ":" + peer['port']
				response = requests.post(address + endpoint,data=json.dumps(transaction.stringify()))
				res.append(response.status_code)

		to_close = []
		ans = []

		for peer in self.ring:
			thread = Thread(target=dummy, args=(peer,ans,'/broadcast_transaction'))
			to_close.append(thread)
			thread.start()

		for i in range(len(ans)):
			to_close[i].join()
			if ans[i] != 200:
				return False
			
		#secondly after validation we need to add it in the block	
		to_close = []
		ans = []

		for peer in self.ring:
			thread = Thread(target=dummy, args=(peer,ans,"/add_transaction"))
			to_close.append(thread)
			thread.start()

		self.add_transaction_to_block(transaction)
		return True
	
	def validate_transaction(self,transaction):
		#use of signature and NBCs balance
		if (transaction.validate_transaction() == False):
			return False
		
		for peer in self.ring:
			if peer['pub'] == transaction.sender_address:
				if peer['balance'] >= transaction.amount:
					return True
		return False

	def add_transaction_to_block(self,transaction):
		#if enough transactions  mine
		if (transaction.receiver_address == self.wallet.public_key_hex):
			self.wallet.transactions.append(transaction)
		if (transaction.sender_address == self.wallet.private_key_hex):
			self.wallet.transactions.append(transaction)

		for peer in self.ring:
			if peer['pub'] == transaction.sender_address:
				peer['balance'] -= transaction.amount
			if peer['pub'] == transaction.receiver_address:
				peer['balance'] += transaction.amount

		if self.active_block == None:
			self.active_block = self.create_new_block()

		self.lock_block.acquire()
		if self.active_block.add_transaction(transaction,CAPACITY):
			self.to_check.append(deepcopy(self.active_block))
			self.active_block = self.create_new_block()
			self.lock_block.release()
			while True:
				with self.lock_temp:
					if(self.to_check):
						mine = self.to_check[0]
						fin = self.mine_block(mine)
						if (fin):
							break
						else:
							self.to_check.insert(0,mine)
					else:
						return
			self.broadcast_block(mine)
		else:
			self.lock_block.release()	

	def mine_block(self,block):
		block.nonce = 0
		block.index = self.blockchain.chain[-1].index + 1
		block.previous_hash = self.blockchain.chain[-1].hash
		current_hash = block.myHash()
		while(current_hash.startsWith('0'*DIFFICULTY) == False & self.mining_flag==False):
			block.nonce +=1
			current_hash = block.myHash()
		block.hash = current_hash

		return not self.mining_flag

	def broadcast_block(self,block):
		#if the new block we just mined is recognised from at least one
		#node then add it in the chain

		def dummy(peer,res):
			address = 'http://' + peer['ip'] + ":" + peer['port']
			response = requests.post(address + '/broadcast_block',data=json.dumps(block))
			res.append(response.status_code)

		to_close = []
		ans = []

		for peer in self.ring:
			thread = Thread(target= dummy, args =(peer,ans))
			to_close.append(thread)
			thread.start()

		accepted = False

		for i in range(len(to_close)):
			to_close[i].join()
			if ans[i] == 200:
				accepted = True

		if (accepted == True):
			with self.lock_chain:
				if self.validate_block(block):
					self.blockchain.chain.add_block(block)

	def validate_block(self,block):
		condition1 = False
		condition2 = False
		
		if (block.previousHash == self.blockchain.chain[-1].hash):
			condition1 = True 
			print(condition1)

		if (block.hash == block.myHash()):
			condition2 = True
			print(condition2)

		return (condition1 & condition2)
			
	#concencus functions

	def valid_chain(self, chain):
		#check if the chain we received is valid after a conflict
		chainOfBlocks = chain.chain
		condition1 = False
		condition2 = False

		for index in range(len(chainOfBlocks)):
			if index == 0 :
				if(chainOfBlocks[index].hash != 1 or chainOfBlocks[index].hash != chainOfBlocks[index].myHash()):
					return False
				else:
					if(chainOfBlocks[index].hash == chainOfBlocks[index].myHash()):
						condition1 = True
					if(chainOfBlocks[index].previousHash == chainOfBlocks[index-1].hash):
						condition2 = True
					if (condition1==False) or (condition2==False):
						return False
		return True
	
	def resolve_conflicts(self,block):
		#after broadcasts to concentrate all the chains we validate the incoming chains and then decide to stick with the longest one
		def dummy(peer,blockchains):
			address = "http://" + peer['ip'] + ':' + peer['port']
			response = requests.get(address + '/broadcast_chain')
			blockchain = json.dumps(response._content)
			blockchains.append(blockchain)

		threads = []
		blockchains = []

		for peer in self.ring:
			thread = Thread(target=dummy,args=(peer,blockchains))
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		winner = None
		for chain in blockchains:
			if winner:
				blockchain_length = len(chain.chain)
				winner_length = len(winner.chain)
				self_length = len(self.blockchain.chain)
				if (self.valid_chain(chain) & (blockchain_length>winner_length)):
					winner = chain
			else:
				if (self.valid_chain(chain) & (blockchain_length>self_length)):
					winner = chain

		if winner:
			self.mining_flag = True
			with self.lock_temp:
				index = len(winner.chain) - 1
				while(index>0 & ((winner.chain[index].hash != self.blockchain.chain[-1].hash))):
					index = index - 1

				for item in self.blockchain.chain[index+1:].reverse():
					self.to_check.insert(0,item)

				for item in winner.chain[index+1:]:
					self.check_doubles(item)


				self.blockchain.chain = winner.chain
				self.mining_flag = False
		return self.validate_block(block)

	def check_doubles(self,block):
		#check for double transactions between added block and blocks you still havent check
		with self.lock_block:
			#flatten list of transactions in unchecked blocks
			transactions = list(itertools.chain.from_iterable([ublock.tr for ublock in self.to_check]))

			if (self.active_block):
				transactions.extend(self.active_block.listOfTransactions)

			self.active_block.listOfTransactions = []

			filter_tr = []

			for tr in transactions:
				if(tr not in block.listOfTransactions):
					filter_tr.append(tr)

			if not self.to_check:
				self.active_block.listOfTransactions = deepcopy(filter_tr)
				return
			
			index = 0

			while ((index + 1) * CAPACITY<= len(filter_tr)):
				self.to_check[index].listOfTransactions = deepcopy(filter_tr[(index * CAPACITY):((index + 1) * CAPACITY)])
				index = index + 1

			if (index * CAPACITY) < len(filter_tr):
				self.active_block.listOfTransactions = deepcopy(filter_tr[(index * CAPACITY):])

			for item in range(len(self.to_check)-index):
				self.to_check.pop()
		return

	def announce_ring(self,node):
		address = 'http://' + node['ip'] + ':' + node['port']
		requests.post(address + '/share_ring', data = json.dumps(self.ring))

	def announce_chain(self,node):
		address = 'http://' + node['ip'] + ':' + node['port']
		requests.post(address + '/share_chain',data = json.dumps(self.blockchain.chain))



