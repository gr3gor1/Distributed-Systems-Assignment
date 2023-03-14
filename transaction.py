from collections import OrderedDict

import binascii
import transactionOut
import transactionIn

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class Transaction:

    def __init__(self, sender_address, sender_id,sender_private_key, recipient_address, recipient_id,value,transactionIn,transactionId=None,transactionOut = None,signature = None):
        #self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address
        #self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = recipient_address
        #self.amount: το ποσό που θα μεταφερθεί
        self.amount = value
        #self.transaction_id: το hash του transaction (hexadecimal format)
        if (self.transaction_id == None):
            self.transaction_id = transactionId
        else:
            self.transaction_id = SHA.new((str(sender_address)+str(recipient_address)+str(value)).encode()).hexdigest()
        #self.transaction_inputs: λίστα από Transaction Input 
        self.transaction_inputs = transactionIn
        #self.transaction_outputs: λίστα από Transaction Output
        if (transactionOut != None):
            self.create_out()
        else:
            self.transaction_outputs = transactionOut
        #self.signature
        self.signature = self.sign_transaction()
        #self.private_key
        self.private_key = sender_private_key
        #sender id
        self.sender = sender_id
        #receiver id
        self.receiver = recipient_id

    def sign_transaction(self):
        #Sign transaction with private key
        sender = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hash = SHA.new(str(self.__dict__).encode('utf8'))
        self.signature = binascii.hexlify(sender.sign(hash)).decode('ascii')

    def validate_transaction(self):
        #validate using sender's public key
        key = RSA.importKey(self.sender_address.encode('utf-8'))
        message_hash = SHA.new(self.transaction_id.encode('utf-8'))
        verifier = PKCS1_v1_5.new(key)
        try:
            signature = binascii.unhexlify(self.sender_address.encode('utf-8'))
            is_valid = verifier.verify(message_hash, signature)
            return True
        except (ValueError, TypeError):
            return False

    def create_out(self):
        out = transactionOut.TransactionOutput(self.transaction_id,self.receiver_address,self.amount)
        self.transaction_outputs = [out]

        

