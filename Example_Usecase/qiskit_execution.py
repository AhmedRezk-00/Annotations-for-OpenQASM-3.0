import sys
import os
# importing directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Annotations.QPU_Selection import QPU_Selection
from Annotations.Circuit_Provenance import Circuit_Provenance
from Annotations.Execution_Annotation import Execution_Annotation
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import loads

service = QiskitRuntimeService(channel="ibm_quantum", token="INSERT TOKEN")
with open('Example_Usecase/test_circuit.qasm', 'r') as f:
    qasm_str = f.read()

#intializing QPU_Selection before assigning a backend to the circuit
qpu_selector = QPU_Selection()
qpu_name = qpu_selector.check_qpu_annotations(qasm_str)
print( "Annotation chose: ", qpu_name)


circuit = loads(qasm_str)
backend = service.backend(qpu_name)
transpiled_circuit = transpile(circuit, backend)
print(backend.name)

#intializing Circuit_Provenance right after transpiling the circuit
circuit_provenance = Circuit_Provenance(backend.name,transpiled_circuit)
print(circuit_provenance.check_annotations(qasm_str))

job = Sampler(backend).run([transpiled_circuit])
job_result = job.result()
creg_name = circuit.cregs[0].name
counts = job_result[0].data.__getattribute__(creg_name).get_counts() 

#intializing the Execution_Annotation class after getting the counts
execution_annotation = Execution_Annotation()
print(execution_annotation.check_execution_annotations(qasm_str, counts))
