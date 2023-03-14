import requests

from blockchain import Blockchain
from wallet import Wallet
from block import Block
from transaction import Transaction
from transactionIn import TransactionInput


CAPACITY = 4
DIFFICULTY = 2

class node:
	def __init__(self):
		self.id = None
		self.blockchain = Blockchain()
		self.capacity = None
		self.id = None
		self.NBCs = 0;
		self.wallet = Wallet()
		self.active_block = None
		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
	
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

	#def validate_transaction():
		#use of signature and NBCs balance

	#def add_transaction_to_block():
		#if enough transactions  mine

	#def mine_block():

	#def broadcast_block():

	#def valid_proof(.., difficulty=MINING_DIFFICULTY):

	#concencus functions

	#def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	#def resolve_conflicts(self):
		#resolve correct chain



