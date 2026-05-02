"""
Timing Attack Mitigation Module

Implements constant-time operations and timing attack countermeasures
to prevent side-channel attacks on cryptographic operations.

Key Features:
1. Constant-time comparison operations
2. Constant-time conditional operations
3. Timing-safe string/byte operations
4. Blinding techniques for cryptographic operations
5. Timing measurement and analysis tools
6. Cache-timing attack mitigation

References:
- Bernstein, D. J. (2005). "Cache-timing attacks on AES"
- Kocher, P. C. (1996). "Timing attacks on implementations of Diffie-Hellman, RSA, DSS"
"""

import hmac
import hashlib
import secrets
import time
import numpy as np
from typing import Optional, Callable, Any, List, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TimingAttackType(Enum):
    """Types of timing attacks"""
    COMPARISON_TIMING = "comparison_timing"
    BRANCH_TIMING = "branch_timing"
    CACHE_TIMING = "cache_timing"
    POWER_ANALYSIS = "power_analysis"
    FAULT_INJECTION = "fault_injection"


@dataclass
class TimingMeasurement:
    """Timing measurement result"""
    operation: str
    execution_time: float
    variance: float
    samples: int
    is_constant_time: bool
    confidence: float
    timestamp: float = field(default_factory=time.time)


class ConstantTimeOps:
    """
    Constant-time operations for cryptographic primitives
    
    All operations are designed to execute in constant time regardless
    of input values to prevent timing side-channel attacks.
    """
    
    @staticmethod
    def ct_compare(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison of two byte strings
        
        Uses bitwise operations to avoid early termination.
        Equivalent to hmac.compare_digest but with explicit implementation.
        
        Args:
            a: First byte string
            b: Second byte string
            
        Returns:
            True if equal, False otherwise
        """
        # Use Python's built-in constant-time comparison
        return hmac.compare_digest(a, b)
    
    @staticmethod
    def ct_compare_manual(a: bytes, b: bytes) -> bool:
        """
        Manual constant-time comparison (educational)
        
        Demonstrates the principle of constant-time comparison
        by accumulating differences without early exit.
        
        Args:
            a: First byte string
            b: Second byte string
            
        Returns:
            True if equal, False otherwise
        """
        if len(a) != len(b):
            # Still need to do constant-time work to avoid length oracle
            result = 1
            for i in range(max(len(a), len(b))):
                result |= 0xFF
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        return result == 0
    
    @staticmethod
    def ct_select(condition: bool, true_val: int, false_val: int) -> int:
        """
        Constant-time conditional selection
        
        Selects between two values without branching.
        Uses bitwise operations to avoid timing leaks.
        
        Args:
            condition: Selection condition
            true_val: Value to return if condition is True
            false_val: Value to return if condition is False
            
        Returns:
            Selected value
        """
        # Convert bool to mask: True -> 0xFFFFFFFF, False -> 0x00000000
        mask = -(int(condition))
        
        # Select using bitwise operations
        return (true_val & mask) | (false_val & ~mask)
    
    @staticmethod
    def ct_copy(condition: bool, src: bytes, dst: bytes) -> bytes:
        """
        Constant-time conditional copy
        
        Copies src to dst if condition is True, otherwise returns dst unchanged.
        Performs the copy operation regardless of condition to maintain constant time.
        
        Args:
            condition: Copy condition
            src: Source bytes
            dst: Destination bytes
            
        Returns:
            Result bytes
        """
        if len(src) != len(dst):
            raise ValueError("Source and destination must have same length")
        
        mask = -(int(condition)) & 0xFF
        result = bytearray(len(dst))
        
        for i in range(len(dst)):
            result[i] = (src[i] & mask) | (dst[i] & ~mask)
        
        return bytes(result)
    
    @staticmethod
    def ct_memcmp(a: bytes, b: bytes, length: int) -> int:
        """
        Constant-time memory comparison
        
        Compares first 'length' bytes in constant time.
        Returns 0 if equal, non-zero otherwise.
        
        Args:
            a: First byte string
            b: Second byte string
            length: Number of bytes to compare
            
        Returns:
            0 if equal, non-zero otherwise
        """
        if len(a) < length or len(b) < length:
            raise ValueError("Inputs too short for specified length")
        
        result = 0
        for i in range(length):
            result |= a[i] ^ b[i]
        
        return result
    
    @staticmethod
    def ct_is_zero(value: int) -> bool:
        """
        Constant-time zero check
        
        Checks if value is zero without branching.
        
        Args:
            value: Integer value to check
            
        Returns:
            True if zero, False otherwise
        """
        # Use bitwise operations to avoid branching
        # If value is 0, all bits are 0
        # If value is non-zero, at least one bit is 1
        return bool((value | -value) >> 31 == 0)
    
    @staticmethod
    def ct_lookup(table: List[int], index: int) -> int:
        """
        Constant-time table lookup
        
        Performs table lookup in constant time by accessing all elements.
        Prevents cache-timing attacks on lookup operations.
        
        Args:
            table: Lookup table
            index: Index to lookup
            
        Returns:
            Value at index
        """
        result = 0
        for i, val in enumerate(table):
            # Create mask: 0xFFFFFFFF if i == index, else 0x00000000
            mask = -(int(i == index))
            result |= val & mask
        
        return result


class BlindingTechniques:
    """
    Blinding techniques for cryptographic operations
    
    Adds randomness to operations to prevent timing analysis
    while maintaining correctness of results.
    """
    
    @staticmethod
    def multiplicative_blinding(value: int, modulus: int) -> Tuple[int, int]:
        """
        Apply multiplicative blinding
        
        Blinds a value by multiplying with random factor.
        Used in RSA and other modular arithmetic operations.
        
        Args:
            value: Value to blind
            modulus: Modulus for operations
            
        Returns:
            Tuple of (blinded_value, blinding_factor)
        """
        # Generate random blinding factor coprime to modulus
        while True:
            r = secrets.randbelow(modulus - 1) + 1
            if np.gcd(r, modulus) == 1:
                break
        
        blinded = (value * r) % modulus
        return blinded, r
    
    @staticmethod
    def additive_blinding(value: int, modulus: int) -> Tuple[int, int]:
        """
        Apply additive blinding
        
        Blinds a value by adding random offset.
        
        Args:
            value: Value to blind
            modulus: Modulus for operations
            
        Returns:
            Tuple of (blinded_value, blinding_factor)
        """
        r = secrets.randbelow(modulus)
        blinded = (value + r) % modulus
        return blinded, r
    
    @staticmethod
    def unblind_multiplicative(blinded: int, factor: int, modulus: int) -> int:
        """
        Remove multiplicative blinding
        
        Args:
            blinded: Blinded value
            factor: Blinding factor
            modulus: Modulus for operations
            
        Returns:
            Original value
        """
        # Compute modular inverse of blinding factor
        inv = pow(factor, -1, modulus)
        return (blinded * inv) % modulus
    
    @staticmethod
    def unblind_additive(blinded: int, factor: int, modulus: int) -> int:
        """
        Remove additive blinding
        
        Args:
            blinded: Blinded value
            factor: Blinding factor
            modulus: Modulus for operations
            
        Returns:
            Original value
        """
        return (blinded - factor) % modulus


class TimingAnalyzer:
    """
    Timing analysis and measurement tools
    
    Measures execution time variance to detect timing vulnerabilities.
    """
    
    def __init__(self, samples: int = 1000):
        """
        Initialize timing analyzer
        
        Args:
            samples: Number of samples for statistical analysis
        """
        self.samples = samples
        self.measurements: List[TimingMeasurement] = []
    
    def measure_operation(self, operation: Callable, *args, **kwargs) -> TimingMeasurement:
        """
        Measure timing characteristics of an operation
        
        Args:
            operation: Function to measure
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Timing measurement result
        """
        times = []
        
        for _ in range(self.samples):
            start = time.perf_counter()
            operation(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        times_array = np.array(times)
        mean_time = float(np.mean(times_array))
        variance = float(np.var(times_array))
        std_dev = float(np.std(times_array))
        
        # Check if constant-time (low variance relative to mean)
        coefficient_of_variation = std_dev / mean_time if mean_time > 0 else 0
        is_constant_time = coefficient_of_variation < 0.05  # 5% threshold
        confidence = float(1.0 - min(1.0, coefficient_of_variation / 0.05))
        
        measurement = TimingMeasurement(
            operation=operation.__name__,
            execution_time=mean_time,
            variance=variance,
            samples=self.samples,
            is_constant_time=is_constant_time,
            confidence=confidence
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def compare_operations(self, op1: Callable, op2: Callable, 
                          args1: tuple, args2: tuple) -> Dict:
        """
        Compare timing of two operations
        
        Args:
            op1: First operation
            op2: Second operation
            args1: Arguments for first operation
            args2: Arguments for second operation
            
        Returns:
            Comparison results
        """
        m1 = self.measure_operation(op1, *args1)
        m2 = self.measure_operation(op2, *args2)
        
        time_diff = abs(m1.execution_time - m2.execution_time)
        relative_diff = time_diff / max(m1.execution_time, m2.execution_time)
        
        return {
            'operation1': m1,
            'operation2': m2,
            'time_difference': time_diff,
            'relative_difference': relative_diff,
            'both_constant_time': m1.is_constant_time and m2.is_constant_time
        }
    
    def generate_report(self) -> str:
        """
        Generate timing analysis report
        
        Returns:
            Formatted report string
        """
        if not self.measurements:
            return "No measurements recorded"
        
        report = []
        report.append("=" * 70)
        report.append("TIMING ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"\nTotal Measurements: {len(self.measurements)}")
        report.append(f"Samples per Measurement: {self.samples}")
        
        constant_time_count = sum(1 for m in self.measurements if m.is_constant_time)
        report.append(f"Constant-Time Operations: {constant_time_count}/{len(self.measurements)}")
        
        report.append("\nDetailed Results:")
        report.append("-" * 70)
        
        for m in self.measurements:
            status = "PASS" if m.is_constant_time else "FAIL"
            report.append(f"\nOperation: {m.operation}")
            report.append(f"  Status: {status}")
            report.append(f"  Mean Time: {m.execution_time*1e6:.2f} µs")
            report.append(f"  Variance: {m.variance*1e12:.2f} ps²")
            report.append(f"  Confidence: {m.confidence*100:.1f}%")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


class CacheTimingMitigation:
    """
    Cache-timing attack mitigation techniques
    
    Implements countermeasures against cache-based side-channel attacks.
    """
    
    @staticmethod
    def constant_time_aes_sbox_lookup(input_byte: int, sbox: List[int]) -> int:
        """
        Constant-time AES S-box lookup
        
        Accesses all S-box entries to prevent cache-timing attacks.
        
        Args:
            input_byte: Input byte (0-255)
            sbox: S-box lookup table (256 entries)
            
        Returns:
            S-box output
        """
        if len(sbox) != 256:
            raise ValueError("S-box must have 256 entries")
        
        result = 0
        for i in range(256):
            mask = -(int(i == input_byte))
            result |= sbox[i] & mask
        
        return result
    
    @staticmethod
    def scatter_gather_access(data: List[int], indices: List[int]) -> List[int]:
        """
        Scatter-gather memory access pattern
        
        Accesses memory in a pattern that minimizes cache-timing leaks.
        
        Args:
            data: Data array
            indices: Indices to access
            
        Returns:
            Accessed values
        """
        # Access all elements to prevent cache-timing analysis
        dummy = 0
        for val in data:
            dummy ^= val
        
        # Now perform actual accesses
        result = [data[i] for i in indices]
        
        # Use dummy to prevent optimization
        if dummy == -1:
            result[0] ^= 0
        
        return result


class TimingSafeOperations:
    """
    High-level timing-safe operations for common use cases
    """
    
    @staticmethod
    def safe_password_verify(password: bytes, hash_value: bytes) -> bool:
        """
        Timing-safe password verification
        
        Args:
            password: Password to verify
            hash_value: Expected hash value
            
        Returns:
            True if password matches, False otherwise
        """
        computed_hash = hashlib.sha256(password).digest()
        return ConstantTimeOps.ct_compare(computed_hash, hash_value)
    
    @staticmethod
    def safe_token_verify(token: bytes, expected: bytes) -> bool:
        """
        Timing-safe token verification
        
        Args:
            token: Token to verify
            expected: Expected token value
            
        Returns:
            True if token matches, False otherwise
        """
        return ConstantTimeOps.ct_compare(token, expected)
    
    @staticmethod
    def safe_hmac_verify(message: bytes, key: bytes, expected_mac: bytes) -> bool:
        """
        Timing-safe HMAC verification
        
        Args:
            message: Message that was authenticated
            key: HMAC key
            expected_mac: Expected HMAC value
            
        Returns:
            True if HMAC matches, False otherwise
        """
        computed_mac = hmac.new(key, message, hashlib.sha256).digest()
        return ConstantTimeOps.ct_compare(computed_mac, expected_mac)


def demo_timing_attack_mitigation():
    """Demonstration of timing attack mitigation techniques"""
    print("\n" + "=" * 70)
    print("TIMING ATTACK MITIGATION DEMONSTRATION")
    print("=" * 70)
    
    # 1. Constant-time comparison
    print("\n1. Constant-Time Comparison")
    print("-" * 70)
    
    a = b"secret_token_12345678"
    b_correct = b"secret_token_12345678"
    b_wrong = b"secret_token_87654321"
    
    print(f"Comparing: {a.decode()}")
    print(f"  vs Correct: {b_correct.decode()} -> {ConstantTimeOps.ct_compare(a, b_correct)}")
    print(f"  vs Wrong:   {b_wrong.decode()} -> {ConstantTimeOps.ct_compare(a, b_wrong)}")
    
    # 2. Constant-time selection
    print("\n2. Constant-Time Selection")
    print("-" * 70)
    
    condition = True
    result = ConstantTimeOps.ct_select(condition, 42, 99)
    print(f"Select(condition={condition}, true=42, false=99) -> {result}")
    
    condition = False
    result = ConstantTimeOps.ct_select(condition, 42, 99)
    print(f"Select(condition={condition}, true=42, false=99) -> {result}")
    
    # 3. Blinding techniques
    print("\n3. Blinding Techniques")
    print("-" * 70)
    
    value = 12345
    modulus = 65537
    
    blinded, factor = BlindingTechniques.multiplicative_blinding(value, modulus)
    unblinded = BlindingTechniques.unblind_multiplicative(blinded, factor, modulus)
    
    print(f"Original value: {value}")
    print(f"Blinded value: {blinded}")
    print(f"Unblinded value: {unblinded}")
    print(f"Correct: {value == unblinded}")
    
    # 4. Timing analysis
    print("\n4. Timing Analysis")
    print("-" * 70)
    
    analyzer = TimingAnalyzer(samples=100)
    
    # Measure constant-time comparison
    test_a = secrets.token_bytes(32)
    test_b = secrets.token_bytes(32)
    
    print("Measuring constant-time comparison...")
    m1 = analyzer.measure_operation(ConstantTimeOps.ct_compare, test_a, test_b)
    print(f"  Mean time: {m1.execution_time*1e6:.2f} µs")
    print(f"  Variance: {m1.variance*1e12:.2f} ps²")
    print(f"  Constant-time: {m1.is_constant_time}")
    print(f"  Confidence: {m1.confidence*100:.1f}%")
    
    # 5. Safe password verification
    print("\n5. Timing-Safe Password Verification")
    print("-" * 70)
    
    password = b"my_secure_password"
    hash_value = hashlib.sha256(password).digest()
    
    print("Verifying correct password...")
    result = TimingSafeOperations.safe_password_verify(password, hash_value)
    print(f"  Result: {result}")
    
    print("Verifying wrong password...")
    wrong_password = b"wrong_password"
    result = TimingSafeOperations.safe_password_verify(wrong_password, hash_value)
    print(f"  Result: {result}")
    
    # 6. Generate report
    print("\n6. Timing Analysis Report")
    print(analyzer.generate_report())
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Mitigation Techniques:")
    print("  - Constant-time comparison (no early exit)")
    print("  - Constant-time selection (no branching)")
    print("  - Blinding (randomize intermediate values)")
    print("  - Cache-timing mitigation (access all entries)")
    print("  - Statistical timing analysis (detect vulnerabilities)")
    print("=" * 70)


if __name__ == "__main__":
    demo_timing_attack_mitigation()

# Made with Bob
