"""
SRAM PUF Implementation

Simulates SRAM (Static Random Access Memory) Physical Unclonable Function.
SRAM cells have random power-up states due to manufacturing variations,
providing a unique device fingerprint.
"""

import numpy as np
import hashlib
from typing import Tuple, Optional


class SRAMPUF:
    """
    SRAM PUF simulator with configurable parameters.
    
    The SRAM PUF exploits the random power-up state of SRAM cells to generate
    a unique device fingerprint. Each cell has a slight bias toward 0 or 1 due
    to manufacturing process variations.
    
    Attributes:
        cell_count: Number of SRAM cells
        response_bits: Number of bits in PUF response
        noise_level: Bit error rate (0.0 to 1.0)
        temperature_sensitivity: Temperature-dependent noise
        device_id: Unique device identifier
    """
    
    def __init__(
        self,
        cell_count: int = 2048,
        response_bits: int = 256,
        noise_level: float = 0.15,
        temperature_sensitivity: float = 0.02,
        device_id: Optional[str] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize SRAM PUF with specified parameters.
        
        Args:
            cell_count: Number of SRAM cells (default: 2048)
            response_bits: Length of PUF response in bits (default: 256)
            noise_level: Base bit error rate (default: 0.15)
            temperature_sensitivity: Additional noise from temperature (default: 0.02)
            device_id: Unique device identifier (auto-generated if None)
            seed: Random seed for reproducibility (None for random)
        """
        self.cell_count = cell_count
        self.response_bits = response_bits
        self.noise_level = noise_level
        self.temperature_sensitivity = temperature_sensitivity
        
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
        
        # Generate cell biases (manufacturing variations)
        # Each cell has a bias between -1 and 1 (negative = prefer 0, positive = prefer 1)
        self.cell_biases = self.rng.uniform(-1, 1, size=cell_count)
        
        # Select cells for response generation
        self.selected_cells = self.rng.choice(
            cell_count, 
            size=response_bits, 
            replace=False
        )
    
    def _simulate_power_up(self, temperature: float = 25.0) -> np.ndarray:
        """
        Simulate SRAM power-up behavior.
        
        Args:
            temperature: Operating temperature in Celsius (default: 25.0)
            
        Returns:
            Array of power-up states (0 or 1) for all cells
        """
        # Temperature affects noise level
        temp_noise = self.temperature_sensitivity * abs(temperature - 25.0) / 25.0
        total_noise = self.noise_level + temp_noise
        
        # Generate power-up states based on cell biases and noise
        noise = self.rng.normal(0, total_noise, size=self.cell_count)
        states = (self.cell_biases + noise) > 0
        
        return states.astype(np.uint8)
    
    def generate_response(
        self, 
        temperature: float = 25.0,
        add_noise: bool = True
    ) -> np.ndarray:
        """
        Generate PUF response by simulating SRAM power-up.
        
        Args:
            temperature: Operating temperature in Celsius
            add_noise: Whether to add environmental noise
            
        Returns:
            Binary array of length response_bits
        """
        # Simulate power-up
        cell_states = self._simulate_power_up(temperature)
        
        # Extract response from selected cells
        response = cell_states[self.selected_cells]
        
        # Add additional environmental noise if requested
        if add_noise:
            flip_mask = self.rng.random(self.response_bits) < self.noise_level
            response = response ^ flip_mask.astype(np.uint8)
        
        return response
    
    def generate_response_bytes(
        self,
        temperature: float = 25.0,
        add_noise: bool = True
    ) -> bytes:
        """
        Generate PUF response as bytes.
        
        Args:
            temperature: Operating temperature in Celsius
            add_noise: Whether to add environmental noise
            
        Returns:
            PUF response as bytes
        """
        response = self.generate_response(temperature, add_noise)
        # Pack bits into bytes
        return np.packbits(response).tobytes()
    
    def get_stable_response(
        self,
        num_samples: int = 10,
        temperature: float = 25.0
    ) -> np.ndarray:
        """
        Generate stable response by majority voting over multiple samples.
        
        Args:
            num_samples: Number of samples to average
            temperature: Operating temperature in Celsius
            
        Returns:
            Stable binary array
        """
        samples = np.array([
            self.generate_response(temperature, add_noise=True)
            for _ in range(num_samples)
        ])
        
        # Majority voting
        stable_response = (samples.sum(axis=0) > num_samples / 2).astype(np.uint8)
        
        return stable_response
    
    def measure_reliability(
        self,
        num_trials: int = 100,
        temperature: float = 25.0
    ) -> float:
        """
        Measure PUF reliability (reproducibility).
        
        Args:
            num_trials: Number of trials to run
            temperature: Operating temperature in Celsius
            
        Returns:
            Reliability score (0.0 to 1.0)
        """
        reference = self.generate_response(temperature, add_noise=False)
        
        matches = 0
        for _ in range(num_trials):
            response = self.generate_response(temperature, add_noise=True)
            matches += np.sum(response == reference)
        
        reliability = matches / (num_trials * self.response_bits)
        return reliability
    
    def measure_uniqueness(
        self,
        other_pufs: list,
        temperature: float = 25.0
    ) -> float:
        """
        Measure inter-device uniqueness (Hamming distance).
        
        Args:
            other_pufs: List of other SRAM PUF instances
            temperature: Operating temperature in Celsius
            
        Returns:
            Average Hamming distance (0.0 to 1.0, ideal is 0.5)
        """
        self_response = self.generate_response(temperature, add_noise=False)
        
        hamming_distances = []
        for other_puf in other_pufs:
            other_response = other_puf.generate_response(temperature, add_noise=False)
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
    
    def __repr__(self) -> str:
        return (
            f"SRAMPUF(device_id={self.device_id}, "
            f"cells={self.cell_count}, "
            f"response_bits={self.response_bits}, "
            f"noise={self.noise_level:.2%})"
        )


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("SRAM PUF Demonstration")
    print("=" * 60)
    
    # Create SRAM PUF instance
    puf = SRAMPUF(
        cell_count=2048,
        response_bits=256,
        noise_level=0.15,
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
    reliability = puf.measure_reliability(num_trials=100)
    print(f"\nReliability: {reliability:.2%}")
    
    # Measure entropy
    entropy = puf.get_entropy()
    print(f"Min-entropy: {entropy:.2f} bits")
    
    # Test uniqueness with other devices
    print("\nTesting uniqueness with other devices...")
    other_pufs = [
        SRAMPUF(device_id=f"device_{i:03d}") 
        for i in range(2, 11)
    ]
    uniqueness = puf.measure_uniqueness(other_pufs)
    print(f"Average Hamming distance: {uniqueness:.2%} (ideal: 50%)")
    
    print("\n" + "=" * 60)
