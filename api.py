import requests
import json
import time
from flask import Blueprint,Flask, jsonify, request, render_template

from block import Block
from transaction import Transaction
from transactionIn import TransactionInput
from transactionOut import TransactionOutput
from node import Node

node = Node()
#number of peers in the network (is provided from the user)
peers = 2

api = Blueprint('api',__name__)

#app functionality

#register node to the network
@api.route('/registration', methods = ['POST'])

def registration():
    data = request.get_json()
    ip = data['ip']
    port = data['port']
    id = len(node.ring)
    pub = data['pub']

    node.register_node_to_ring(ip,id,port,pub,0)

    if (peers == id + 1):
        for peer in node.ring:
            node.announce_ring(peer)
            node.announce_chain(peer)
            if peer.id != node.id:
                node.create_transaction(peer.id,peer.pub,100)
        res = jsonify(peer.id)

    return res

#learn the ring of the bootstrap node and set the id of the node
@api.route('/learn_ring',methods = ['POST'])

def learn_ring():
    load = request.json
    node.ring = load.data

    for peer in node.ring:
        if peer.pub == node.wallet.public_key:
            node.id = peer.id

    return jsonify({'message':'Registered'})

