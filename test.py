
def read_transactions(total_nodes, id):
    transactions = []
    with open("transactions/{}nodes/transactions{}.txt".format(total_nodes, id), "r") as file:
        content = file.readlines()
        for line in content:
            id, amount = line.split()
            transactions.append([int(id[2]), int(amount)])
    return transactions

    
transactions = read_transactions(5, 0)

print(transactions)
