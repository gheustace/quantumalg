from qiskit.quantum_info import DensityMatrix
import random
from bitstring import BitArray

# Random Key Generator
def rand_key(p):
    key1 = ""
    for i in range(p):
        temp = str(random.randint(0, 1))
        key1 += temp
    return(key1)

# Hamming Weight Function
def hamming(x):
    x -= (x >> 1) & 0x5555555555555555
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    return ((x * 0x0101010101010101) & 0xffffffffffffffff ) >> 56

def is_prime(n):
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n%i==0:
            return False    
    return True

# Universal Hash Function Family Generator
class UniversalHashFamily:
    def __init__(self, number_of_hash_functions, number_of_buckets, min_value_for_prime_number=2, bucket_value_offset=0):
        self.number_of_buckets = number_of_buckets
        self.bucket_value_offset = bucket_value_offset
        
        primes = []
        number_to_check = min_value_for_prime_number
        while len(primes) < number_of_hash_functions:
            if is_prime(number_to_check):
                primes.append(number_to_check)
            number_to_check += random.randint(1, 1000)

        self.hash_function_attrs = []
        for i in range(number_of_hash_functions):
            p = primes[i]
            a = random.randint(1, p)
            b = random.randint(0, p)
            self.hash_function_attrs.append((a, b, p))
    
    def __call__(self, function_index, input_integer):
        a, b, p = self.hash_function_attrs[function_index]
        return (((a*input_integer + b)%p)%self.number_of_buckets) + self.bucket_value_offset


m = 10 # Total number of qubits sent from encrypting to decrypting party
theta = rand_key(m)
theta = BitArray(bin=theta).int
k = hamming(theta)
s = m - k
lam = 10 # Security Parameter
n = s + k
lam = s + k
tau = s + k
mu = s + k

print(n, lam, tau, mu, m, s, k)
#k = 10 # Length of string used for verification
# s = m - k
# n, lam, tau, mu


rho = DensityMatrix.from_label('+0')

theta = 0
r_itilde = 0
# u = rand_key(n)
# d = rand_key(mu)
# e = rand_key(tau)
hpa = UniversalHashFamily(20, 100)
hec = UniversalHashFamily(20, 100)

# Probabilities for measuring both qubits
probs = rho.probabilities()
print('probs: {}'.format(probs))

