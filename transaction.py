from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
import json
import hashlib
import base64


class Transaction:

    def __init__(self, sender_address, recipient_address, value, transaction_inputs):
        ##set

        self.sender_address= sender_address #To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver_address=recipient_address  #To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.value=value  #το ποσό που θα μεταφερθεί
        self.transaction_inputs= transaction_inputs #λίστα από Transaction Input 
        self.transaction_outputs=[]# λίστα από Transaction Output 
        self.transaction_id=self.hash() #το hash του transaction
        self.Signature=""

    
    def hash(self):
        transaction = { 
        'sender': self.sender_address,
        'receiver': self.receiver_address, 
        'value': self.value, 
        'inputs' : self.transaction_inputs, 
        'outputs' : self.transaction_outputs,
        }
        string = json.dumps(transaction, sort_keys=True).encode()
        return hashlib.sha256(string).hexdigest()

    def transaction_to_json(self):
        transaction = {
            'sender' : self.sender_address, 
		    'receiver' : self.receiver_address,  
		    'value' : self.value, 
            'inputs' : self.transaction_inputs, 
            'outputs' : self.transaction_outputs,
            'signature' : self.Signature
        }
        string = json.dumps(transaction, sort_keys=True)
        return string 


    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                           'receiver_address': self.receiver_address,
                           'value': self.value,
                           'transaction_id':self.transaction_id,
                           'transaction_inputs':self.transaction_inputs,
                           'transaction_outputs':self.transaction_outputs,
                           'Signature':self.Signature})
    
    def to_dict2(self):
        return OrderedDict({'sender_address': self.sender_address,
                           'receiver_address': self.receiver_address,
                           'value': self.value,
                           'transaction_id':self.transaction_id,
                           'transaction_inputs':self.transaction_inputs,
                           'transaction_outputs':self.transaction_outputs})
        

    def sign_transaction(self,sender_private_key):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(sender_private_key)
        signer = PKCS1_v1_5.new(private_key)
        
        hash_obj = self.to_dict2()
        hash_obj = SHA.new(str(hash_obj).encode('utf8'))
        self.Signature = (base64.b64encode(signer.sign(hash_obj)).decode())
        
        return 
       
    def verify_signature(self,public_key):
        # Load public key and verify message

        hash_obj = self.to_dict2()
        hash_obj = SHA.new(str(hash_obj).encode())
        
        public_key = RSA.importKey(public_key)
        verifier = PKCS1_v1_5.new(public_key)

        verify = verifier.verify(hash_obj, base64.b64decode(self.Signature))
        
        return verify