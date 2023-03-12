import block

class Blockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, block):
        #Add a block to the blockchain.
        self.chain.append(block)

    def create_genesis_block(self):
        genesis_block = block.Block(0,"0",1)
        genesis_block.list_of_transactions = []  
        genesis_block.hash = genesis_block.myHash()
        self.chain.append(genesis_block)