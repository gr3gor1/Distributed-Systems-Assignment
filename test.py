from block import Block
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from node import Node

#test block class

#create block
bl = Block(0,1)
#check attributes after initial creation
bl.stringify()
#utilize myHash() function inside Block class
a = bl.myHash()
#set hash value in block 
bl.hash = a
#check the added values inside block
bl.stringify()

#test blockchain class

#create blockchain
blchain = Blockchain()
#print current chain
blchain.stringify_chain()
#add block in blockchain
blchain.add_block(bl)
#show current contents in chain 
blchain.stringify_chain()
#print their content too
blchain.chain[0].stringify()

#test wallet class

#create a wallet
wallet = Wallet()
#show attributes of wallet class
wallet.stringify()
#show initial balance without any UTXOs
wallet.balance()

#test node class

#create a node
node = Node()
#create a block
node.create_new_block()
#register node to ring
node.register_node_to_ring("192.168.1.2","id0",3000,node.wallet.public_key,200)
#create hash of genesis block
node.active_block.hash = node.active_block.myHash()
#show genesis info
node.active_block.stringify()
#add block to node's blockchain
node.blockchain.add_block(node.active_block)
#create a new active block
node.create_new_block()
#give index 1 
node.active_block.index = 1
#give previousHash
node.active_block.previousHash = node.blockchain.chain[0].hash
#give current hash
node.active_block.hash = node.active_block.myHash()
#print block contents
node.active_block.stringify()
#check if the initial block is valid
node.validate_block(node.active_block)
#check the chain only with one block in it
node.valid_chain(node.blockchain)
#append active block in the chain
node.blockchain.add_block(node.active_block)
#check the current chain
node.valid_chain(node.active_block)
#create one more block
node.create_new_block()
#mine block
node.mine_block(node.active_block)
#check the block contents
node.active_block.stringify()

#need to test endpoints

#initialize a node


#need to test conflicts
#need to test transactions
