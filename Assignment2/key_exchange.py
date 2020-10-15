import random
import sympy

class DiffieHellman:

    def __init__(self, generator=None, prime=None):
        self.generator = generator if generator is not None else sympy.randprime(0, int("1"*64,2)) 
        self.prime = prime if prime is not None else sympy.primitive_root(self.generator)
        self.private_key = random.randint(1, self.generator)

    def get_public_key(self):
        return pow(self.prime, self.private_key, self.generator)

    def get_session_key(self, public_key):
        return pow(public_key, self.private_key, self.generator)

    def get_generator(self):
        return self.generator

    def get_prime(self):
        return self.prime