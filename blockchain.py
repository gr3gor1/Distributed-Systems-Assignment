from block import Block
from transaction import Transaction
from wallet import wallet
import threading
import time
##import node

CAPACITY=1

class Blockchain:
    def __init__(self):
        self.chain = []
        self.list_transactions = []
        self.mine = threading.Event()
        #self.ring=node.ring
        #self.id=node.id

    def genesis_block(self,participants):
        money = 100 * (participants + 1)
        address=wallet()
        genesis_block = Block(len(self.chain),[],'0')
        trans = Transaction('0', address.address, money, [])
        genesis_block.add_transaction(trans.to_dict())
        genesis_block.cur_hash = genesis_block.myHash()
        self.chain.append(genesis_block)
        return print("genesis created")

    def print_blocks(self):
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            print("Block {} {}".format(i, current_block))
            current_block.print_cont()
        return
    
    
    def add_transaction(self,transaction):
        print("new transaction")
        self.list_transactions.append(transaction.to_dict())
        if(len(self.list_transactions)==CAPACITY):
            previous_hash = self.chain[-1].cur_hash
            new_block = Block(len(self.chain),self.list_transactions,previous_hash)
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
            self.chain.append(block)
            print('Mined block')
            message = {
                        'last_block': self.chain[-1].print_contents() # to JSON
                    }
            print(message)
    
    
    
    def output (self):
        outlist = []
        for bl in self.chain:
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