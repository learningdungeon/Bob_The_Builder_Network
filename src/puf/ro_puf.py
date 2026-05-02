"""
Ring Oscillator PUF Implementation

Simulates Ring Oscillator (RO) Physical Unclonable Function.
RO-PUFs exploit frequency variations in ring oscillators due to manufacturing
process variations to generate unique device fingerprints.
"""
# -*- coding: utf-8 -*-
import numpy as np
import hashlib
from typing import Tuple, Optional, List


class RingOscillatorPUF:
    """
    Ring Oscillator PUF simulator with configurable parameters.
    
    The RO-PUF uses pairs of ring oscillators and compares their frequencies.
    Manufacturing variations cause each oscillator to have a unique frequency,
    creating a device-specific fingerprint.
    
    Attributes:
        oscillator_pairs: Number of oscillator pairs
        response_bits: Number of bits in PUF response
        noise_level: Frequency measurement noise (0.0 to 1.0)
        frequency_range: Base frequency range in Hz
        device_id: Unique device identifier
    """
    
    def __init__(
        self,
        oscillator_pairs: int = 128,
        response_bits: int = 128,
        noise_level: float = 0.08,
        frequency_range: Tuple[float, float] = (100e6, 150e6),
        measurement_time: float = 1e-3,
        device_id: Optional[str] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize Ring Oscillator PUF with specified parameters.
        
        Args:
            oscillator_pairs: Number of oscillator pairs (default: 128)
            response_bits: Length of PUF response in bits (default: 128)
            noise_level: Frequency measurement noise (default: 0.08)
            frequency_range: (min_freq, max_freq) in Hz (default: 100-150 MHz)
            measurement_time: Measurement duration in seconds (default: 1ms)
            device_id: Unique device identifier (auto-generated if None)
            seed: Random seed for reproducibility (None for random)
        """
        self.oscillator_pairs = oscillator_pairs
        self.response_bits = response_bits
        self.noise_level = noise_level
        self.frequency_range = frequency_range
        self.measurement_time = measurement_time
        
        # Generate or use provided device ID
        if device_id is None:
            import secrets
            self.device_id = hashlib.sha256(
                secrets.token_bytes(16)
            ).hexdigest()[:16]
        else:
            self.device_id = device_id
        
        # Initialize RNG with device-specific seed
        device_seed = int(hashlib.sha256(self.device_id.encode()).hexdigest()[:8], 16)
        if seed is not None:
            device_seed = seed
        
        self.rng = np.random.RandomState(device_seed)
        
        # Generate base frequencies for all oscillators
        # Each oscillator has a unique frequency due to manufacturing variations
        num_oscillators = oscillator_pairs * 2
        mean_freq = np.mean(frequency_range)
        freq_std = (frequency_range[1] - frequency_range[0]) / 6  # 99.7% within range
        
        self.base_frequencies = self.rng.normal(
            mean_freq,
            freq_std,
            size=num_oscillators
        )
        
        # Clip to valid range
        self.base_frequencies = np.clip(
            self.base_frequencies,
            frequency_range[0],
            frequency_range[1]
        )
        
        # Create oscillator pairs for comparison
        self.oscillator_pairs_indices = [
            (2*i, 2*i+1) for i in range(oscillator_pairs)
        ]
        
        # Select pairs for response generation
        self.selected_pairs = self.rng.choice(
            oscillator_pairs,
            size=response_bits,
            replace=False
        )
    
    def _measure_frequency(
        self,
        oscillator_idx: int,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> float:
        """
        Measure frequency of a ring oscillator.
        
        Args:
            oscillator_idx: Index of oscillator to measure
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized, 1.0 = nominal)
            add_noise: Whether to add measurement noise
            
        Returns:
            Measured frequency in Hz
        """
        base_freq = self.base_frequencies[oscillator_idx]
        
        # Temperature coefficient: ~0.1% per degree C
        temp_factor = 1.0 - 0.001 * (temperature - 25.0)
        
        # Voltage coefficient: frequency proportional to voltage
        voltage_factor = voltage
        
        # Apply environmental factors
        freq = base_freq * temp_factor * voltage_factor
        
        # Add measurement noise
        if add_noise:
            noise_std = self.noise_level * base_freq
            noise = self.rng.normal(0, noise_std)
            freq += noise
        
        return freq
    
    def _compare_oscillators(
        self,
        pair_idx: int,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> int:
        """
        Compare frequencies of an oscillator pair.
        
        Args:
            pair_idx: Index of oscillator pair
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add measurement noise
            
        Returns:
            1 if first oscillator is faster, 0 otherwise
        """
        osc1_idx, osc2_idx = self.oscillator_pairs_indices[pair_idx]
        
        freq1 = self._measure_frequency(osc1_idx, temperature, voltage, add_noise)
        freq2 = self._measure_frequency(osc2_idx, temperature, voltage, add_noise)
        
        return 1 if freq1 > freq2 else 0
    
    def generate_response(
        self,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> np.ndarray:
        """
        Generate PUF response by comparing oscillator pairs.
        
        Args:
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized, 1.0 = nominal)
            add_noise: Whether to add measurement noise
            
        Returns:
            Binary array of length response_bits
        """
        response = np.array([
            self._compare_oscillators(pair_idx, temperature, voltage, add_noise)
            for pair_idx in self.selected_pairs
        ], dtype=np.uint8)
        
        return response
    
    def generate_response_bytes(
        self,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> bytes:
        """
        Generate PUF response as bytes.
        
        Args:
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add measurement noise
            
        Returns:
            PUF response as bytes
        """
        response = self.generate_response(temperature, voltage, add_noise)
        return np.packbits(response).tobytes()
    
    def get_stable_response(
        self,
        num_samples: int = 10,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> np.ndarray:
        """
        Generate stable response by majority voting over multiple samples.
        
        Args:
            num_samples: Number of samples to average
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Stable binary array
        """
        samples = np.array([
            self.generate_response(temperature, voltage, add_noise=True)
            for _ in range(num_samples)
        ])
        
        # Majority voting
        stable_response = (samples.sum(axis=0) > num_samples / 2).astype(np.uint8)
        
        return stable_response
    
    def measure_reliability(
        self,
        num_trials: int = 100,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> float:
        """
        Measure PUF reliability (reproducibility).
        
        Args:
            num_trials: Number of trials to run
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Reliability score (0.0 to 1.0)
        """
        reference = self.generate_response(temperature, voltage, add_noise=False)
        
        matches = 0
        for _ in range(num_trials):
            response = self.generate_response(temperature, voltage, add_noise=True)
            matches += np.sum(response == reference)
        
        reliability = matches / (num_trials * self.response_bits)
        return reliability
    
    def measure_uniqueness(
        self,
        other_pufs: List['RingOscillatorPUF'],
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> float:
        """
        Measure inter-device uniqueness (Hamming distance).
        
        Args:
            other_pufs: List of other RO PUF instances
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Average Hamming distance (0.0 to 1.0, ideal is 0.5)
        """
        self_response = self.generate_response(temperature, voltage, add_noise=False)
        
        hamming_distances = []
        for other_puf in other_pufs:
            other_response = other_puf.generate_response(temperature, voltage, add_noise=False)
            hamming_dist = np.sum(self_response != other_response) / self.response_bits
            hamming_distances.append(hamming_dist)
        
        return np.mean(hamming_distances)
    
    def get_entropy(self) -> float:
        """
        Estimate min-entropy of PUF responses.
        
        Returns:
            Estimated min-entropy in bits
        """
        # Generate multiple responses
        responses = np.array([
            self.generate_response(add_noise=False)
            for _ in range(1000)
        ])
        
        # Calculate bit probabilities
        bit_probs = responses.mean(axis=0)
        
        # Min-entropy: -log2(max(p, 1-p))
        min_entropy = -np.log2(np.maximum(bit_probs, 1 - bit_probs)).sum()
        
        return min_entropy
    
    def get_frequency_distribution(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get frequency distribution of all oscillators.
        
        Returns:
            Tuple of (frequencies, histogram)
        """
        return self.base_frequencies, np.histogram(self.base_frequencies, bins=50)
    
    def __repr__(self) -> str:
        return (
            f"RingOscillatorPUF(device_id={self.device_id}, "
            f"pairs={self.oscillator_pairs}, "
            f"response_bits={self.response_bits}, "
            f"noise={self.noise_level:.2%}, "
            f"freq_range={self.frequency_range[0]/1e6:.0f}-{self.frequency_range[1]/1e6:.0f}MHz)"
        )


