import os
import binascii
import time
import multiprocessing
from multiprocessing import Pool

# Fast indexing for S-boxes
BITS_TO_VAL = {
    (0,0): 0,
    (0,1): 1,
    (1,0): 2,
    (1,1): 3
}

VAL_TO_BITS = {
    0: [0,0],
    1: [0,1],
    2: [1,0],
    3: [1,1]
}

# Generate S-boxes
S0 = [[1,0,3,2],[3,2,1,0],[0,2,1,3],[3,1,3,2]]
S1 = [[0,1,2,3],[2,0,1,3],[3,0,1,0],[2,1,0,3]] 
for row, l in enumerate(S0):
    for col, num in enumerate(l):
        S0[row][col] = VAL_TO_BITS[num]
        
for row, l in enumerate(S1):
    for col, num in enumerate(l):
        S1[row][col] = VAL_TO_BITS[num]



BITNUMS = [2**i for i in range(10)]


def P10(bits):
    return [bits[i-1] for i in [3,5,2,7,4,10,1,9,8,6]]

def P8(bits):
    return [bits[i-1] for i in [6,3,7,4,8,5,10,9]]

def LS(bits, k):
    """Performs a left shift by k"""
    return bits[k:] + bits[:k]

def generate_key(K):
    K = P10(K)
    LS_1_0 = LS(K[:5],k=1)
    LS_1_1 = LS(K[5:],k=1)
    K1 = P8(LS_1_0 + LS_1_1)
    LS_2_0 = LS(LS_1_0,k=2)
    LS_2_1 = LS(LS_1_1,k=2)
    K2 = P8(LS_2_0 + LS_2_1)
    return K1,K2


def P4(bits):
    return [bits[i-1] for i in [2,4,3,1]]

def IP(bits):
    return [bits[i-1] for i in [2,6,3,1,4,8,5,7]]

def EP(bits):
    return [bits[i-1] for i in [4,1,2,3,2,3,4,1]]

def IP_inverse(bits):
    return [bits[i-1] for i in [4,1,3,5,7,2,8,6]]


def bits_to_val(bits, k=10):
    return sum([j*BITNUMS[i] for i,j in enumerate(bits[::-1])])
    
def val_to_bits(val, return_len=2):
    res = [1 if i=='1' else 0 for i in bin(val)[2:]]
    if len(res) < return_len:
        pad = [0]*(return_len-len(res))
        res = pad + res
    return res
        
     

def S_box(bits_0, bits_1):
    #Get output for S0 box
    r = 2*bits_0[0] + 1*bits_0[3]
    c = 2*bits_0[1] + 1*bits_0[2]
    S0_out = S0[r][c]

    #Get output for S1 box
    r = 2*bits_1[0] + 1*bits_1[3] #bit_1, bit_4
    c = 2*bits_1[1] + 1*bits_1[2] #bit_2, bit_3
    S1_out = S1[r][c]
    return S0_out, S1_out

def XOR(bits_0, bits_1):
    return [0 if i==j else 1 for i,j in zip(bits_0, bits_1)]

def SW(bits):
    return bits[4:] + bits[:4]

def sdes_round(inp, K):
    """Performs a round based on input and key"""
    inp_0 = inp[:4]
    inp_1 = inp[4:]
    out = EP(inp_1)
    out = XOR(out, K)
    S0,S1 = S_box(out[:4], out[4:])
    out = P4(S0+S1)
    out = XOR(inp_0,out)
    return out + inp_1


def encrypt(K, plaintext):
    K1,K2 = generate_key(K)
    init_perm = IP(plaintext)
    round_1 = sdes_round(init_perm, K1)
    switch = SW(round_1) #input for round_2
    round_2 = sdes_round(switch, K2)
    enc = IP_inverse(round_2)
    return enc

def decrypt(K, ciphertext):
    K1,K2 = generate_key(K)
    init_perm = IP(ciphertext)
    round_1 = sdes_round(init_perm, K2)
    switch = SW(round_1) #input for round_2
    round_2 = sdes_round(switch, K1)
    dec = IP_inverse(round_2)
    return dec


def test_sdes():
    raw_keys = [[0,0,0,0,0,0,0,0,0,0], [1,1,1,0,0,0,1,1,1,0],[1,1,1,0,0,0,1,1,1,0], [1,1,1,1,1,1,1,1,1,1]]
    plaintext = [[1,0,1,0,1,0,1,0],[1,0,1,0,1,0,1,0],[0,1,0,1,0,1,0,1],[1,0,1,0,1,0,1,0]]
    ciphertext = [[0,0,0,1,0,0,0,1],[1,1,0,0,1,0,1,0],[0,1,1,1,0,0,0,0],[0,0,0,0,0,1,0,0]]
    for k, p, c in zip(raw_keys, plaintext, ciphertext):
        enc = encrypt(k,p)
        if enc == c:
            print(f'CORRECT CIPHERTEXT: encrypted:{enc}, real cipher:{c}')
        else:
            print(f'WRONG CIPHERTEXT: encrypted:{enc}, real cipher:{c}')


def test_encrypt():
    raw_keys = [[0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,1,1,1,1,1], [0,0,1,0,0,1,1,1,1,1], [0,0,1,0,0,1,1,1,1,1]]
    plaintext = [[0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1], [1,1,1,1,1,1,0,0], [1,0,1,0,0,1,0,1]]
    ciphertexts = []
    for k, p in zip(raw_keys, plaintext):
        enc = encrypt(k,p)     
        ciphertexts.append(enc)
    return ciphertexts


