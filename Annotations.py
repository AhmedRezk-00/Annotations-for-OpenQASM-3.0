import requests
from qiskit import transpile
import pandas as pd
QPROV_URL = "http://quantil-docker-1-qprov-1:5020/qprov"

class Circuit_Provenance:
    def __init__(self, backend, transpiled_circuit):
        self.backend = backend
        self.transpiled_circuit = transpiled_circuit


    def check_annotations(self, qasm_string):
            results = {}
            
            if "@get_qubit_characteristics" in qasm_string:
                results["qubit_characteristics"] = self.get_qubit_characteristics(self.backend, self.transpiled_circuit)
                
            if "@get_gate_characteritics" in qasm_string:
                results["gate_characteristics"] = self.get_gate_characteristics(self.backend, self.transpiled_circuit)
                
            if "@get_qpu" in qasm_string:
                results["qubit_gates"] = self.get_qpu_provenance()

            if "@get_calibration_matrix" in qasm_string:
                results["calibration_matrix"] = self.get_calibration_matrix(self.backend)
                
            return results
    

    def get_qpu_url(backend):
            available_computer = []
            r = requests.get("http://localhost:5020/qprov/providers")
            r.raise_for_status()
            providers = r.json()["_embedded"]["providerDtoes"]
            for provider in providers:
                if provider["name"] == "ibmq":
                    URL_for_qpu = provider["_links"]["qpus"]["href"]
                    get_available_qpu = requests.get(URL_for_qpu)
                    get_available_qpu.raise_for_status()
                    available_qpu = get_available_qpu.json()["_embedded"]["qpuDtoes"]
                    for qpu in available_qpu:
                        if qpu["name"] == backend:
                            return qpu["_links"]["self"]["href"]

#this method returns the physical qbits and the gates that has been used for transpilation 
    def transpiled_circuit_information(transpiled):
        used_qubits = set()    
        qubit_gates = {} 
        for instruction in transpiled.data:
            gate_name = instruction.operation.name
            qubits = instruction.qubits
            physical_qubits = [qubit._index for qubit in qubits]
            used_qubits.update(physical_qubits)
            gate_label = f"{gate_name}{physical_qubits}" if len(physical_qubits) > 1 else gate_name
            for qubit in physical_qubits:
                qubit_gates.setdefault(qubit, []).append(gate_label)
                            
        return sorted(list(used_qubits)), qubit_gates

#returns only a list of physical qbits that has been used for transpilation 
    def get_physical_qubits(self,transpiled):
        qubits = self.transpiled_circuit_information(transpiled)
        return qubits[0]

#returns a list of gates for a specific qbit
    def get_qubit_gates(self,transpiled, qubit):
        qubit_gates = self.transpiled_circuit_information(transpiled)
        qubit_gates= qubit_gates[1]
        if qubit in qubit_gates:
            return list(dict.fromkeys(qubit_gates[qubit]))  
        return []

#List of complete QProv URLs for the qubit ID
    def get_qubit_ids(self,backend,transpiled):
        physical_qubits = self.get_physical_qubits(transpiled)
        r = requests.get(f"{self.get_qpu_url(backend)}/qubits")
        r.raise_for_status()
        qubits = r.json()["_embedded"]["qubitDtoes"]
        qubit_urls = []
        for qubit in qubits:
            physical_num = int(qubit['name'])
            if physical_num in physical_qubits:
                qubit_url = qubit["_links"]["self"]["href"]
                qubit_urls.append(qubit_url)
        return qubit_urls

