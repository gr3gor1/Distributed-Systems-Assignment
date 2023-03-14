#each transaction creates two outputs

class TransactionOutput:

    def __init__(self,previousOutputId,recipient,value):
        self.transactionId = previousOutputId
        self.recipient = recipient
        self.value = value
        self.unspent = True;

    
