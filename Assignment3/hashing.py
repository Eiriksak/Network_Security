"""
SHA256 implementation from scratch by using a helper class BitString.
DO NOT WORK! 
The code need bug fixes and should not be used in any cases..
"""
from bitstring import BitString

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

h0 = 0x6a09e667
h1 = 0xbb67ae85
h2 = 0x3c6ef372
h3 = 0xa54ff53a
h4 = 0x510e527f
h5 = 0x9b05688c
h6 = 0x1f83d9ab
h7 = 0x5be0cd19
H = [h0, h1, h2, h3, h4, h5, h6, h7]

def pad_len(bitlen):
    """Calculates number of bits needed for message padding
    Args:
        bitlen: number of bits in the message
        
    Returns:
        bitstring to pad after the message. "1" followed by
        k zero bits where l+1+k=448mod512. l=message length.
    """
    length = 448-(bitlen%512)
    if length < 0:
        length += 512
    return '1'.ljust(length,'0')


def block_bits(bitlen):
    """Calculates 64-bit block to be added at the end of message
    Args:
        bitlen: number of bits in the original message (before padding)
        
    Returns:
        (String) 64-bit block which is a binary representation of the
        message length
    """
    bits = bin(bitlen)[2:].rjust(64,'0')
    assert len(bits) == 64
    return bits


def char_to_bitstring(char):
    """Converts an ASCII character to 8-bit string"""
    return bin(ord(char))[2:].rjust(8,"0")


def pad_message(message):
    """Adds padding to an ASCII message
    Args:
        message: original message in ASCII characters
        
    Returns:
        bitstring which is a multiple of 512. The bitstring
        is padded based SHA-256 algorithm.
    
    """
    bitstring = ''.join([char_to_bitstring(c) for c in message])
    bitlen = len(bitstring)
    padding = pad_len(bitlen)
    len_bits = block_bits(bitlen)
    # Add padding and 64-bit message block
    bitstring = bitstring + padding + len_bits
    assert len(bitstring)%512==0
    return bitstring

def parse_block(bitstring):
    """Parse message into 16 32-bit blocks
    Args:
        bitstring: bitstring of length 512
    
    Returns:
        list of 16 32-bit bitstrings
    """
    M = [bitstring[i:i + 32] for i in range(0, 512, 32)]
    assert len(M) == 16
    return M


def sha256(message, H=H, K=K):
    bitstring = pad_message(message)
    chunks = [] # bitstring chunks of 512 bits
    for i in range(0, len(bitstring), 512):
        chunks.append(bitstring[i:i+512])
    # Initialize hash values as BitString objects
    # They are originally 32 bit hex values
    h0,h1,h2,h3,h4,h5,h6,h7 = list(map(lambda x: BitString.from_hex(x, 32), H))
    # Initialize round constants as BitString objects
    K = [BitString.from_hex(k, 32) for k in K]
    for chunk in chunks: # chunk is bitstring of size 512
        # Run 64 rounds in compression function
        # We need W(i) and K(i) for i=1,..,64
        # Break the 16 first rounds into 32-bit blocks from the chunk
        M = parse_block(chunk) 
        # The 48 next rounds will be computed by
        # W(i) = Wⁱ⁻¹⁶ + σ⁰ + Wⁱ⁻⁷ + σ¹ where,
        # σ⁰ = (Wⁱ⁻¹⁵ ROTR⁷(x)) XOR (Wⁱ⁻¹⁵ ROTR¹⁸(x)) XOR (Wⁱ⁻¹⁵ SHR³(x))
        # σ¹ = (Wⁱ⁻² ROTR¹⁷(x)) XOR (Wⁱ⁻² ROTR¹⁹(x)) XOR (Wⁱ⁻² SHR¹⁰(x))
        # ROTRⁿ(x) = Circular right rotation of 'x' by 'n' bits
        # SHRⁿ(x)  = Circular right shift of 'x' by 'n' bits
        W = M + ['0'.rjust(32,'0')]*48
        W = [BitString.from_bitstring(w) for w in W]
        for i in range(16, 64):
            _W = [w.copy() for w in W]
            sigma1 = _W[i-15].rotate_right(7).bitwise_xor(_W[i-15].rotate_right(18))\
            .bitwise_xor(_W[i-15].shift_right(3))
            sigma2 = _W[i-2].rotate_right(17).bitwise_xor(_W[i-2].rotate_right(19))\
            .bitwise_xor(_W[i-2].shift_right(10))
            W[i] = _W[i-16].add(sigma1).add(_W[i-7]).add(sigma1)
        # Initialize eight working variables
        a,b,c,d,e,f,g,h = h0,h1,h2,h3,h4,h5,h6,h7
        # Compression function
        
        for i in range(64):
            _e = e.copy()
            _a = a.copy()
            _c = c.copy()
            _f = f.copy()
            _h = h.copy()
            _g = g.copy()
            _b = b.copy()
            sum_e = _e.rotate_right(6).bitwise_xor(_e.rotate_right(11))\
            .bitwise_xor(_e.rotate_right(25))
            sum_a = _a.rotate_right(2).bitwise_xor(_a.rotate_right(13))\
            .bitwise_xor(_a.rotate_right(22))
            Ch = _e.bitwise_and(_f).bitwise_xor(_e.bitwise_not().bitwise_and(_g))
            maj = _a.bitwise_and(_b).bitwise_xor(_a.bitwise_and(_c))\
            .bitwise_xor(_b.bitwise_and(_c))
            T1 =  _h.add(sum_e).add(Ch).add(K[i]).add(W[i])
            T2 = sum_e.add(maj)
            h,g,f,e,d,c,b,a = g,f,e,d.add(T1),c,b,a,T1.add(T2)
        
        # Add compressed chunk to current hash val
        for h, char in zip([h0,h1,h2,h3,h4,h5,h6,h7],[a,b,c,d,e,f,g,h]):
            char = BitString.from_bitstring(char.bits)
        # Produce final hash val
        digest = h0.extend(h1).extend(h2).extend(h3).extend(h4)\
                .extend(h5).extend(h6).extend(h7)
        return digest