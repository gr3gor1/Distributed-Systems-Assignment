from block import Block

class Blockchain:
    def __init__(self):
        self.chain = []
        self.unconfirmed_transactions = []
        self.genesis_block()

    def genesis_block(self):
        genesis_block = Block("0", [])
        genesis_block.generate_hash()
        self.chain.append(genesis_block)

    def add_block(self, block):
        self.chain.append(block)

    def print_blocks(self):
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            print("Block {} {}".format(i, current_block))
            current_block.print_contents()