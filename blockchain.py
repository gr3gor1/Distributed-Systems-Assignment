import block

class Blockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, block):
        #Add a block to the blockchain.
        self.chain.append(block)

    def create_genesis_block(self):
        genesis_block = Block(0,"0")
        self.chain.append(genesis_block)