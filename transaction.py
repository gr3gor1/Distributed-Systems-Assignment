from collections import OrderedDict
from datetime import datetime
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from hashlib import sha256

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):

        self.sender_address = sender_address                                                                                                        #To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address = recipient_address                                                                                               #To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value                                                                                                                         #το ποσό που θα μεταφερθεί
        self.transaction_id = sha256((str(self.sender_address) + str(self.receiver_address) + str(self.amount) + str(datetime.now())).encode())     #το hash του transaction
        self.transaction_inputs =                                                                                                                   #λίστα από Transaction Input 
        self.transaction_outputs =                                                                                                                  #λίστα από Transaction Output 
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
        """
        Sign transaction with private key
        """
        return PKCS1_v1_5.new(sender_private_key).sign(self.transaction_id)