from kasisky import ALPHABET, decipher, encipher, get_key_lens, frequency_analysis, candidate_keys
import matplotlib.pyplot as plt
import time
import os

if __name__ == "__main__":

    with open('cipher.txt', 'r') as f:
        doc = f.read()
        doc = "".join(doc.split()) 


    """
        key_len_times = []
        x = []
        for key_len in range(5, 600, 10):
            key = random_key(key_len)
            ciphertext = encipher(plaintext, key)

            start_time = time.time()
            key_lens = get_key_lens(key_len, doc)
            _ex_time = (time.time() - start_time)
            print(f'Time spent for key length {key_len}: {_ex_time:.5f}s')
            key_len_times.append(_ex_time)
            x.append(key_len)


        plt.plot(x, key_len_times, color="blue")
        plt.xlabel('Key length', fontsize=18)
        plt.ylabel('Execution time in seconds',fontsize=18)
        plt.title('Execution time for Kasiskis method', fontsize=18)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.savefig('kasiski')
    """

    key_len_times = []
    x = []
    for key_len in range(5, 1000, 10):
        start_time = time.time()
        L, lf = frequency_analysis(doc, key_len)
        keys = candidate_keys(lf)
        _ex_time = (time.time() - start_time)
        print(f'Time spent for key length {key_len}: {_ex_time:.5f}s')
        key_len_times.append(_ex_time)
        x.append(key_len)

    plt.figure(figsize=(15,8))
    plt.plot(x, key_len_times, color="blue")
    plt.xlabel('Key length', fontsize=18)
    plt.ylabel('Execution time in seconds',fontsize=18)
    plt.title('Execution time for candidate key generation', fontsize=18)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.savefig('candidate_keys')