if __name__ == "__main__":
    # Demo usage
    print("=" * 70)
    print("Ring Oscillator PUF Demonstration")
    print("=" * 70)
    
    # Create RO PUF instance
    puf = RingOscillatorPUF(
        oscillator_pairs=128,
        response_bits=128,
        noise_level=0.08,
        frequency_range=(100e6, 150e6),
        device_id="device_001"
    )
    
    print(f"\n{puf}")
    
    # Generate responses
    print("\nGenerating PUF responses...")
    response1 = puf.generate_response()
    response2 = puf.generate_response()
    
    print(f"Response 1: {response1[:32]}... ({len(response1)} bits)")
    print(f"Response 2: {response2[:32]}... ({len(response2)} bits)")
    
    # Measure reliability
    print("\nMeasuring reliability...")
    reliability = puf.measure_reliability(num_trials=100)
    print(f"Reliability: {reliability:.2%}")
    
    # Measure entropy
    entropy = puf.get_entropy()
    print(f"Min-entropy: {entropy:.2f} bits")
    
    # Test with different environmental conditions
    print("\nTesting environmental sensitivity...")
    temp_responses = []
    temperatures = [0, 25, 50, 75]
    for temp in temperatures:
        resp = puf.generate_response(temperature=temp, add_noise=False)
        temp_responses.append(resp)
        print(f"  Temperature {temp}�C: {resp[:16]}...")
    
    # Test uniqueness with other devices
    print("\nTesting uniqueness with other devices...")
    other_pufs = [
        RingOscillatorPUF(device_id=f"device_{i:03d}")
        for i in range(2, 11)
    ]
    uniqueness = puf.measure_uniqueness(other_pufs)
    print(f"Average Hamming distance: {uniqueness:.2%} (ideal: 50%)")
    
    # Frequency distribution
    print("\nOscillator frequency statistics:")
    freqs = puf.base_frequencies
    print(f"  Mean: {freqs.mean()/1e6:.2f} MHz")
    print(f"  Std Dev: {freqs.std()/1e6:.2f} MHz")
    print(f"  Min: {freqs.min()/1e6:.2f} MHz")
    print(f"  Max: {freqs.max()/1e6:.2f} MHz")
    
    print("\n" + "=" * 70)
