import socket
import os
import json


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 4000))
s.listen(1)

def get_transactions():
    """Returns all generated transaction files"""
    transactions = []
    for transaction_file in os.listdir('transactions'):
        if '.json' in transaction_file:
            with open('transactions/'+transaction_file, 'r') as f:
                data =  json.load(f)
                data['transaction_id'] = transaction_file.split(".json")[0]
                transactions.append(data)
    return transactions

line = "*"*20
print(line,"Running CRYPTOBANK Server",line)
while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")
    data = get_transactions()
    data = json.dumps(data).encode('utf-8')
    clientsocket.sendall(data)