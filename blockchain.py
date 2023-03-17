from block import Block
from transaction import Transaction
import threading
import time
import copy

CAPACITY=1

class Blockchain:
    def __init__(self):
        self.list_blocks = []
        self.list_transactions = []
        
        ### orizoume to threat gia to mining ###
        
        self.mine = threading.Event()

## theloume na paroume to ring me oles tis addresses gia na mporoume na stelnoume pantou ##

    def get_addresses(self, addresses):
        #print("aaaaaaaaaaaaaaaaaaaaaaaaa")
        self.ring = copy.deepcopy(addresses)
        return
    
 ### otan orizoume ton bootstrap ftiaxetai to genesis kai bazei kai ena transaction mesa ##   
    
    def genesis_block(self,participants,address):
        money = 100 * (participants + 1)
        genesis_block = Block(len(self.list_blocks),[],'0')
        trans = Transaction('0', address, money, [])
        genesis_block.add_transaction(trans.to_dict())
        genesis_block.cur_hash = genesis_block.myHash()
        self.list_blocks.append(genesis_block)
        print("genesis_block")
        return

    def print_blocks(self):
        for i in range(len(self.list_blocks)):
            current_block = self.chain[i]
            print("Block {} {}".format(i, current_block))
            current_block.print_cont()
        return
    
    
    ## prosthetoume transaction kai blepoyme an exei gemisei to block ###
    
    def add_transaction(self,transaction):
        print("new transaction")
        self.list_transactions.append(transaction.to_dict())
        if(len(self.list_transactions)==CAPACITY):
            previous_hash = self.chain[-1].cur_hash
            new_block = Block(len(self.list_blocks),self.list_transactions,previous_hash)
            self.list_transactions = []
            self.mine.clear()
            miner = threading.Thread(name = 'miner', target = self.lets_mine, args = (new_block, ))
            miner.start()
            return
            
    def lets_mine(self,block):
        print("start mining")
        strart_mine_time = time.time()
        block.mine_block(self.mine)
        if (not self.mine.isSet()):
            self.list_blocks.append(block)
            print('Mined block')
            message = {
                        'last_block': self.list_blocks[-1].print_contents() # to JSON
                    }
            print(message)
    
    
    
    def output (self):
        outlist = []
        for bl in self.list_blocks:
            outlist.append(bl.print_contents())
        return outlist
            
            
            
'''
    def add_block(self, transactions):
        previous_hash = (self.chain[-1]).hash
        new_block = Block(len(self.chain),transactions,previous_hash)
        new_block.myHash()
        proof = self.proof_of_work(new_block)
        self.chain.append(new_block)
        return new_block,proof
        
    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if(current.hash != current.myHash()):
                print("Current hash does not equal generated hash")
                return False
            if(current.previous_hash != previous.myHash()):
                print("Previous block's hash got changed")
                return False
        return True
 
    def proof_of_work(self, block, difficulty=MINING_DIFFICULTY):
        proof = block.myHash()
        while proof[:difficulty] != "0"*difficulty:
            block.nonce += 1
            proof = block.myHash()
        block.nonce = 0
        return proof
        '''