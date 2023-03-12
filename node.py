import block
import wallet
import blockchain
import requests

CAPACITY = 4

class node:
	def __init__(self,ip,port,bootstrap=False):
		self.ip = ip
		self.port = port
		self.boot = bootstrap
		self.blockchain = blockchain.Blockchain()
		self.uncomplete_transactions = []
		self.id = None
		self.NBCs=500 ;
		self.NBC = 0;
		self.wallet = None
		self.ring = {}   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

	def create_genesis_block(self):
		if self.ip == '192.168.1.2' and self.boot:
			self.blockchain.create_genesis_block()
	
	def create_new_block(self):
		previous_block = self.blockchain.chain[-1]
		index = previous_block.index + 1
		previous_hash = previous_block.hash
		new_block = block.Block(index, previous_hash)
		pending_transactions = self.uncomplete_transactions[:CAPACITY]
		for transaction in pending_transactions:
			new_block.add_transaction(transaction)
		self.uncomplete_transactions = self.uncomplete_transactions[CAPACITY:]
		new_block.hash = new_block.myHash()
		return new_block

	def create_wallet(self,amount=0):
		#create a wallet for this node, with a public key and a private key
		self.wallet = wallet.walletWallet(amount)

	def register_node_to_ring(self,address):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
		if self.boot:
			return ("I am bootstrap node")
		
		data = {'ip':self.ip,'port':self.port}
		response = requests.post(address+"/add_node",json=data)

		if response.status_code == 200:
			result = response.json()
			self.id = result.id
			self.ring = result['ring']
			self.wallet.total = result['total_wallet_amount']
			return result
		else:
			return None

	#def create_transaction(sender, receiver, signature):
		#remember to broadcast it

	#def broadcast_transaction():

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



