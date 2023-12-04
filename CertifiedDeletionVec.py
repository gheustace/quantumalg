from qiskit.quantum_info import DensityMatrix
from qiskit.quantum_info import Statevector
import random
from bitstring import BitArray
import numpy as np
from sklearn.preprocessing import normalize
from qiskit import Aer

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
    corr_bitstring = ""
    for i in range(len(syndrome)):
        if syndrome[i] == "1":
            if err_bitstring[i] == "0":
                corr_bitstring += "1"
            else:
                corr_bitstring += "0"
        else:
            corr_bitstring += err_bitstring[i]
    return corr_bitstring

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

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

def twos(num, length):
    return BitArray(int=num, length=length).bin

def key_generation(m, theta, r, hash_family_size):
    statevec_str = ""
    k = hamming(theta)
    r_hadamard = get_r_hadamard(r, theta)
    statevec_str += r_hadamard
    statevec_str += theta
    s = m - k
    n = s + k
    tau = s + k
    mu = s + k
    hpa = UniversalHashFamily(hash_family_size, 2**(n-1))
    hec = UniversalHashFamily(hash_family_size, 2**(tau-1))
    u = rand_key(n)
    statevec_str += u
    d = rand_key(mu)
    statevec_str += d
    e = rand_key(tau)
    statevec_str += e
    return m, theta, r, hpa, hec, statevec_str

def encryption(m, theta, r, msg, keystate_str, hpa, hec):
    k = hamming(theta)
    s = m - k
    r_hadamard = keystate_str[0:k]
    theta = keystate_str[k:s+2*k]
    u = keystate_str[s+2*k:2*s+3*k]
    d = keystate_str[2*s+3*k:3*s+4*k]
    e = keystate_str[3*s+4*k:4*s+5*k]
    r_computational = get_r_computational(r, theta)
    print(f"R Computational: {r_computational}")
    x = hpa(1, BitArray(bin=r_computational).int)
    p = hec(1, BitArray(bin=r_computational).int) ^ BitArray(bin=d).int
    q = BitArray(bin=synd(r_computational, r_computational)).int ^ BitArray(bin=e).int
    weisner_str = ""
    print(f"theta: {theta}")
    print(f"r: {r}")
    for i in range(len(theta)):
        if theta[i] == "0":
            weisner_str += r[i]
        else:
            if r[i] == "1":
                weisner_str += "-"
            else:
                weisner_str += "+"
    print(f"Weisner String: {weisner_str}")
    msgenc_str = twos(BitArray(bin=msg).int ^ x ^ BitArray(bin=u).int, m) + twos(p, m) + twos(q, m)
    return m, theta, r, hpa, hec, weisner_str + msgenc_str

# def deletion(rho):
#     num_qubits = rho.num_qubits
#     circuit = QuantumCircuit(num_qubits, num_qubits)
    
#     for qubit in range(num_qubits):
#         circuit.h(qubit)
    
#     circuit.measure(range(num_qubits), range(num_qubits))

#     simulator = Aer.get_backend('qasm_simulator')
#     job = execute(circuit, simulator, shots=1)
#     result = job.result()
#     measurement_result = result.get_counts(circuit)

#     # measured_state = list(measurement_result.keys())[0]
#     # certificate_state_string = '|{}⟩⟨{}|'.format(measured_state, measured_state)
#     certificate_state_density_matrix = DensityMatrix.from_label(measured_state)
#     return certificate_state_density_matrix

def decryption(keyvector, ciphertextvector, Hec, Hpa):
    # Apply Hadamard to Weisner part of ciphertext
    weisner = ciphertextvector[0:m]
    print(f"Weisner String: {weisner}")
    # for i in range(len(weisner)):
    #     if weisner[i] == '1':
    #         weisner[i] = '-'
    #     if weisner[i] == '0':
    #         weisner[i] = '+'
    weisner = weisner.replace('1', '-')
    weisner = weisner.replace('0', '+')
    weisner_vec = Statevector.from_label(weisner)
    weisner_matrix = DensityMatrix(weisner_vec)
    r = weisner_matrix.measure()
    #3
    q = ciphertextvector[len(ciphertextvector) - m:]
    e = keyvector[len(keyvector) - m:]

    # print(get_r_computational(f"{r[0]}", f"{theta}"))
    # print(f"{twos(BitArray(bin=q).int ^ BitArray(bin=e).int)}")

    r_prime = corr(get_r_computational(f"{r[0]}", f"{theta}"), f"{(BitArray(bin=q).int ^ BitArray(bin=e).int)}")
    #4
    p_prime = Hec(1, BitArray(bin=r_prime).int) ^ BitArray(bin=keyvector[len(keyvector) - 2*m:len(keyvector)- m]).int
    #5
    if (twos(p_prime, m) == ciphertextvector[len(ciphertextvector) - 2*m:len(ciphertextvector)- m]):
        gamma = '0'
    else:
        gamma = '1'
    #6 
    x_prime = Hpa(1, BitArray(bin=r_prime).int)
    sigma_str = BitArray(bin=ciphertextvector[m:2*m]).int ^ x_prime ^ BitArray(bin=keyvector[hamming(theta) + m: hamming(theta) + 2*m]).int

    return twos(sigma_str, m)

# def verification(keystate, certificate_string_state, delta):
#     #1
#     y_prime = get_r_hadamard(certificate_string_state)
#     #2
#     q = key_state[:hamming(theta)]
#     #3
#     if(hamming(q ^ y_prime < delta * hamming(theta))):
#         return 1    
#     else:
#         return 0
    
    
m, theta, r, hpa, hec, keystatevector = key_generation(m=6, theta=rand_key(6), r=rand_key(6), hash_family_size=10)
print("Key State:")
print(keystatevector)
message = "010110"
print("Message:")
print(message)
m, theta, r, hpa, hec, ciphertextstatevector = encryption(m, theta, r, message, keystatevector, hpa, hec)
print("Ciphertext State:")
print(ciphertextstatevector)
decryptionstate = decryption(keystatevector, ciphertextstatevector, hec, hpa)
print("Decryption State:")
print(decryptionstate)