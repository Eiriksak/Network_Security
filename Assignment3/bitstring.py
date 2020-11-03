class BitString:
    """Helper class for creation and manupilation of binary data"""
    
    def __init__(self, bits):
        """Initiate a BitString object
        Args:
            bits: list of integer (0/1) values 
        """
        self.bits = bits
        self._validate_bits()
        
    @classmethod
    def from_hex(cls, hexstring, n):
        """Initiate a BitString object from hex values
        Args:
            hexstring: integer in hex format
            n: number of bits in BitString
        """
        bits = bin(hexstring)[2:].rjust(n,'0')
        bits = [int(i) for i in bits]
        return cls(bits)
    
    @classmethod
    def from_bitstring(cls, bitstring):
        """Initiate a BitString object from string of bits
        Args:
            bitstring: string of bits (0/1)
        """
        bits = [int(i) for i in bitstring]
        return cls(bits)
    
    @staticmethod
    def to_bitstring(n, l):
        """Converts an integer (n) to a (l) length bitstring"""
        return bin(n)[2:].rjust(l,'0')
    
    def copy(self):
        return BitString(self.bits[:])
    
    def _validate_bits(self):
        """Ensure all bits are either 0 or 1"""
        if any([bit not in [0,1] for bit in set(self.bits)]):
            raise ValueError('Bits should be 0 or 1')
        return
    
    def to_int(self):
        """Returns integer representation of self"""
        bitstring = ''.join(str(i) for i in self.bits)
        return int(bitstring, 2)
    
    def to_string(self):
        """Returns ASCII string representation of self"""
        assert len(self.bits)%8 == 0
        string = []
        for i in range(0, len(self.bits), 8):
            byte = self.bits[i:i+8]
            byte = ''.join([str(i) for i in byte])
            string.append(chr(int(byte,2)))
        return ''.join(string)
    
    def to_hex(self):
        """Returns hex representation of self"""
        return self.to_string().encode().hex()
    
    def add(self, bits):
        """Performs addition in modulo 2^32
        Args:
            bits (BitString): object with bits to be added with self
        """
        if not isinstance(bits, BitString):
            raise TypeError('Addition is only allowed with another BitString Object')
        num = (self.to_int() + bits.to_int())%pow(2,32)
        bitstring = self.to_bitstring(num, len(self.bits))
        self.bits = [int(i) for i in bitstring]
        self._validate_bits()
        return BitString(self.bits)
        
    def extend(self, bits):
        """Appends new bits to itself
        Args:
            bits (BitString): object with bits to be appended to itself
        """
        if not isinstance(bits, BitString):
            raise TypeError('Extention is only allowed with another BitString Object')
        self.bits.extend(bits.bits)
        return BitString(self.bits[:])
        
    def unshift(self, bits):
        """Adds new bits to the beginning of self
        Args: 
            bits (BitString): object with bits to be added to itself
        """
        if not isinstance(bits, BitString):
            raise TypeError('Extention is only allowed with another BitString Object')
        self.bits = bits.bits + self.bits
        return BitString(self.bits[:])
        
    def rotate_right(self, n):
        """Performs a circular right shift operation
        Takes n last bits (right) and places them in front (left)
        
        Args:
            n: number to be shifted
        """
        self.bits = self.bits[-n:] + self.bits[:-n]
        return BitString(self.bits[:])
            
            
    def shift_right(self, n):
        """Shifts (self) bits n places to the right
        Remaining bits to the left becomes zero
        """
        left_pad = [0]*n
        self.bits = left_pad + self.bits[:-n]
        return BitString(self.bits[:])
        
    def bitwise_xor(self, bits):
        """Performs a bitwise XOR with another BitString
        Args:
            bits (BitString): object with bits to perform XOR with
        """
        assert len(self.bits) == len(bits.bits)
        if not isinstance(bits, BitString):
            raise TypeError('XOR is only allowed with another BitString Object')
        
        self.bits = [0 if i==j else 1 for i,j in zip(self.bits, bits.bits)]
        return BitString(self.bits[:])
        
    def bitwise_and(self, bits):
        """Performs a bitwise AND with another BitString
        Args:
            bits (BitString): object with bits to perform AND with
        """
        if not isinstance(bits, BitString):
            raise TypeError('Bitwise AND is only allowed with another BitString Object')
        self.bits = [1 if i and j else 0 for i,j in zip(self.bits, bits.bits)]
        return BitString(self.bits[:])
        
    def bitwise_not(self):
        """Performs a bitwise NOT with another BitString"""
        self.bits = [1 if not bit else 0 for bit in self.bits]
        return BitString(self.bits[:])
        
        

    