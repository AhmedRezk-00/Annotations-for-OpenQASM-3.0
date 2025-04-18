import requests
import pandas as pd
QPROV_URL = "http://localhost:5020/qprov" 
class QPU_Selection:


    # checking for annotation in th OpenQASM circuit.
    def check_qpu_annotations(self, qasm_string):
        for line in qasm_string.split('\n'):
            if '@select_qpu(' in line:
                first_split = line.split('@select_qpu(')
                comma_split = first_split[1].split(',')
                min_qubits = int(comma_split[0].strip())
                metric = comma_split[1].strip(')').strip()
                
                all_qpus = self.get_all_qpu()
                return self.select_qpu(min_qubits, metric, all_qpus)
                
    


    # getting all quantum computer from IBM only.
    def get_all_qpu(self):
        available_computer = []
        r = requests.get(f"{QPROV_URL}/providers")
        r.raise_for_status()
        providers = r.json()["_embedded"]["providerDtoes"]
        for provider in providers:
          if provider.get("name") =="ibmq": 
            provider_id = provider["id"]
            break
        qpu_r = requests.get(f"{QPROV_URL}/providers/{provider_id}/qpus")
        qpu_r.raise_for_status()
        qpus = qpu_r.json()["_embedded"]["qpuDtoes"]
        for qpu in qpus:
            collect_info = {
                'name': qpu['name'],
                'num_qubits': qpu.get('numberOfQubits'),
                'max_shots': qpu.get('maxShots'),
                'queue_size': qpu.get('queueSize'),
                'max_gate_time': qpu.get('maxGateTime'),
                't1_time': qpu.get('avgT1Time'),
                't2_time': qpu.get('avgT2Time'),
                'readout_error': qpu.get('avgReadoutError'),
                'multi_qubit_gate_error': qpu.get('avgMultiQubitGateError'),
                'single_qubit_gate_error': qpu.get('avgSingleQubitGateError'),
                'average_multi_qubit_gate_time': qpu.get('avgMultiQubitGateTime'),
                'average_single_qubit_gate_time': qpu.get('avgSingleQubitGateTime')
            }
            available_computer.append(collect_info)

        df = pd.DataFrame(available_computer)
        return df
    #filter operation based on number of qubits and user specified metric
    def select_qpu(self, min_qubits, metric, all_qpus):
        filtered_df = all_qpus[all_qpus['num_qubits'] >= min_qubits]
        if filtered_df.empty:
            return "No QPUs found with the specified number of qubits"
        if metric not in all_qpus.columns:
            return f"Unsupported metric: {metric}. Available metrics: {', '.join(all_qpus.columns)}"
        if metric == 't1_time' or metric == 't2_time':
            best_qpu = filtered_df.sort_values(metric, ascending=False).iloc[0]
        else:
            best_qpu = filtered_df.sort_values(metric, ascending=True).iloc[0]

        return best_qpu['name']
