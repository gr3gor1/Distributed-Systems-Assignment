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
        self.signature = self.sign_transaction()
        #self.private_key
        self.private_key = sender_private_key

    def sign_transaction(self):
        #Sign transaction with private key
        sender = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hash = SHA.new(str(self.__dict__).encode('utf8'))
        self.signature = binascii.hexlify(sender.sign(hash)).decode('ascii')