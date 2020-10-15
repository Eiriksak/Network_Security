from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def to_hex(bits):
    return hex(int(bits,2))[2:]

def pad_text(plaintext):
    if len(plaintext) % 16 != 0:
        return pad(plaintext, 16)
    return plaintext

def unpad_text(plaintext):
    if len(plaintext) % 16 != 0:
        return unpad(plaintext, 16)
    return plaintext

def encrypt(plaintext, key):
    key = bytes.fromhex(to_hex(key))
    plaintext = pad_text(plaintext.encode())
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plaintext)

def decrypt(ciphertext, key):
    key = bytes.fromhex(to_hex(key))
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    return unpad_text(plaintext).decode()