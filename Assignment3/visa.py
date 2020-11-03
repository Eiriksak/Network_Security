"""
visa.py acts as a server between banking institutions.
You can think of it as a VISA server that
receives a signed transaction from bank A and then it will
verify the signed transactions before sending it to the
receivers account on Bank B
"""

import socket
import json
import dsa
import datetime
from datetime import datetime

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 4000))


bytestr = b''
while True:
    data = s.recv(8192)
    bytestr += data
    if len(bytestr) >= 0:
        break
transactions = json.loads(bytestr.decode('utf-8'))

def verify_transactions(transactions):
    now = datetime.now()
    datestr = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Verifying transactions: ", datestr)
    line = "*"*15
    for transaction in transactions:
        print("\n\n")
        print(line, "Verifying new transaction",line)
        # Shared global public key values
        p = transaction['p']
        q = transaction['q']
        g = transaction['g']
        y = transaction['public_key']
        transaction_id = transaction['transaction_id']
        print(f'Transaction parameters:\nTransaction ID: {transaction_id}\np: {p}\nq: {q}\ng: {g}\ny: {y}')
        # Verify each part of the transaction
        for field, values in transaction.items():
            if field not in ['p', 'q', 'g', 'public_key', 'transaction_id']:
                value  = str(values['value'])
                verified = dsa.verify_message(value, p, q, g, values['r'], values['s'], y)
                if verified:
                    print(f'\n{field}: {value} ##### Status=VERIFIED')
                else:
                    j = '#'*20
                    print(f'\n{field}: {value} {j}WARNING{j}Status=NOT VERIFIED!')



verify_transactions(transactions)