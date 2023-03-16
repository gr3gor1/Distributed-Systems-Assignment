import requests
from flask import Flask, jsonify, request, render_template

import sys
import json
from node import node, no_mine
from transaction import Transaction
from blockchain import Blockchain
from block import Block
from flask_cors import CORS





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
        return "Error:No valid address", 400
    #print(mykey)
    master.register_node(ad, pub)
    response = {'message': 'ok'}
    return jsonify(response), 200



# run it once fore every node

if __name__ == '__main__':

    app.run(host=sys.argv[2], port=int(sys.argv[3]))