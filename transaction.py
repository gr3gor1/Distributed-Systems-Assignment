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
        'outputs' : self.transaction_outputs
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
            'signature' : self.Signature,
            'tran_id':self.transaction_id
        }
        string = json.dumps(transaction, sort_keys=True)
        return string 


    def to_dict(self):
        transaction_dict = OrderedDict()
        transaction_dict['sender_address'] = self.sender_address
        transaction_dict['recipient_address'] = self.receiver_address
        transaction_dict['value'] = self.value
        transaction_dict['transaction_id'] = self.transaction_id
        transaction_dict['transaction_inputs'] = self.transaction_inputs
        transaction_dict['transaction_outputs'] = self.transaction_outputs
        transaction_dict['signature'] = self.Signature
        return transaction_dict
        
    
    def to_dict2(self):
        transaction_dict = OrderedDict()
        transaction_dict['sender_address'] = self.sender_address
        transaction_dict['recipient_address'] = self.receiver_address
        transaction_dict['value'] = self.value
        transaction_dict['transaction_id'] = self.transaction_id
        transaction_dict['transaction_inputs'] = self.transaction_inputs
        #transaction_dict['transaction_outputs'] = self.transaction_outputs
        return transaction_dict
        
        

    def sign_transaction(self,sender_private_key,t):
        """
        Sign transaction with private key
        """
    
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        
        hash_obj = t.to_dict2()
        hash_obj = SHA.new(str(hash_obj).encode('utf8'))
        
        return binascii.hexlify(signer.sign(hash_obj)).decode('ascii')
       
    def verify_signature(self,public_key,sing,t):
        # Load public key and verify message
        public_key = RSA.importKey(binascii.unhexlify(public_key))
        verifier = PKCS1_v1_5.new(public_key)
        
        hash_obj = t.to_dict2()
        hash_obj = SHA.new(str(hash_obj).encode('utf8'))

        verify = verifier.verify(hash_obj,  binascii.unhexlify(sing))
        
        return verify