from block import Block
from transaction import Transaction

class Blockchain:
    def __init__(self):
        self.chain = []
        #self.genesis_block()

    def create_genesis_block(self, bootstrap_address, amount):
        genesis_block = Block(0, "1", [])#Transaction("0", recipient_address=bootstrap_address, value=amount, transaction_inputs=None)])
        self.chain.append(genesis_block)

    def add_block(self, block):
        self.chain.append(block)

    def print_blocks(self):
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            print("Block {} {}".format(i, current_block))
            current_block.print_contents()