def test_decrypt():
    raw_keys = [[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,1,1,1,1,1],[1,0,0,0,1,0,1,1,1,0],[1,0,0,0,1,0,1,1,1,0]]
    ciphertexts = [[0,0,0,0,1,1,1,1],[0,1,0,0,0,0,1,1],[0,0,0,1,1,1,0,0],[1,1,0,0,0,0,1,0]]
    plaintexts = []
    for k, c in zip(raw_keys, ciphertexts):
        dec = decrypt(k,c)
        plaintexts.append(dec)
    return plaintexts


def encrypt_3DES(K1, K2, plaintext):
    return encrypt(K1,decrypt(K2,encrypt(K1,plaintext)))

def test_encrypt_3DES():
    raw_keys_1 = [[1,0,0,0,1,0,1,1,1,0],[1,0,0,0,1,0,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0]]
    raw_keys_2 = [[0,1,1,0,1,0,1,1,1,0],[0,1,1,0,1,0,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0]]
    plaintexts = [[1,1,0,1,0,1,1,1],[1,0,1,0,1,0,1,0],[0,0,0,0,0,0,0,0],[0,1,0,1,0,0,1,0]]
    ciphertexts = []
    for k1, k2, p in zip(raw_keys_1, raw_keys_2, plaintexts):
        enc = encrypt_3DES(k1,k2,p)
        ciphertexts.append(enc)
    return ciphertexts


def decrypt_3DES(K, ciphertext):
    return decrypt(K[:10], encrypt(K[10:], decrypt(K[:10], ciphertext)))


def test_decrypt_3DES():
    raw_keys_1 = [[1,0,0,0,1,0,1,1,1,0],[1,0,1,1,1,0,1,1,1,1],[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0]]
    raw_keys_2 = [[0,1,1,0,1,0,1,1,1,0],[0,1,1,0,1,0,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0]]
    ciphertexts = [[1,1,1,0,0,1,1,0],[0,1,0,1,0,0,0,0],[0,0,0,0,0,1,0,0],[1,1,1,1,0,0,0,0]]
    plaintexts = []
    for k1, k2, c in zip(raw_keys_1, raw_keys_2, ciphertexts):
        k = k1 + k2
        dec = decrypt_3DES(k, c)
        plaintexts.append(dec)
    return plaintexts


def binary_to_ascii(s):
    """Slice every 8 bit and convert it"""
    chunks = chunk(s, n=8)
    return ''.join(chr(int(c,2)) for c in chunks)

def ascii_to_binary(asc):
    return ''.join(bin(ord(c))[2:].zfill(8) for c in asc)


def chunk(l, n=8):
    """Divides a list into 8 bit chunks"""
    return [l[i:i+n] for i in range(0, len(l), n)]


def key_check(key, chunks):
    res = []
    for _chunk in chunks:
        dec_str = ''.join(str(i) for i in decrypt(key, _chunk))
        dec_str = binary_to_ascii(dec_str)
        c = ord(dec_str)
        if (c > 64 and c < 91) or (c > 96 and c < 123):
            res.append(dec_str)
        else:
            return False
    return ''.join(res)




with open('CTX2.txt') as f:
    ctx2 = f.read()
    ctx2 = [int(i) for i in ctx2]
    chunks2 = chunk(ctx2, n=8)

    
def key_check_3des(key, chunks=chunks2):
    res = []
    for _chunk in chunks:
        dec_str = ''.join(str(i) for i in decrypt_3DES(key, _chunk))
        dec_str = binary_to_ascii(dec_str)
        c = ord(dec_str)
        if (c > 64 and c < 91) or (c > 96 and c < 123):
            res.append(dec_str)
        else:
            return key, False
    return key, ''.join(res)


if __name__ == "__main__":

    with open('CTX1.txt') as f:
        ctx1 = f.read()
        ctx1 = [int(i) for i in ctx1]
        chunks = chunk(ctx1, n=8)

    inp = input("Verify SDES implementation? (y/n):")
    if inp == "y":
        test_sdes()
        print()

    inp = input("Test SDES decryption and encryption? (y/n):")
    if inp == "y":
        dec = test_decrypt()
        enc = test_encrypt()
        print(f'Ciphertexts:\n{enc}')
        print(f'Plaintexts:\n{dec}')
        print()

    inp = input("Test TripleSDES decryption and encryption? (y/n):")
    if inp == "y":
        dec = test_decrypt_3DES()
        enc = test_encrypt_3DES()
        print(f'Ciphertexts:\n{enc}')
        print(f'Plaintexts:\n{dec}')
        print()   

    inp = input("Crack CTX1 with SDES? (y/n):")
    if inp == "y":
        keys = [val_to_bits(i, return_len=10) for i in range(2**10)]
        start_time = time.time()
        for key in keys:
            pos_key = key_check(key, chunks)
            if pos_key:
                print(pos_key)
                print(key)
                break
                
        print("--- %s seconds ---" % (time.time() - start_time))
        print()

    inp = input("Crack CTX2 with TripleSDES (Multiprocessing)? (y/n):")
    if inp == "y":
        # Generate all possible keys
        start_time = time.time()
        keys = [val_to_bits(i, return_len=10) for i in range(2**10)]
        keys_3des = []
        for key1 in keys:
            for key2 in keys:
                keys_3des.append(key1+key2)
        
        time_spent = time.time() - start_time
        print(f'Spent {time_spent:.5f}s generating all {len(keys_3des)} possible keys')

        start_time = time.time()
        chunksize = int(len(keys) / multiprocessing.cpu_count())
        with multiprocessing.Pool() as pool:
            for key, decoded_text in pool.imap_unordered(func=key_check_3des, iterable=keys_3des, chunksize = chunksize):
                if decoded_text:
                    print(key)
                    print(decoded_text)
                    break
                    
                    
        print("--- %s seconds ---" % (time.time() - start_time))