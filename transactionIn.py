#each transaction comes after a previous transaction

class TransactionInput:

    def __init__(self,previousOutputId):
        self.previousId = previousOutputId;