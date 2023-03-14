import block

class Blockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, block):
        #Add a block to the blockchain.
        self.chain.append(block)

    def stringify_chain(self):
        return str(self.__dict__)