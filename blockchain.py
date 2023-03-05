class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_id_count = 0
        
    def add_block(self, block):
        #Add a block to the blockchain.
        self.chain.append(block)