from key_exchange import DiffieHellman 
from cipher import encrypt, decrypt
from bbs import BlumBlumShub

if __name__ == "__main__":
    g = int(input("Define g for DH (press 0 to use default) "))
    p = int(input("Define p for DH (press 0 to use default) "))
    if g == 0:
        g = None
    if p == 0:
        p = None
    Alice = DiffieHellman(g, p)
    g = Alice.get_generator()
    p = Alice.get_prime()
    Bob = DiffieHellman(generator=g, prime=p)
    print(f'You have successfully set up DH for Alice and Bob with these parameters:\ng: {g}\np: {p}')
    # Compute respective public keys
    PU_A = Alice.get_public_key()
    PU_B = Bob.get_public_key()
    print(f'\nYou have succesfully set up public keys for Alice and Bob:\nAlice: {PU_A}\nBob: {PU_B}')
    # Compute shared session key
    K_A = Alice.get_session_key(PU_B)
    K_B = Bob.get_session_key(PU_A)
    print(f'\nYou have succesfully set up a shared key for Alice and Bob:\nAlice: {K_A}\nBob: {K_B}')
    print("\nYou will now further improve the shared key by using Blum Blum Shub")
    q = int(input("Define q for BBS (press 0 to use default) "))
    p = int(input("Define p for BBS (press 0 to use default) "))
    bitlen = int(input("Define bitlen for BBS (press 0 to use default(1024)) "))
    key_len = int(input("Define key length to be used for AES (press 0 to use default (128)) "))
    if q == 0:
        q = None
    if p == 0:
        p = None
    if bitlen == 0:
        bitlen = 1024
    if key_len == 0:
        key_len = 128
    #CSPRNG
    bbs = BlumBlumShub(q=q, p=p, bitlen=bitlen)
    Alice_secret_key = bbs.generate(seed=K_A, key_len=key_len)
    Bob_secret_key = bbs.generate(seed=K_B, key_len=key_len)
    key_len = len(Bob_secret_key)
    print(f'\nYou have succesfully set up a more secure shared key of length {key_len} for Alice and Bob:\nAlice: {Alice_secret_key}\nBob: {Bob_secret_key}')
    print("\nTest the protocol by writing a message")
    message = input("\n(Alice) Write your message to Bob here: ")
    enc_message = encrypt(message, Alice_secret_key) 
    dec_message = decrypt(enc_message, Bob_secret_key)
    print(f'\nMessage sent over the network: {enc_message}')
    print(f'\nBob decrypting the message by his generated key: {dec_message}')

    message = input("\n(Bob) Write your message to Alice here: ")
    enc_message = encrypt(message, Bob_secret_key) 
    dec_message = decrypt(enc_message, Alice_secret_key)
    print(f'\nMessage sent over the network: {enc_message}')
    print(f'\Alice decrypting the message by her generated key: {dec_message}')

