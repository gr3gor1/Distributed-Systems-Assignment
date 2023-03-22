import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time
time.clock = time.time

from block import Block
from node import node
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction
import json  
import pickle   
import threading
from datetime import datetime 


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


#.......................................................................................

@app.route('/', methods=['GET'])

def welcome():
    wl = '''
        <html>
        <head><title>Blockchain</title></head>
        <body>
        <h1>Blockchain</h1>
        Welcome to our Blockchain Page
        <br>
            <ul>
            <li>For Mining Blocks Visit : <a href="http://127.0.0.1:5000/mineblock">http://127.0.0.1:5000/mineblock</a></li>
            <li>For Viewing the Blockchain Visit : <a href="http://127.0.0.1:5000/getchain">http://127.0.0.1:5000/getchain</a></li>
            <li>For Validating Blockchain Visit : <a href="http://127.0.0.1:5000/validate">http://127.0.0.1:5000/validate</a></li>
            </ul>
        </body>
        </html>
        '''
    return wl

#send info to bootstrap

@app.route('/get_ring_info', methods=['POST'])
def get_info():
    data = request.get_json()
    if node_.register_node_to_ring(data):
        if len(node_.ring) == node_.total_nodes:
            if node_.broadcast_ring():
                print('Ring broadcasted')
            else:
                print('Failed to broadcast the ring.')

            if node_.broadcast_block(node_.blockchain.chain[0]):
                print('Genesis block broadcasted')
            else:
                print('Failed to broadcast the genesis block.')
            
            initial_transaction = node_.create_transaction(node_.wallet.address, node_.total_nodes*100, initial_transaction=True)
            node_.broadcast_transaction(initial_transaction)
            node_.add_transaction_to_block(initial_transaction, node_.blockchain.chain[-1])

            for node in node_.ring:
                if node['id'] != node_.id:
                    print()
                    print(1)
                    new_transaction = node_.create_transaction(node['public_key'], 100)
                    print()
                    print(2)
                    node_.broadcast_transaction(new_transaction)
                    print()
                    print()
                    print(len(node_.blockchain.chain), node_.blockchain.chain[-1].transactions)
                    print()
                    print()
                    print()
                    print(3)
                    node_.add_transaction_to_block(new_transaction, node_.blockchain.chain[-1])

            #print(len(node_.blockchain.chain), node_.blockchain.chain[-1].hash)

            #print(len(node_.blockchain.chain))
            #print(node_.blockchain.chain[-1].hash)

        return jsonify(data), 200
    else:
        print('Failed to register node.')

#broadcast ring 

@app.route('/broadcast/ring', methods=['POST'])
def get_ring():
    data = json.loads(request.get_data())
    if data != None:
        node_.ring = data
        print('Got the ring!')
        return jsonify({"Broadcast": "Done"}), 200
    else:
        print('Failed to broadcast the ring.')
        return jsonify({"Broadcast": "Failed"}), 400

#broadcast transaction        
   
@app.route('/broadcast/transaction', methods=['POST'])
def get_transaction():
    print("received transaction...", datetime.now())
    data = pickle.loads(request.get_data())
    if data.sender_address == "0":
        node_.add_transaction_to_block(data, node_.blockchain.chain[-1])
        print()
        print()
        print(len(node_.blockchain.chain), node_.blockchain.chain[-1].transactions)
        print()
        print()
        
        new_utxos = []
        for utxo in node_.wallet.UTXOs:
            flag = True
            for utxo_id in data.transaction_inputs:
                if utxo['id'] == utxo_id:
                    flag = False
            if flag:
                new_utxos.append(utxo)

        node_.wallet.UTXOs = new_utxos.copy()
        node_.wallet.UTXOs.extend(data.transaction_outputs)
        return jsonify({"Broadcast": "Done"}), 200

    else:
        if node_.verify_signature(data):
            node_.add_transaction_to_block(data, node_.blockchain.chain[-1])
            new_utxos = []
            for utxo in node_.wallet.UTXOs:
                flag = True
                for utxo_id in data.transaction_inputs:
                    if utxo['id'] == utxo_id:
                        flag = False
                if flag:
                    new_utxos.append(utxo)

            node_.wallet.UTXOs = new_utxos.copy()
            node_.wallet.UTXOs.extend(data.transaction_outputs)
            return jsonify({"Broadcast": "Done"}), 200

        else:
            print('Invalid signature')
            return jsonify({"Broadcast": "Failed"}), 400


#broadcast block        
   
@app.route('/broadcast/block', methods=['POST'])
def get_block():
    print('block broadcasted:', datetime.now())
    data = pickle.loads(request.get_data())
    node_.blockchain.add_block(data)
    #print(len(node_.blockchain.chain), node_.blockchain.chain[-1].hash)
    return jsonify({"Broadcast": "Done"}), 200

#broadcast chain        
   
@app.route('/broadcast/chain', methods=['POST'])
def get_chain():
    data = request.get_json()
    node_.blockchain.chain = data
    return jsonify(data), 200
   
#get the balance of a node

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = node_.wallet.balance()
    response = {'Balance': balance}
    return jsonify(response), 200

#get the transactions of the last confirmed block of the blockchain

@app.route('/transactions', methods=['GET'])
def get_transactions_of_the_last_block():
    transactions = node_.chain[-1].transactions
    response = {'Transactions': transactions}
    return jsonify(response), 200

# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return jsonify(response), 200

# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-id', default=0, type=int, help='id of the node')    
    parser.add_argument('-bootstrap', default=1, type=int, help='is this the bootstrap node?')
    parser.add_argument('-ip', default='127.0.0.1', type=str, help='ip of the node')
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-nodes', default=2, type=int, help='number of nodes')
    args = parser.parse_args()

    node_ = node(args.id, args.bootstrap, args.ip, args.port, blockchain, args.nodes)
    #thread = threading.Thread(target=app.run(host=args.ip, port=args.port, debug=True, use_reloader=False))
    #thread.start()
    app.run(host=args.ip, port=args.port, debug=True, use_reloader=False)

    print('Length of blockchain: ', len(node_.blockchain.chain))
    for i, block in enumerate(node_.blockchain.chain):
        print('Block {}:'.format(i))
        print('Previous hash:', block.previous_hash)
        print('Current hash:', block.hash)

    print('Balance : ', node_.wallet.balance())
    print('UTXOs : ', node_.wallet.UTXOs)