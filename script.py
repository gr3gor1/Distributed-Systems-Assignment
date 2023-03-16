
from collections import OrderedDict

import hashlib as hasher
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import base64
import Crypto
import Crypto.Random

from Crypto.Hash import SHA384

import json

from block import Block


from transaction import Transaction

from blockchain import Blockchain

from node import node

'''

t = Transaction(9,10,100,234)


rsa_keypair = RSA.generate(2048)


privkey = rsa_keypair.exportKey('PEM').decode()
pubkey = rsa_keypair.publickey().exportKey('PEM').decode()
random_gen = Crypto.Random.new().read
priv = RSA.generate(1024, random_gen)
pub = priv.publickey()
privkey = priv.exportKey(format='DER')
pubkey = pub.exportKey(format='DER')


t.sign_transaction(privkey)
print(t.verify_signature(pubkey))
'''
'''
chain=Blockchain()
chain.genesis_block(1)
#chain.print_blocks()
t=Transaction(0,123,10,100)
chain.add_transaction(t)
#chain.print_blocks()
t2=Transaction(0,123,10,100)
chain.add_transaction(t2)
chain.print_blocks()'''

start=node(0,0,0,"yes",1)
start.register_node_to_ring()