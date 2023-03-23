import requests
from flask import Flask, jsonify, request, render_template

import sys
import json
from node import node, no_mine
from transaction import Transaction
from blockchain import Blockchain
from block import Block
from flask_cors import CORS
import pickle
import time
from node import consesus





### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)

# id,ip,port, number of participants, father or no father
master = node(int(sys.argv[1]),sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])

#.......................................................................................



# send your address in bootstrap

@app.route('/bootstrap/register', methods=['POST'])
def register():
    print('someone send his identity')
    ad = request.json['address']
    pub= request.json['public_key']
    if (ad is None) or (pub is None):
        return "Error:No valid address or public key", 400
    master.register_node(ad, pub)
    response = {'message': 'ok'}
    return jsonify(response), 200

@app.route('/child/register',methods=['POST'])
def register_child():
    myid = request.json['id']
    ring = request.json['ring']
    pub = request.json['public_key_list']
    genesis = request.json['genesis']
    if myid is None:
        return "Error:No valid myid",400
    if ring is None:
        return "Error:No valid ring",400
    if pub is None:
        return "Error:No valid public keys",400
    master.recieve(myid,ring,pub,genesis)
    response = {'message': 'ok'}
    return jsonify(response), 200

@app.route('/broadcast/transaction', methods=['POST'])
def get_transaction():
    #data = pickle.loads(request.get_data())
    n=master.id	
    time.sleep(n%2)
    data = json.loads(request.get_json())
    if not no_mine.is_set():
        no_mine.wait()
    master.validate_tran(data)
    print("balanceeeeee:",master.wallet.mybalance())
    return jsonify({"Broadcast": "Done"}), 200

@app.route('/broadcast/block', methods=['POST'])
def get_block():
    data = request.get_json()
    #data = pickle.loads(request.get_data())
    print("someone send a block")
    #print(data)
    master.chain.mine.set()
    master.validate_block(data)
    #master.chain.mine.set()
    no_mine.set()
    #master.chain.add_block(data)
    return jsonify({"Broadcast": "Done"}), 200

@app.route('/create_transaction', methods=['POST'])
def create():
    data = request.get_json()
    addr = data['address']
    #print ("Address is",addr)
    amount = data['amount']
    # print("Amount is",amount)
    # current balance
    bal = master.wallet.mybalance()
    if (not addr.isnumeric() or int(addr) < 0 or int(addr) > master.participants):
        response = {
            'message': "Please provide a number between 0 and " + str(master.participants) + " as address."
        }
    elif (int(addr) == master.id):
        response = {
            'message': "You cannot make a transaction with yourself..."
        }
    elif (not amount.isnumeric() or int(amount) <= 0):
        response = {
            'message': "Please provide a positive number as amount."
        }
    elif int(amount) > bal:
        #print(bal)
        response = {
            'message': "Not enough money..."

        }
    else:
        # stall transaction till mining is done
        if not no_mine.is_set():
            no_mine.wait()

        sender = master.public_key_list[master.id]
        receiver = master.public_key_list[int(addr)]
       
        master.create_transaction(sender,receiver, int(amount))

        response = {
            'message': "Create transaction works !"
        }
    return jsonify(response), 200
        

@app.route('/send_chain', methods=['POST'])
def send_chain():
    #data = pickle.loads(request.get_data())
    print("hiiii")
    #consesus.clear()
    print("consesous")
    return pickle.dumps(master.chain.list_blocks)

# run it once fore every node

if __name__ == '__main__':

    app.run(host=sys.argv[2], port=int(sys.argv[3]))
    
    
    for i, block in enumerate(master.chain.list_blocks):
        print('Block {}:'.format(i))
        print('Previous hash:', block.previous_hash)
        print('Current hash:', block.myHash())
        print('Count Transactions:',len(block.listOftransactions))
    print("Balance:",master.wallet.mybalance())