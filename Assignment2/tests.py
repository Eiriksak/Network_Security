import time

from key_exchange import DiffieHellman 
from cipher import encrypt, decrypt
from bbs import BlumBlumShub

def test_protocol():
    start_time = time.time()
    Alice = DiffieHellman()
    q = Alice.get_generator()
    p = Alice.get_prime()
    Bob = DiffieHellman(generator=q, prime=p)
    # Compute respective public keys
    PU_A = Alice.get_public_key()
    PU_B = Bob.get_public_key()
    # Compute shared session key
    K_A = Alice.get_session_key(PU_B)
    K_B = Bob.get_session_key(PU_A)
    assert K_A == K_B

    #CSPRNG
    bbs = BlumBlumShub(q=383, p=503)
    Alice_secret_key = bbs.generate(seed=K_A, key_len=128)
    Bob_secret_key = bbs.generate(seed=K_B, key_len=128)
    assert Alice_secret_key == Bob_secret_key
    assert len(Alice_secret_key) == 128
    # From Alice to Bob
    message = "Hi Bob, this is a message that should be encrypted properly"
    enc_message = encrypt(message, Alice_secret_key) 
    dec_message = decrypt(enc_message, Bob_secret_key)
    assert message in dec_message

    # From Bob to Alice
    message = "Hi Alice, this is also a message that should be encrypted properly"
    enc_message = encrypt(message, Bob_secret_key) 
    dec_message = decrypt(enc_message, Alice_secret_key)
    assert message in dec_message
    total_time = (time.time() - start_time)
    print(f'##########\nPassed protocol test in {total_time}s\n##########')

def test_DH(g=None, p=None):
    start_time = time.time()
    Alice = DiffieHellman(generator=g, prime=p)
    _g = Alice.get_generator()
    _p = Alice.get_prime()
    Bob = DiffieHellman(generator=_g, prime=_p)
    # Compute respective public keys
    PU_A = Alice.get_public_key()
    PU_B = Bob.get_public_key()
    # Compute shared session key
    K_A = Alice.get_session_key(PU_B)
    K_B = Bob.get_session_key(PU_A)
    assert K_A == K_B
    total_time = (time.time() - start_time)
    print(f'##########\nPassed DH test in {total_time}s\n##########')

def test_BBS(key_len=128, q=None, p=None, bitlen=1024):
    start_time = time.time()
    bbs = BlumBlumShub(q=q, p=p, bitlen=bitlen)
    pub1 = bbs.generate(seed=42, key_len=key_len)

    bbs2 = BlumBlumShub(q=q, p=p, bitlen=bitlen)
    pub2 = bbs.generate(seed=42, key_len=key_len)

    assert pub1 == pub2
    assert len(pub1) == key_len
    total_time = (time.time() - start_time)
    print(f'##########\nPassed BBS test in {total_time}s\n##########')

def test_AES():
    start_time = time.time()
    key = '11100101010001100001110100011111100101000010010011000010011111101101001110010110101101010101011101101101110010000111101001000111'
    enc = encrypt('Hello World!', key)
    dec = decrypt(enc, key)
    assert 'Hello World!' in dec
    total_time = (time.time() - start_time)
    print(f'##########\nPassed AES test in {total_time}s\n##########')

if __name__ == "__main__":
    inp = input("Test entire protocol? (y/n):")
    if inp == "y":
        test_protocol()
    else:
        inp = input("Test DH-exchange? (y/n)")
        if inp == "y":
            test_DH()
        inp = input("Test BBS generator? (y/n)")
        if inp == "y":
            test_BBS()
        inp = input("Test AES? (y/n)")
        if inp == "y":
            test_AES()