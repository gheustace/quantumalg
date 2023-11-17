from qiskit import QuantumCircuit, Aer, execute
from qiskit.quantum_info import DensityMatrix

def deletion_circuit(rho):
    num_qubits = rho.num_qubits
    circuit = QuantumCircuit(num_qubits, num_qubits)

    for qubit in range(num_qubits):
        circuit.h(qubit)
    
    circuit.measure(range(num_qubits), range(num_qubits))
    
    simulator = Aer.get_backend('qasm_simulator')
    job = execute(circuit, simulator, shots=1)
    result = job.result()
    measurement_result = result.get_counts(circuit)

    measured_state = list(measurement_result.keys())[0]
    certificate_state_string = '|{}⟩⟨{}|'.format(measured_state, measured_state)

    certificate_state_density_matrix = DensityMatrix.from_label(measured_state)

    return certificate_state_string, certificate_state_density_matrix

input_state_rho = DensityMatrix.from_label('00')  # Just an example state

certificate_string_state, certificate_density_matrix = deletion_circuit(input_state_rho)
print("Certificate string state:", certificate_string_state)
print("Certificate state as a density matrix:")
print(certificate_density_matrix)
