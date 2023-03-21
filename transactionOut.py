#each transaction creates two outputs

class TransactionOutput:

    def __init__(self,transactionId,recipient,value):
        self.transactionId = transactionId
        self.recipient = recipient
        self.value = value
        self.unspent = True;

    
