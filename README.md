# Annotations-for-OpenQASM-3.0

## Overview

This project provides a set of Python modules designed to extend OpenQASM 3.0 circuits through annotations. These annotations allow for the selection of quantum processing units (QPUs), execution modifications, and circuit provenance tracking.

## QPROV Service

This project relies on a local QPROV service to fetch information about available QPUs and their characteristics. The service is expected to be running at `http://localhost:5020/qprov`. Ensure that this service is active and accessible for the modules to function correctly. The QProv service can be found on GitHub at [UST-QuAntiL/quantil-docker](https://github.com/UST-QuAntiL/quantil-docker).

## Modules

### QPU_Selection(As A Proof Of Concept!)
- **Purpose**: Selects a QPU based on user-defined criteria such as the minimum number of qubits and specific performance metrics.
- **Key Functions**:
  - `check_qpu_annotations`: Parses OpenQASM strings to identify and process QPU selection annotations.
  - `get_all_qpu`: Retrieves a list of available QPUs from IBM.
  - `select_qpu`: Filters and selects the best QPU based on the specified criteria.
 
- **Add this annotation to automatically select a quantum computer based on your requirements:**

  - `@select_qpu(min_qubits, metric)`: Selects the best QPU based on specified criteria
  - `min_qubits`: Minimum number of qubits required
  - **Available optimization metrics:** 
    - `max_gate_time`: Maximum gate time
    - `t1_time`: Average T1 relaxation time 
    - `t2_time`: Average T2 coherence time
    - `readout_error`: Average readout error rate
    - `multi_qubit_gate_error`: Average multi-qubit gate error rate
    - `single_qubit_gate_error`: Average single-qubit gate error rate
    - `average_multi_qubit_gate_time`: Average time for multi-qubit gates
    - `average_single_qubit_gate_time`: Average time for single-qubit gates

### Execution_Annotation

- **Purpose**: bitstring manipulation and formatting for results of OpenQASM 3 circuits 
- **Key Functions**:
  - `check_execution_annotations`: Identifies and applies execution-related annotations in OpenQASM strings.
  - `reverse_bitString`: Reverses the bitstrings in the measurement results.
  - `format_counts_hex` and `format_counts_decimal`: Format the measurement results into hexadecimal and decimal representations, respectively.
 
- **Add these annotations to process your circuit execution results:**
   - `@reverse_bitString`: Reverses the bit strings in the measurement results
   - `@format_to_hex`: Converts measurement results to hexadecimal representation
   - `@format_to_dec`: Converts measurement results to decimal representation

### Circuit_Provenance

- **Purpose**: Provides detailed provenance information about the quantum circuit and the QPU used.
- **Key Functions**:
  - `check_annotations`: Processes annotations related to qubit and gate characteristics, QPU provenance, and calibration matrices.
  - `get_qubit_characteristics` and `get_gate_characteristics`: Retrieves detailed characteristics of qubits and gates used in the circuit.
  - `get_qpu_provenance`: Fetches provenance metrics for the selected QPU.
  - `get_calibration_matrix`: Returns the calibration matrix for a specific quantum computer.
- **Add these annotations to your QASM code to get information about the quantum hardware:**

   - `@get_qubit_characteristics`: Returns characteristics of the qubits used in your circuit (T1 time, T2 time, readout error)
   - `@get_gate_characteristics`: Returns characteristics of the gates used in your circuit (gate time, gate fidelity)
   - `@get_qpu`: Returns detailed information about the quantum computer being used
   - `@get_calibration_matrix`: Returns the calibration matrix for the quantum computer

## Example Use Case

The `Example_Usecase` directory contains a sample OpenQASM file (`test_circuit.qasm`) and its corresponding output (`example_output.txt`). This example (`qiskit_execution.py`) demonstrates how annotations can be used to select a QPU, retrieve qubit and gate characteristics, and format execution results, as well as where to integrate them into the execution pipeline.

## Getting Started
1. **Dependencies**: 
   - Ensure you have Python installed.
   - Install the following Python packages:
     - `requests`
     - `pandas`
     - `qiskit`
     - `qiskit-ibm-runtime`
     - `qiskit-qasm3`
   - The QPROV service is required and should be running locally. You can set it up using the [UST-QuAntiL/quantil-docker](https://github.com/UST-QuAntiL/quantil-docker) repository.
2. **Running the Example**: Execute the provided example to see how annotations are processed and results are generated.
