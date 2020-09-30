from flask import Flask, render_template, request
from sdes import decrypt_3DES, chunk, binary_to_ascii

app = Flask(__name__)

RAW_KEY_1 = [1,0,0,0,1,0,1,1,1,0]
RAW_KEY_2 = [0,1,1,0,1,0,1,1,1,0]


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/cipher', methods=['GET'])
def cipher():
    ciphertext = request.args.get('ciphertext')
    ciphertext = [int(i) for i in ciphertext]
    chunks = chunk(ciphertext, n=8)
    
    key = RAW_KEY_1 + RAW_KEY_2
    dec = [decrypt_3DES(key, chnk) for chnk in chunks]
    plaintext = []
    for _chnk in dec:
        dec_str = ''.join(str(i) for i in _chnk)
        plaintext.append(dec_str)
    plaintext = ''.join(plaintext)
    plaintext = binary_to_ascii(plaintext)
    return plaintext


if __name__ == '__main__':
    app.run(debug=True)
