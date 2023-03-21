from block import Block
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from node import Node

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
import binascii

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
#show initial balance without any UTXOs (expects 0)
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
#print block contents (expect nonce = None because we created block 
# manually and did not use mine_block())
node.active_block.stringify()
#check if the initial block is valid
node.validate_block(node.active_block)
#check the chain only with one block in it
node.valid_chain(node.blockchain)
#append active block in the chain
node.blockchain.add_block(node.active_block)
#check the current chain
node.valid_chain(node.blockchain)
#create one more block
node.create_new_block()
#set DIFFICULTY
node.DIFFICULTY = 4
#mine block
node.mine_block(node.active_block)
#check the block contents
node.active_block.stringify()

#test transaction class

#create pair of keys 1
random1 = RSA.generate(1024)
private_key1 = random1.exportKey().decode()
public_key1 = random1.publickey().exportKey().decode()
#create pair of keys 2
random2 = RSA.generate(1024)
private_key2 = random2.exportKey().decode()
public_key2 = random2.publickey().exportKey().decode()
#check that the keys are not the same (should print False)
print(private_key1 == private_key2)
#create transaction from 1 to 2
a = Transaction(sender_address=public_key1,sender_id='0',recipient_address=public_key2,recipient_id="9",value=100,NBCs=100,transactionIn=None)
#let 1 sign transaction
print(a.sign_transaction(private_key1))
#let 2 verify transaction with 
print(a.validate_transaction())

#test endpoints