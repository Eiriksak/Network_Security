import sympy
import random
import hashlib

def gen_pubkeys(L, N=160):
    """Generate shared global public key values p, q and g
    Args:
        L (int):  512 <= L <= 1024 and L is a multiple of 64
        N (int): bit length of q

    Returns:
        p: prime number where 2^(L-1) < p < 2^(L) 
        q: prime divisor of (p-1) where 2^(N-1) < q < 2^(N)
        g: g=h^((p-1)/q)mod p where 1<h<p-1 and g > 1
     """
    if L not in range(512,1025) or L%64 != 0:
        raise ValueError("Choose L: 512 <= L <= 1024 and L is a multiple of 64")
    p, g = 1, 1
    while not sympy.isprime(p):
        m = random.randrange(2**(L-N-1), 2**(L-N))
        q = sympy.randprime(2**(N-1), 2**N)
        p = m * q + 1
    assert (p-1)%q == 0
    while g <= 1:
        h = random.randrange(1, p-1)
        g =  pow(h, (p-1)//q, p)
    return p,q,g


def gen_userkeys(p, q, g):
    """Generates user's private key (x) and public key (y)
    Args:
        p, q, g: shared global public key parameters (from gen_pubkeys)
    
    Returns:
        x: user's private key
        y: user's public key
    """
    x = random.randrange(0, q) 
    y = pow(g, x, p)
    return x, y

def mod_inv(a, m):
    """Finds the modular multiplicative inverse of a number a under modulo m
    This method is directly taken from:
    https://www.geeksforgeeks.org/multiplicative-inverse-under-modulo-m/
    """
    m0 = m 
    y = 0
    x = 1
  
    if (m == 1) : 
        return 0
  
    while (a > 1) : 
        q = a // m 
        t = m 
        m = a % m 
        a = t 
        t = y 
        y = x - q * y 
        x = t 
    if (x < 0) : 
        x = x + m0 
    return x


def sign_message(message, p, q, g, x):
    """Digital signature of a message based on public key components and a private key
    Args:
        p, q, g: shared global public key parameters (from gen_pubkeys)
        x: private key
        message (string): message to be signed

    Returns:
        signature pair (r, s) and the message itself 
    """
    k = random.randrange(0, q)
    r = pow(g, k, p)%q
    HM = hashlib.sha256(message.encode('utf-8')).hexdigest() # hashed message
    k_inv = mod_inv(k, q)
    s = ((k_inv*(int(HM,16) + x*r)))%q
    return r, s, message


def verify_message(message, p, q, g, r, s, y):
    """Verifies a digital signature
    Args:
        p, q, g: shared global public key parameters (from gen_pubkeys)
        y: public key
        r, s: signature pair
        message (string): message to be signed
    
    Returns:
        Boolean whether or not it was verified (r=v)
    """
    w = mod_inv(s,q)
    HM = hashlib.sha256(message.encode('utf-8')).hexdigest() # hashed message
    u1 = (int(HM, 16)*w)%q
    u2 = (r*w)%q
    _gu1 = pow(g, u1, p)
    _yu2 = pow(y, u2, p)
    v = ((_gu1*_yu2)%p)%q
    if v == r:
        return True
    return False