#dictionary containing qubit names and their characteristics
    def get_qubit_characteristics(self,backend, transpiled):

        qubit_urls = self.get_qubit_ids(backend, transpiled)
        characteristics_dict = {}
        
        t1_times = []
        t2_times = []
        readout_errors = []
        
        for qubit_url in qubit_urls:
                r = requests.get(qubit_url)
                r.raise_for_status()
                qubit_name = r.json()["name"]
                url = f"{qubit_url}/characteristics"
                r = requests.get(url)
                r.raise_for_status()
                characteristics = r.json()["_embedded"]["qubitCharacteristicsDtoes"][0]
                
                t1_time = characteristics["t1Time"]
                t2_time = characteristics["t2Time"]
                readout_error = characteristics["readoutError"]
                
                t1_times.append(t1_time)
                t2_times.append(t2_time)
                readout_errors.append(readout_error)
                
                characteristics_dict[qubit_name] = {
                    "t1_time": t1_time,
                    "t2_time": t2_time,
                    "readout_error": readout_error
                }
        
        characteristics_dict["averages"] = {
            "avg_t1_time": sum(t1_times) / len(t1_times),
            "avg_t2_time": sum(t2_times) / len(t2_times),
            "avg_readout_error": sum(readout_errors) / len(readout_errors)
        }
        
        return characteristics_dict


    def get_gate_characteristics(self,backend, transpiled):
        qubit_urls = self.get_qubit_ids(backend, transpiled)
        qubit_gate_characteristics = {}
        all_gate_times = []
        all_gate_fidelities = []
        
        for qubit_url in qubit_urls:
                r = requests.get(qubit_url)
                r.raise_for_status()
                qubit_name = f"qubit {r.json()['name']}"
                
                qubit_gate_characteristics[qubit_name] = {}
                qubit_gate_times = []
                qubit_gate_fidelities = []
                
                used_gates = self.get_qubit_gates(transpiled, int(qubit_name.split(' ')[1]))
                gates = []
                for gate in used_gates:
                    gates.append(gate.split('[')[0])
                
                gates_url = f"{qubit_url}/gates"
                r = requests.get(gates_url)
                r.raise_for_status()
                available_gates = r.json()["_embedded"]["gateDtoes"]
                
                for gate in available_gates:
                    gate_name = gate["name"]
                    if gate_name in gates:
                        url = gates["_links"]["characteristics"]["href"]
                        r = requests.get(url)
                        r.raise_for_status()
                        characteristics = r.json()["_embedded"]["gateCharacteristicsDtoes"][0]
                        
                        gate_time = characteristics["gateTime"]
                        gate_fidelity = characteristics["gateFidelity"]
                        
                        qubit_gate_characteristics[qubit_name][gate_name] = {
                            "gateTime": gate_time,
                            "gateFidelity": gate_fidelity
                        }
                        
                        qubit_gate_times.append(gate_time)
                        qubit_gate_fidelities.append(gate_fidelity)
                        all_gate_times.append(gate_time)
                        all_gate_fidelities.append(gate_fidelity)
                
                # Add per-qubit averages
                if qubit_gate_times:  # Only add if the qubit has gates
                    qubit_gate_characteristics[qubit_name]["qubit_averages"] = {
                        "total_gate_time": sum(qubit_gate_times),
                        "avg_gate_fidelity": sum(qubit_gate_fidelities) / len(qubit_gate_fidelities)
                    }
        
        # Add overall averages
        if all_gate_times:  
            qubit_gate_characteristics["overall_averages"] = {
                "avg_gate_time": sum(all_gate_times) / len(all_gate_times),
                "avg_gate_fidelity": sum(all_gate_fidelities) / len(all_gate_fidelities)
            }
        
        return qubit_gate_characteristics

    def get_qpu_provenance(self,backend):
        qpu_url = self.get_qpu_url(backend)
        r = requests.get(qpu_url)
        r.raise_for_status()
        qpu_data = r.json()
        provenance_metrics = {
            "avgT1Time": qpu_data["avgT1Time"],
            "avgT2Time": qpu_data["avgT2Time"],
            "avgReadoutError": qpu_data["avgReadoutError"],
            "avgMultiQubitGateError": qpu_data["avgMultiQubitGateError"],
            "avgSingleQubitGateError": qpu_data["avgSingleQubitGateError"],
            "avgMultiQubitGateTime": qpu_data["avgMultiQubitGateTime"],
            "avgSingleQubitGateTime": qpu_data["avgSingleQubitGateTime"],
            "maxGateTime": qpu_data["maxGateTime"]
        }
        
        return provenance_metrics

    def get_calibration_matrix(self,backend):
        r = requests.get("http://localhost:5020/qprov/providers")
        r.raise_for_status()
        providers = r.json()["_embedded"]["providerDtoes"]
        for provider in providers:
         if provider["name"] == "ibmq":
            URL_for_qpu = provider["_links"]["qpus"]["href"]
            get_available_qpu = requests.get(URL_for_qpu)
            get_available_qpu.raise_for_status()
            available_qpu = get_available_qpu.json()["_embedded"]["qpuDtoes"]
            for qpu in available_qpu:
                if qpu["name"] == backend:
                    aggregated_url = qpu["_links"]["aggregated-data"]["href"]
                    r = requests.get(aggregated_url)
                    r.raise_for_status()
                    
                    calibration_url = r.json()["_links"]["calibration-matrix"]["href"]
                    r = requests.get(calibration_url)
                    r.raise_for_status()
                    
                    calibration_data = r.json()["_embedded"]["calibrationMatrixDtoes"][0]
                    return calibration_data["calibrationMatrix"]
                


