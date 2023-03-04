from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address
        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = recipient_address
        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = value
        #self.transaction_id: το hash του transaction (hexadecimal format)
        self.transaction_id = SHA.new((str(sender_address)+str(recipient_address)+str(value)).encode()).hexdigest()
        #self.transaction_inputs: λίστα από Transaction Input 
        self.transaction_inputs = []
        #self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = [] 
        #self.signature
        self.signature = None
        #self.private_key
        self.private_key = sender_private_key

    def to_dict(self):
        # Convert transaction object to a dictionary
        transaction_dict = OrderedDict()
        transaction_dict['sender_address'] = self.sender_address
        transaction_dict['recipient_address'] = self.receiver_address
        transaction_dict['value'] = self.amount
        transaction_dict['transaction_id'] = self.transaction_id
        transaction_dict['transaction_inputs'] = self.transaction_inputs
        transaction_dict['transaction_outputs'] = self.transaction_outputs
        transaction_dict['signature'] = self.signature
        return transaction_dict

    def sign_transaction(self):
        #Sign transaction with private key
        sender = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hash = SHA.new(str(self.to_dict()).encode('utf8'))
        self.signature = binascii.hexlify(sender.sign(hash)).decode('ascii')