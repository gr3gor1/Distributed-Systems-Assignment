from block import Block
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from node import Node

#test block class

#create bloc
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

#test transaction class

#create transaction instance

#sign transaction

#stringify transaction


#test node class

#create a node
node = Node()
#create a block
node.create_new_block()
#register node to ring
node.register_node_to_ring("192.168.1.2","id0",3000,node.wallet.public_key,200)
#add block to node's blockchain
node.blockchain.add_block(node.active_block)
#check if the initial block is valid
node.validate_block(node.active_block)