class Execution_Annotation:
    def check_execution_annotations(self, qasm_string, counts):
        """Check QASM string for execution annotations and apply corresponding formatting"""
        results = counts

        if "@reverse_bitString" in qasm_string:
            results = self.reverse_bitString(results)
            
        if "@format_to_hex" in qasm_string:
            results = self.format_counts_hex(results)
            
        if "@format_to_decimal" in qasm_string:
            results = self.format_counts_decimal(results)
            
        return results

    def reverse_bitString(self, counts):
        reversed_counts = {}
        for bits, count in counts.items():
            reversed_bits = bits[::-1] 
            reversed_counts[reversed_bits] = count
        return reversed_counts
    
    def format_counts_hex(self, counts):
        hex_counts = {}
        for bitstring, count in counts.items():
            count_hex = hex(int(bitstring, 2))
            hex_counts[count_hex] = count
        return hex_counts

    def format_counts_decimal(self, counts):
        decimal_counts = {}
        for bitstring, count in counts.items():
            decimal = str(int(bitstring, 2))
            decimal_counts[decimal] = count
        return decimal_counts



class QPU_Selection:
    def check_qpu_annotations(self, qasm_string):
        """Check QASM string for QPU selection annotations and return selected QPU"""
        if "@select_qpu" not in qasm_string:
            return None
            
        # Find the line containing the select_qpu annotation
        for line in qasm_string.split('\n'):
            if '@select_qpu(' in line:
                args = line.split('select_qpu(')[1].split(')')[0].split(',')
                min_qubits = int(args[0].strip())
                metric = args[1].strip()
                
                # Get all QPUs data
                all_qpus = self.get_all_qpu()
                
                # Filter and select QPU
                return self.select_qpu(min_qubits, metric, all_qpus)
                
        return None

    def get_all_qpu(self):
        available_computer = []
        r = requests.get(f"{QPROV_URL}/providers")
        r.raise_for_status()
        providers = r.json()["_embedded"]["providerDtoes"]
        for provider in providers:
            provider_id = provider["id"]
            qpu_r = requests.get(f"{QPROV_URL}/providers/{provider_id}/qpus")
            qpu_r.raise_for_status()
            qpus = qpu_r.json()["_embedded"]["qpuDtoes"]
            for qpu in qpus:
                collect_info = {
                    'name': qpu['name'],
                    'num_qubits': qpu.get('numberOfQubits'),
                    'max_shots': qpu.get('maxShots'),
                    'queue_size': qpu.get('queueSize'),
                    'max_gateTime': qpu.get('maxGateTime'),
                    'avg_T1_time': qpu.get('avgT1Time'),
                    'avg_T2_time': qpu.get('avgT2Time'),
                    'avg_readout_error': qpu.get('avgReadoutError'),
                    'avg_multi_qubit_gate_error': qpu.get('avgMultiQubitGateError'),
                    'avg_single_qubit_gate_error': qpu.get('avgSingleQubitGateError'),
                    'avg_multi_qubit_gate_time': qpu.get('avgMultiQubitGateTime'),
                    'avg_single_qubit_gate_time': qpu.get('avgSingleQubitGateTime')
                }
                available_computer.append(collect_info)

        df = pd.DataFrame(available_computer)
        return df

    def select_qpu(self, min_qubits, metric, all_qpus):
        """Select best QPU based on minimum qubits and optimization metric"""
        filtered_df = all_qpus[all_qpus['num_qubits'] >= min_qubits]
        
        if filtered_df.empty:
            return "No QPUs found with the specified number of qubits"
        
        higher_better = ['avg_T1_time', 'avg_T2_time']
        
        if metric not in all_qpus.columns:
            return f"Unsupported metric: {metric}. Available metrics: {', '.join(all_qpus.columns)}"
        
        ascending = metric not in higher_better
        best_qpu = filtered_df.sort_values(metric, ascending=ascending).iloc[0]
        
        return best_qpu['name']
