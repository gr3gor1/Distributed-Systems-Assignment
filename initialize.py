import requests
import json
import time
import socket
import threading
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


import block
import node
import blockchain
import wallet
from transaction import Transaction
import wallet
from api import api,node




## in this file we will initialize the node and its registration
app = Flask(__name__)

#add the subsection that provides the actual functionalities
app.register_blueprint(api)

CORS(app)



#bootstrap
boot_ip = '192.168.1.2'
boot_port = '5000'
boot = False

#set the node's ip
name = socket.gethostname() 
ip = socket.gethostbyname(name)

# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="noobcash api")
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-n',"--number_of_nodes", type=int, help="number of nodes in the network")
    parser.add_argument('-c','--capacity',type=int, help="capacity of each block")
    parser.add_argument('-d','--difficulty',type=int, help="difficulty of mining procedure")
    args = parser.parse_args()
    port = args.port

    #set difficulty,capacity,number of peers in the network
    node.peers = args.number_of_nodes
    node.CAPACITY = args.capacity
    node.DIFFICULTY = args.difficulty

    #if this is not the bootstrap node
    if not boot:
        #we use this thread in order to stall request
        #we need the request to be made after the server is initialized
        def fun():
            time.sleep(1)
            address = 'http://' + boot_ip + ':' + boot_port + '/registration'
            res = requests.post(address,json={'ip':ip,'port':port,'pub':node.wallet.public_key})
            
            
            if res.status_code == 200:
                print("Successfully initialized")


        thread = threading.Thread(target=fun)
        thread.start()

        app.run(host=ip,port=port)

    #if it is the bootstrap node
    else:
        #set the id to 0 initialize the ring
        node.id = 0
        node.register_node_to_ring(ip,node.id,port,node.wallet.public_key,node.peers*100)

        #create the genesis block using .create_new_block with blockchain.chain being empty
        genesis = node.create_new_block()
        genesis.nonce = 0

        #create the transaction of giving N*100 coins to the bootstrap node from 0 address
        transaction = Transaction(sender_address='0',sender_id='0',recipient_address=node.wallet.public_key,recipient_id=node.id,value=100*node.peers,NBCs=100*node.peers,transactionIn=None)
        
        #add the transaction in the genesis block
        genesis.add_transaction(transaction,node.CAPACITY)
        #add the transaction in the wallet of the node
        node.wallet.transactions.append(transaction)
        
        #create the hash of the block
        genesis.hash = genesis.myHash()
        
        #add genesis block (current active block) in the chain
        node.blockchain.add_block(node.active_block)
        
        #set the active block of bootstrap node to blank so that we can continue
        node.active_block = None
        
        #run app
        app.run(host=boot_ip,port=port)      
  