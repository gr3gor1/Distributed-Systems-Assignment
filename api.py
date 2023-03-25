import requests
import json
import time
import pickle
import os
from threading import Thread 
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
@api.route('/conflict_chain', methods = ['GET'])
def conflict_chain():
    return pickle.dumps(node.blockchain)

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
            else:
                node.lock_chain.release()
                return jsonify({'status':'REJECTED'}), 400
            
    return jsonify({'status':"SUCCESS"}), 200

#show balance of the client in the local node
@api.route('/money',methods = ['GET'])
def money():
    return jsonify({"message":str(node.wallet.balance())}), 200

#show local transactions of the last block
@api.route('/last_transactions', methods = ['GET'])
def last_transactions():
    latest_block = node.blockchain.chain[-1]
    transactions = latest_block.listOfTransactions
    export = []
    for i in transactions:
        b = {'sender':None,'recipient':None,'value':None}
        b['sender'] = 'id' + str(i.sender)
        b['recipient'] = 'id' + str(i.receiver)
        b['value'] =  str(i.amount)
        export.append(b)
    return jsonify(export),200

#make a new transaction
@api.route('/transaction', methods = ['POST'])
def transaction():
    #turn the data we received from string to int
    recipient_id = str(request.json.get('id'))
    #the node should not be able to send money to itself
    if recipient_id != str(node.id):
        value = request.json.get('amount')
        id = None
        pub = None
        #then we search for info about the node with the
        #id that is provided from the client
        for peer in node.ring:
            if str(peer['id']) == recipient_id:
                if (peer['pub']!=None):
                    id = peer['id']
                    pub = peer['pub']

        check = node.create_transaction(id,pub,int(value))
        if (check==True):
            return jsonify({"message":"SUCCESS"}),200
        else: 
            return jsonify({'message': 'FAILURE'}),400
    else:
            return jsonify({"message":'Wrong id'}), 400

@api.route('/five_nodes', methods=['GET'])
def five_nodes():
    def dummy(peer,ans):
        address = 'http://' + peer['ip'] + ':' + str(peer['port']) + '/init5'
        response = requests.get(address)
        ans.append(response.status_code)

    ans = []
    for peer in node.ring:
        thread = Thread(target=dummy,args=(peer,ans))
        thread.start()
    
    for i in ans:
        if i != 200:
            return 300
        
    return json.dumps({'ans':ans}) , 200

@api.route('/init5',methods = ['GET'])
def init5():
    id = node.id
    credentials = None
    for cred in node.ring:
        if str(cred['id']) == str(id):
            credentials = cred
           
    address =  'http://' + credentials['ip'] + ':' + str(credentials['port']) + '/transaction'
    file = os.path.join('/home/user/5nodes','transactions'+str(node.id)+'.txt')
    with open(file,'r') as text:
        for line in text:
            line = line.split()
            recipient = int(line[0][2])
            amount = int(line[1])
            string = {'id':recipient,'amount':amount}
            response = requests.post(address,json=string)
            if response.status_code == 200:
                print('Transaction completed')
            else:
                print('Failure')

    return '',200

@api.route('/ten_nodes', methods=['GET'])
def ten_nodes():
    def dummy(peer,ans):
        address = 'http://' + peer['ip'] + ':' + str(peer['port']) + '/init10'
        response = requests.get(address)
        ans.append(response.status_code)

    ans = []
    for peer in node.ring:
        thread = Thread(target=dummy,args=(peer,ans))
        thread.start()
    
    for i in ans:
        if i != 200:
            return 300
        
    return json.dumps({'ans':ans}) , 200

@api.route('/init10',methods = ['GET'])
def init10():
    id = node.id
    credentials = None
    for cred in node.ring:
        if str(cred['id']) == str(id):
            credentials = cred
           
    address =  'http://' + credentials['ip'] + ':' + str(credentials['port']) + '/transaction'
    file = os.path.join('/home/user/10nodes','transactions'+str(node.id)+'.txt')
    with open(file,'r') as text:
        for line in text:
            line = line.split()
            recipient = int(line[0][2])
            amount = int(line[1])
            string = {'id':recipient,'amount':amount}
            response = requests.post(address,json=string)
            if response.status_code == 200:
                print('Transaction completed')
            else:
                print('Failure')

    return '',200

@api.route('/temp', methods=['GET'])
def temp():
    def dummy(peer,ans):
        address = 'http://' + peer['ip'] + ':' + str(peer['port']) + '/temp_init'
        response = requests.get(address)
        ans.append(response.content)

    ans = []
    for peer in node.ring:
        thread = Thread(target=dummy,args=(peer,ans))
        thread.start()
    
    for i in ans:
        if i != 200:
            return 300
        
    return json.dumps({'ans':ans}) , 200

@api.route('/temp_init',methods = ['GET'])
def temp_init():
    time_counter = 0
    transaction_counter = 0

    id = node.id
    credentials = None
    for cred in node.ring:
        if str(cred['id']) == str(id):
            credentials = cred
           
    address =  'http://' + credentials['ip'] + ':' + str(credentials['port']) + '/transaction'
    file = os.path.join('/home/user/5small','transactions'+str(node.id)+'.txt')
    with open(file,'r') as text:
        for line in text:
            line = line.split()
            recipient = int(line[0][2])
            amount = int(line[1])
            string = {'id':recipient,'amount':amount}
            start = time.time()
            response = requests.post(address,json=string)
            stop_time = time.time() - start
            if response.status_code == 200:
                time_counter += stop_time
                transaction_counter += 1
            else:
                print('Failure')

    return '',200



