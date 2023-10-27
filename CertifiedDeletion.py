from qiskit.quantum_info import DensityMatrix
from qiskit.quantum_info import Statevector
import random
from bitstring import BitArray
import numpy as np
from sklearn.preprocessing import normalize

# Random Key Generator
def rand_key(p):
    key1 = ""
    for i in range(p):
        temp = str(random.randint(0, 1))
        key1 += temp
    return(key1)

# Hamming Weight Function
def hamming(x):
    weight = 0
    for i in range(len(x)):
        if x[i] == "1":
            weight += 1
    return weight

def is_prime(n):
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n%i==0:
            return False    
    return True

def synd(err_bitstring, corr_bitstring):
    syndrome = ""
    for i in range(len(err_bitstring)):
        if err_bitstring[i] == corr_bitstring[i]:
            syndrome += "0"
        else:
            syndrome += "1"
    return syndrome

def corr(err_bitstring, syndrome):
    for i in range(len(syndrome)):
        if syndrome[i] == "1":
            if err_bitstring[i] == "0":
                err_bitstring[i] = "1"
            else:
                err_bitstring[i] = "0"
    corr_bitsring = err_bitstring
    return corr_bitsring

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

def get_r_hadamard(r_bitstring, theta_bitstring):
    r_hadamard = ""
    for i in range(len(r_bitstring)):
        if theta_bitstring[i] == "1":
            r_hadamard += r_bitstring[i]
    return r_hadamard

def get_r_computational(r_bitstring, theta_bitstring):
    r_computational = ""
    for i in range(len(r_bitstring)):
        if theta_bitstring[i] == "0":
            r_computational += r_bitstring[i]
    return r_computational

def key_generation(m, hash_family_size):
    statevec_str = ""
    theta = rand_key(m)
    k = hamming(theta)
    statevec_str += theta
    print(f"theta{len(theta)}")
    r = rand_key(m)
    r_hadamard = get_r_hadamard(r, theta)
    statevec_str += r_hadamard
    print(f"r_hadamard{len(r_hadamard)}")
    theta = BitArray(bin=theta).int
    r_hadamard = BitArray(bin=r_hadamard).int
    s = m - k
    n = s + k
    tau = s + k
    mu = s + k
    hpa = UniversalHashFamily(hash_family_size, 2**n)
    hec = UniversalHashFamily(hash_family_size, 2**tau)
    u = rand_key(n)
    statevec_str += u
    print(f"u{len(u)}")
    u = BitArray(bin=u).int
    d = rand_key(mu)
    statevec_str += d
    print(f"d{len(d)}")
    d = BitArray(bin=d).int
    e = rand_key(tau)
    statevec_str += e
    print(f"e{len(e)}")
    e = BitArray(bin=e).int
    hpa_index = random.randint(1, hash_family_size - 1)
    hec_index = random.randint(1, hash_family_size - 1)
    # statevec_str += bin(hpa_index)[2:]
    # statevec_str += bin(hec_index)[2:]
    print(statevec_str)
    statevector = Statevector.from_label(statevec_str)
    print(statevector.num_qubits)
    rho = DensityMatrix(statevector)
    return hpa, hec, rho, s, k, r, theta

def encryption(msg_state, key_state, hpa, hec, s, k):
    # msg_vector = msg_state.to_statevector()
    hpa, hec, key_state, s, k, r, theta = key_generation(2, 10)
    key_vector = key_state.to_statevector()
    
    # r_computational = get_r_computational(r, theta)
    msg = "010"
    msg = BitArray(bin=msg).int
    statevec_str = list(key_vector.probabilities_dict().keys())[0]
    r_hadamard = statevec_str[0:k]
    theta = statevec_str[k:s+2*k]
    u = statevec_str[s+2*k:2*s+3*k]
    d = statevec_str[2*s+3*k:3*s+4*k]
    e = statevec_str[3*s+4*k:4*s+5*k]
    print(f"r: {len(r)}")

    r_computational = get_r_computational(r, theta)
    x = hpa(4, BitArray(bin=r_computational).int)
    p = hec(5, BitArray(bin=r_computational).int) ^ BitArray(bin=d).int
    q = BitArray(bin=synd(r_computational, r_computational)).int ^ BitArray(bin=e).int
    weisner_str = ""
    for i in range(len(theta)):
        if theta[i] == "0":
            weisner_str += r[i]
        else:
            if r[i] == 1:
                weisner_str += "-"
            else:
                weisner_str += "+"
    msgenc_str = '{0:b}'.format(msg ^ x ^ BitArray(bin=u).int) + '{0:b}'.format(p) + '{0:b}'.format(q)
    print(weisner_str + msgenc_str)
    statevector = Statevector.from_label(weisner_str + msgenc_str)
    rho = DensityMatrix(statevector)


    return rho

print(encryption(1, 1, 1, 1, 1, 1))
