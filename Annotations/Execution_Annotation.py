class Execution_Annotation:
    def check_execution_annotations(self, qasm_string, counts):
        """Check QASM string for execution annotations and apply corresponding formatting"""
        results = {}

        if "@reverse_bitString" in qasm_string:
            results['reverse_bitString'] = self.reverse_bitString(counts)
            
        if "@format_to_hex" in qasm_string:
            results['Hexadecimal representation'] = self.format_counts_hex(counts)
            
        if "@format_to_dec" in qasm_string:
            results['Decimal representation'] = self.format_counts_decimal(counts)
            
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
            bit_length = len(bitstring)
            decimal = str(int(bitstring, 2))
            formatted_value = f"[{decimal}]-{bit_length} bits"
            decimal_counts[formatted_value] = count
        return decimal_counts
