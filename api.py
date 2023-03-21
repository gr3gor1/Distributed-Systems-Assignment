import requests
import json
import time
import pickle
from flask import Blueprint,Flask, jsonify, request, render_template

from block import Block
from transaction import Transaction
from transactionIn import TransactionInput
from transactionOut import TransactionOutput
from node import Node

#create node instance
node = Node()

#set the subsection we will add later on to the main script
api = Blueprint('api',__name__)

#app functionality

#register node to the network
@api.route('/registration', methods = ['POST'])
def registration():
    ip = request.json.get('ip')
    port = str(request.json.get('port'))
    id = len(node.ring)
    pub = request.json.get('pub')

    node.register_node_to_ring(ip,id,port,pub,0)

    if (node.peers == id + 1):
        for peer in node.ring:
            node.announce_ring(peer)
            node.announce_chain(peer)
            if peer['id'] != node.id:
                node.create_transaction(peer['id'],peer['pub'],100)
    

    return jsonify({"status":"Registered"}),200
        

#learn the ring of the bootstrap node and set the id of the node
@api.route('/learn_ring',methods = ['POST'])
def learn_ring():
    load = request.json
    node.ring = load['data']
    #print('passed')
    for peer in node.ring:
        if peer['pub'] == node.wallet.public_key:
            node.id = peer['id']

    return jsonify({'status':'SUCCESS'}),200

#learn the chain of bootstrap node and initialize the local blockchain
@api.route('/learn_chain',methods = ['POST'])
def learn_chain():
    node.blockchain.chain = pickle.loads(request.get_data())
    return jsonify({'status':"ADDED"}) 

#send local chain to resolve conflicts
@api.route('/conflict_chain', methods = ['POST'])
def conflict_chain():
    return pickle.dumps(node.blockchain.chain)

#validate posted transaction
@api.route('/valid_transaction',methods=['POST'])
def valid_transaction():
    #get the transaction
    transaction = pickle.loads(request.get_data())
    if node.validate_transaction(transaction):
        return jsonify({'status':'OK'}), 200
    else:
        return jsonify({'status':'FAILURE'}), 400

#add valid transaction 
@api.route('/add_transaction',methods=['POST'])
def add_transaction():
    transaction = pickle.loads(request.get_data())
    node.add_transaction_to_block(transaction)
    return jsonify({'status':'OK'}), 200

#make sure an incoming block is valid and then insert it in the local node
@api.route('/check_block',methods = ['POST'])
def broadcast_block():
    block = pickle.loads(request.get_data())
    #make sure the chain is not in danger of being changed during the procedure
    node.lock_chain.acquire()
    if node.validate_block(block):
        #make sure mining is stopped
        node.mining_flag = True 
        with node.lock_temp : 
            node.blockchain.add_block(block)
            node.lock_chain.release()
            #clean double transactions
            node.check_doubles(block)
            #we can start mining again
            node.mining_flag = False
            return jsonify({'status':"SUCCESS"}), 200

    else:
        #check the validity of the block
        if block.previousHash == node.blockchain.chain[-1].hash:
            node.lock_chain.release()
            return jsonify({'status':'FAILED VALIDATION'}), 400
        else:
           #there has been some confilct that needs fixing
            if node.resolve_conflicts(block):
               #if resolved stop minining and add block to the chain
                node.mining_flag = True
                with node.lock_temp:
                    node.blockchain.add_block(block)
                    node.lock_chain.release()
                    #check double transactions
                    node.check_doubles(block)
                    #continue mining
                    node.mining_flag = False
                    return jsonify({'status':'SUCCESS'}), 200
            else:
                node.lock_chain.release()
                return jsonify({'status':'REJECTED'}), 400

#show balance of the client in the local node
@api.route('/money',methods = ['GET'])
def money():
    return jsonify({"message":str(node.wallet.balance())}), 200



