import block
import wallet
import blockchain

class node:
	def __init__(self,bootstrap=False):
		self.boot = bootstrap
		self.blockchain = blockchain.Blockchain()
		self.pending_transactions = []
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
		for transaction in self.pending_transactions:
			new_block.add_transaction(transaction)
		self.pending_transactions = []
		new_block.hash = new_block.myHash()
		return new_block

	def create_wallet(self,amount=0):
		#create a wallet for this node, with a public key and a private key
		self.wallet = wallet.walletWallet(amount)

	#def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

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



