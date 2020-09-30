import os
import string
import itertools
from nltk.corpus import stopwords
import time

ALPHABET = string.ascii_uppercase
STOPWORDS = stopwords.words('english')
STOPWORDS = [w.upper() for w in STOPWORDS if len(w) > 2]
MAX_KEY_LEN = 10
EN_WF = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406,
         6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978,2.360, 0.150, 1.974, 0.074]

EN_WF = [i/100 for i in EN_WF]

def get_ngram(s, n):
    """Get list of all character level ngrams in a given string
    
    Args:
        s: Input string.
        n: Number of characters in the ngram.
        
    Returns:
        A list of all character level ngrams in s.
        Ex. s="TESTING" n=3
        => ['TES', 'EST', 'STI', 'TIN', 'ING']
    """

    tokens = list(s)
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return ["".join(ngram) for ngram in ngrams]

def get_distances(idx):
    """Get all positional distances for a certain item
    
    Args:
        idx: List of indexes indicating the positions of the item.
        
    Returns:
        A List containing all distances for this item. Ex. if an
        item AB is in positions [2,6,15,25] it returns: 
        [4, 13, 23, 9, 19, 10] (6-2,15-2,25-2,15-6,25-6,25-15).
    """
    dists = []
    for i in range(len(idx)-1):
        for j in idx[i+1:]:
            dists.append(j-idx[i])  
    return dists

    

def get_ngram_distances(ngram):
    """Get all positional distances in a ngram sequence
    
    Args:
        ngram: Sequence of ngram items (Ex. [ABC, BCD, CDE])
        
    Returns:
        A list of all distances between similar items in
        the ngram sequence
    """
    res = []
    for item in set(ngram):
        # Get the position index for all occurences of a ngram
        pos_idx = [i for i,_ngram in enumerate(ngram) if _ngram==item] 
        if len(pos_idx) > 1:
            res = res + get_distances(pos_idx)
    return res


def get_factors(n, limit):
    return [x for x in range(1, n+1) if n % x == 0 and x != 1 and x <= limit]


def get_key_lens(max_len, doc):
    factors = []
    for n in range(2,max_len+1):
        ngram = get_ngram(doc,n)
        dists = get_ngram_distances(ngram)
        _factors = [get_factors(i, limit=max_len) for i in dists]
        # Flatten array: [[2,4], [6,3]] => [2,4,6,3]
        factors += [item for sublist in _factors for item in sublist]

    factor_frequencies = {k:factors.count(k) for k in range(2,max_len+1)}
    factor_frequencies = {k: v for k, v in sorted(factor_frequencies.items(), reverse=True, key=lambda item: item[1])}
    return factor_frequencies

def frequency_analysis(doc, key_len):
    L = [''] * key_len 
    lf = [0] * key_len
    for i in range(key_len):
        l = doc[i:len(doc):key_len] # Slice string[start: stop: step]
        L[i] = l

    for i, v in enumerate(L):
        lf[i] = [v.count(w)/len(v) if len(v) > 0 else 0 for w in ALPHABET ]
    return L, lf

def top_letters(k):
    #https://www.geeksforgeeks.org/python-indices-of-n-largest-elements-in-list/
    lf = {w:v for w, v in zip(ALPHABET, EN_WF)} # e.g. A: 0.0012345
    lf = {k: v for k, v in sorted(lf.items(), reverse=True, key=lambda item: item[1])}
    return list(lf.keys())[:k]


def e_offset(frequencies, k=1):
    letters = top_letters(k) 
    candidates = [[]] * len(frequencies) # Store k most probable keys based on each frequency
    for i, lf in enumerate(frequencies):
        _c = []
        for letter in letters:
            # Find top k most frequent letters and calculate distance to E
            _idx = (lf.index(max(lf)) - ALPHABET.find(letter)) % 26
            _key = ALPHABET[_idx]
            _c.append(_key)
        candidates[i] = _c
    return candidates

def candidate_keys(frequencies):
    candidates = e_offset(frequencies, k=5)
    key_comboes = list(itertools.product(*candidates))
    return [''.join(combo) for combo in key_comboes] # All key alternatives

def get_top_candidates(doc, keys, k=5):
    res = {k:0 for k in keys}
    for key in keys:
        decoded_doc = decipher(doc, key)
        res[key] = sum([decoded_doc.count(word) for word in STOPWORDS])
    
    res = {k: v for k, v in sorted(res.items(), reverse=True, key=lambda item: item[1])}
    return list(res.keys())[:k], list(res.values())[:k]  # Top k key alternatives

def decipher(doc, key):
    key_len = len(key)
    key = ''.join([key[i % key_len] for i in range(len(doc))])
    decoded_doc = []
    for i, char in enumerate(doc):
        shift = (ALPHABET.find(char) - ALPHABET.find(key[i])) % 26
        decoded_doc.append(ALPHABET[shift])
    return ''.join(decoded_doc)

def encipher(doc, key):
    key_len = len(key)
    key = ''.join([key[i % key_len] for i in range(len(doc))])
    decoded_doc = []
    for i, char in enumerate(doc):
        shift = (ALPHABET.find(char) + ALPHABET.find(key[i])) % 26
        decoded_doc.append(ALPHABET[shift])
    decoded_doc = ''.join(decoded_doc)
    return ''.join(decoded_doc)


if __name__ == "__main__":
    # Read cipher text and remove spacing
    with open('cipher.txt', 'r') as f:
        doc = f.read()
        doc = "".join(doc.split()) 
    
    total_time = time.time()

    start_time = time.time()
    key_lens = get_key_lens(MAX_KEY_LEN, doc)
    time_key_kens = (time.time() - start_time)

    print(f'Key lengths:{key_lens}')
    key_len = int(input("Choose key length:")) # Define most probable one based on kasiski results
    print(f'Performing frequency analysis with key length: {key_len}\n\n')
    print(f'Original document:\nLength:{len(doc)}\nText:\n{doc}')

    start_time = time.time()
    L, lf = frequency_analysis(doc, key_len)
    keys = candidate_keys(lf)
    time_candidate_keys = (time.time() - start_time) #time for freq analysis + candidate keys

    print(f'\nOriginal document divided into {key_len} columns:\n{L}\n\n')
    num_examples = int(input("Number of most probable keys:"))

    start_time = time.time()
    keys, stopword_counts = get_top_candidates(doc, keys, k=num_examples)
    time_top_candidates = (time.time() - start_time)

    #keys = ['BDLAEKCY']
    for key, count in zip(keys,stopword_counts):
        decoded_doc = decipher(doc, key)
        print(f'\nKey: {key}:\nStopword count: {count}\nDecoded text:\n{decoded_doc}')
    
    key = input("Final key (Type n to ignore):")
    if key != "n":
        deciphered_doc = decipher(doc, key)
        print("\n\n###################################  FINAL TEXT ###################################")
        print(f'Key: {key}:\nDecoded text:\n{deciphered_doc}')

    total_time = (time.time() - total_time)
    # Print time spent
    print("\n\n#####Execution time of various parts of this task#####")
    print(f'Key length frequencies: {time_key_kens}s')
    print(f'Candidate keys: {time_candidate_keys}s')
    print(f'Top candidates: {time_top_candidates}s')
    print(f'In total (with your involvations): {total_time}s')

    
