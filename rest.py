import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time
time.clock = time.time

from block import Block
from node import node, statistics
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction
import json  
import pickle   
import threading
from datetime import datetime 
import numpy as np

app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


#.......................................................................................

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

            print("Initializing...")
            
            time.sleep(1)
            start = time.time()
            initial_transaction = node_.create_transaction(node_.wallet.address, node_.total_nodes*100, initial_transaction=True)
            node_.broadcast_transaction(initial_transaction)
            node_.add_transaction_to_block(initial_transaction, node_.blockchain.chain[-1])
            end = time.time()
            statistics["Throughput"].append(end-start)

            for node in node_.ring:
                if node['id'] != node_.id:
                    start = time.time()
                    new_transaction = node_.create_transaction(node['public_key'], 100)
                    node_.broadcast_transaction(new_transaction)
                    node_.add_transaction_to_block(new_transaction, node_.blockchain.chain[-1])
                    end = time.time()
                    statistics["Throughput"].append(end-start)
            
            time.sleep(2)
            print('End of initialization!')

            node_.broadcast_init_finished()
            node_.read_transactions()

            time.sleep(2)
            node_.resolve_conflicts()
            print()
            print()
            print("Throughput: ",np.mean(statistics["Throughput"]))
            print("Block time:", np.mean(statistics["Block time"]))
            print()
            print()

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
    #print("received transaction...", datetime.now())
    data = pickle.loads(request.get_data())
    if data.sender_address == "0":
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
    #print('block broadcasted:', datetime.now())
    data = pickle.loads(request.get_data())
    if node_.validate_block(data) or data.previous_hash ==  "1":
        node_.blockchain.add_block(data)
        return jsonify({"Broadcast": "Done"}), 200
    else:
        node_.resolve_conflicts()
        return jsonify({"Broadcast": "Done"}), 200
    #print(len(node_.blockchain.chain), node_.blockchain.chain[-1].hash)

#broadcast init finished

@app.route('/broadcast/init_finished', methods = ['POST'])
def get_init_finished():
    data = json.loads(request.get_data())
    #print(data)
    if data != None:
        node_.read_transactions()
        #print(transactions)
                
    return jsonify(data), 200

#broadcast chain (consensus)    
   
@app.route('/broadcast/chain', methods=['POST'])
def get_chain():
    data = pickle.loads(request.get_data())
    node_.blockchain.chain = data
    return jsonify({"Consensus": "Done"}), 200

#get longest chain (consensus)

@app.route('/send_chain', methods = ['GET'])
def send_chain():
    return pickle.dumps(node_.blockchain.chain), 200

#broadcast statistics

@app.route('/broadcast/statistics', methods = ['POST'])
def get_statistics():
    data = json.loads(request.get_data())
    if data != None:
        statistics["Throughput"].extend(data["Throughput"])
        statistics["Block time"].extend(data["Block time"])

    return jsonify({"Statistics": "Taken"}), 200

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
    app.run(host=args.ip, port=args.port, debug=True, use_reloader=False)

    '''print('Length of blockchain: ', len(node_.blockchain.chain))
    for i, block in enumerate(node_.blockchain.chain):
        print('Block {}:'.format(i))
        print('Previous hash:', block.previous_hash)
        print('Current hash:', block.hash)'''


    print('Length of blockchain: ', len(node_.blockchain.chain))
    print('Balance : ', node_.wallet.balance())
    #print('UTXOs : ', node_.wallet.UTXOs)
    print(len(node_.wallet.UTXOs))
    total = 0
    for utxo in node_.wallet.UTXOs:
        total+= utxo['amount']
    print(total)
