import os
import json

from flask import Flask, request, render_template, redirect, url_for, jsonify
import requests
import base64

from key_exchange import DiffieHellman 
from cipher import encrypt, decrypt
from bbs import BlumBlumShub

app = Flask(__name__)

session = {
    'key': None,
    'endpoint': 'http://127.0.0.1:5000',
    'active_chat': False,
    'username': 'Bob',
    'receiver': 'Alice',
    'messages': [],
    'secret_key': None
    }

# We define p and q from a pre generated file as this requires a bit more implemenation
# if we were to implement the secret flow in this app
with open('p.txt', 'r') as f:
    Q = int(f.read())
with open('q.txt', 'r') as f:
    P = int(f.read())

def clear_session():
    session['key'] = None
    session['active_chat'] = False
    session['public_key'] = None
    session['secret_key'] = None

@app.route('/')
def index():
    return render_template('index.html',
    chat=session['active_chat'],
    key=session['key'],
    name=session['username'],
    receiver=session['receiver'],
    messages=session['messages'],
    secret_key=session['secret_key']
    )

@app.route('/new_chat')
def new_chat():
    """
    1. Clear current session
    2. Initialize a new Diffie-Hellman object and generate your public key
    3. Post your public key together with prime and generator so receiving end can set up correct
    4. Get public key from other end 
    5. Compute session key (based on received public key)
    6. Further improve session key by using Blum Blum Shub generator
    """
    clear_session()
    dh = DiffieHellman()
    public_key = dh.get_public_key() # Send to other part
    params = {'generator': dh.get_generator(), 'prime': dh.get_prime(), 'key': public_key}
    url = session['endpoint'] + '/getpub'
    res = requests.post(url, json=params).json()
    received_public_key = res['key']
    session['key'] = dh.get_session_key(public_key=received_public_key)
    #CSPRNG
    bbs = BlumBlumShub(q=Q, p=P)
    secret_key = bbs.generate(seed=session['key'], key_len=128)
    session['secret_key'] = secret_key
    session['active_chat'] = True
    return redirect(url_for('index'))


@app.route('/sendmsg', methods=['POST'])
def sendmsg():
    """Encrypts plaintext into ciphertext and sends it to the other part"""
    if session['secret_key'] is not None:
        msg = request.form['msg']
        msg = encrypt(plaintext=msg, key=session['secret_key'])
        #Cannot serialize bytes in JSON, so convert it to string over the network
        msg = str(base64.encodebytes(msg), 'utf-8') 
        url = session['endpoint'] + '/getmsg'
        res = requests.post(url, json={'msg': msg})
    return redirect(url_for('index'))


@app.route('/getmsg', methods=['POST'])
def get_msg():
    """Receives and decrypts the encrypted message"""
    if request.method == 'POST':
        data = request.get_json(force=True)
        msg = base64.decodebytes(data['msg'].encode()) #Bring it back to bytes
        session['messages'].append({
            'decrypted': decrypt(ciphertext=msg, key=session['secret_key']),
            'encrypted': msg
        })
    return ''

@app.route('/getpub', methods=['GET','POST'])
def get_pub():
    """
    POST: Calculate new session key
    GET: Return public key
    """
    print('METHOD: ', request.method)
    if request.method == 'POST':
        # Calculate new session key
        clear_session()
        data = request.get_json(force=True)
        #Use same generator and prime as the user who initiated this session
        dh = DiffieHellman(generator=data['generator'], prime=data['prime'])
        public_key = dh.get_public_key() # Send to other part
        session['key'] = dh.get_session_key(data["key"])
        #CSPRNG
        bbs = BlumBlumShub(q=Q, p=P)
        secret_key = bbs.generate(seed=session['key'], key_len=128)
        session['secret_key'] = secret_key
        session['active_chat'] = True
        return jsonify({'key': public_key})
    else:
        return session['key']


if __name__ == '__main__':
    app.run(debug=True, port=4000)