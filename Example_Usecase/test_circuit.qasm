OPENQASM 3.0;
include "stdgates.inc";

@select_qpu(15,readout_error)
@get_qpu

qubit[15] q; 
bit[15] c; 
@get_qubit_characteristics
h q[0]; 
cx q[0], q[1]; 
cx q[1], q[2]; 
cx q[2], q[3];
cx q[3], q[4];
x q[5]; 
h q[6]; 
cx q[6], q[7]; 
x q[8];
h q[9];
cx q[9], q[10];
h q[11];
x q[12];
cx q[12], q[13];
h q[14];
@get_gate_characteristics
@reverse_bitString
@format_to_hex
@format_to_dec
c = measure q; 