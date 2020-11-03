from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file
import dsa
import json
import string
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        description = request.form.get('description')
        amount = request.form.get('amount')
        amount = str(amount)
        data = {
            'firstname': {'value': firstname},
            'lastname': {'value': lastname},
            'username': {'value': username},
            'description': {'value': description},
            'amount': {'value': amount}
        }
        
        # Sign each of the fields and store the document under /transactions folder
        p, q, g = dsa.gen_pubkeys(L=512) # Set up shared global public key values
        x, y = dsa.gen_userkeys(p, q ,g) # Private and public keys
        print(data)
        for field in data:
            print(field)
            r, s, _ = dsa.sign_message(data[field]['value'], p, q, g, x) # Sign data in field
            data[field]['r'] = r
            data[field]['s'] = s
        # Add public data
        data['public_key'] = y
        data['p'] = p
        data['q'] = q
        data['g'] = g
        transaction_id = ''.join(random.choice(string.ascii_letters) for i in range(30)) # Random hash
        with open('transactions/'+transaction_id+".json", 'w') as f:
            json.dump(data, f, indent=4)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)