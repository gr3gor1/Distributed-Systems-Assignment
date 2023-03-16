from collections import OrderedDict
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from hashlib import sha256

import requests
from flask import Flask, jsonify, request, render_template
import base64


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value, transaction_inputs):

        self.sender_address = sender_address                                                                                            #To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address                                                                                       #To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value                                                                                                             #το ποσό που θα μεταφερθεί
        self.transaction_id = sha256(Crypto.Random.get_random_bytes(128).encode()).hexdigest()                                                     #το hash του transaction
        self.transaction_inputs = transaction_inputs                                                                                    #λίστα από Transaction Input 
        self.transaction_outputs = []                                                                              #λίστα από Transaction Output
        self.signature = self.sign_transaction(sender_private_key)

    def to_dict(self):
        transaction_dict = OrderedDict()
        transaction_dict['sender_address'] = self.sender_address
        transaction_dict['recipient_address'] = self.receiver_address
        transaction_dict['value'] = self.amount
        transaction_dict['transaction_id'] = self.transaction_id
        transaction_dict['transaction_inputs'] = self.transaction_inputs
        transaction_dict['transaction_outputs'] = self.transaction_outputs
        transaction_dict['signature'] = self.signature
        return transaction_dict
        

    def sign_transaction(self, sender_private_key):
        #Sign transaction with private key
        private_key = RSA.importKey(sender_private_key)
        signer = PKCS1_v1_5.new(private_key)
        hash_obj = self.to_dict()
        hash_obj = SHA.new(str(hash_obj).encode('utf8'))
        return base64.b64encode(signer.sign(hash_obj)).decode()

    def verify_signature(self, public_key):
        # Load public key and verify message
        hash_obj = self.to_dict()
        hash_obj = SHA.new(str(hash_obj).encode())
        public_key = RSA.importKey(public_key)
        verifier = PKCS1_v1_5.new(public_key)
        return verifier.verify(hash_obj, base64.b64decode(self.signature))