import requests
import socket
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


import block
import node
import blockchain
import wallet
import transaction
import wallet
from api import api,node




## in this file we will initialize the node and its registration

app = Flask(__name__)
CORS(app)

#add the subsection that provides the actual functionalities
app.register_blueprint(api)

#bootstrap
boot_ip = '192.168.1.2'
boot_port = '5000'
boot = True

#set the node's ip
name = socket.gethostname() 
ip = socket.gethostbyname(name)

# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="noobcash api")
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-N',"--number_of_nodes", type=int, help="number of nodes in the network")
    parser.add_argument('-c','--capacity',type=int, help="capacity of each block")
    parser.add_argument('-d','--difficulty',type=int, help="difficulty of mining procedure")
    args = parser.parse_args()
    port = args.port

#set difficulty,capacity,number of peers in the network
api.peers = args.N
node.capacity = args.c
node.difficulty = args.d

#if this is not the bootstrap node

app.run(host='127.0.0.1', port=port)