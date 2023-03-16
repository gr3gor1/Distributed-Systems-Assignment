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
    node0.register_node_to_ring(data)
    return jsonify(data), 200

#get the balance of a node

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = node0.wallet.balance()

    response = {'Balance': balance}
    return jsonify(response), 200

#get the transactions of the last confirmed block of the blockchain

@app.route('/transactions', methods=['GET'])
def get_transactions_of_the_last_block():
    transactions = node0.chain[-1].transactions

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
    parser.add_argument('-bootstrap', default=True, type=bool, help='is this the bootstrap node?')
    parser.add_argument('-ip', default='127.0.0.1', type=str, help='ip of the node')
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()

    node0 = node(args.id, args.bootstrap, args.ip, args.port, blockchain.chain)
    app.run(host=args.ip, port=args.port, debug=True)