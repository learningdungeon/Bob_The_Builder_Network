"""
Arbiter PUF Implementation

Simulates Arbiter Physical Unclonable Function with delay chain.
Arbiter PUFs exploit race conditions in symmetric delay chains to generate
unique device responses based on manufacturing variations.
"""
# -*- coding: utf-8 -*-
import numpy as np
import hashlib
from typing import Optional, List


class ArbiterPUF:
    """
    Arbiter PUF simulator with delay chain modeling.
    
    The Arbiter PUF uses two parallel delay chains with a race condition.
    Manufacturing variations cause slight delay differences in each stage,
    and an arbiter determines which signal arrives first.
    
    Attributes:
        delay_stages: Number of stages in delay chain
        response_bits: Number of bits in PUF response  
        noise_level: Delay measurement noise (0.0 to 1.0)
        delay_variation: Standard deviation of delay per stage (seconds)
        device_id: Unique device identifier
    """
    
    def __init__(
        self,
        delay_stages: int = 64,
        response_bits: int = 64,
        noise_level: float = 0.11,
        delay_variation: float = 1e-12,  # 1 picosecond
        base_delay: float = 10e-12,  # 10 picoseconds per stage
        device_id: Optional[str] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize Arbiter PUF with specified parameters.
        
        Args:
            delay_stages: Number of stages in delay chain (default: 64)
            response_bits: Length of PUF response in bits (default: 64)
            noise_level: Delay measurement noise (default: 0.11)
            delay_variation: Std dev of delay per stage in seconds (default: 1ps)
            base_delay: Base delay per stage in seconds (default: 10ps)
            device_id: Unique device identifier (auto-generated if None)
            seed: Random seed for reproducibility (None for random)
        """
        self.delay_stages = delay_stages
        self.response_bits = response_bits
        self.noise_level = noise_level
        self.delay_variation = delay_variation
        self.base_delay = base_delay
        
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
        
        # Generate delay differences for each stage
        # Positive = upper path faster, Negative = lower path faster
        self.stage_delays = self.rng.normal(
            0,
            delay_variation,
            size=delay_stages
        )
        
        # Pre-generate challenge-response pairs for efficiency
        self._challenge_cache = {}
    
    def _apply_challenge(self, challenge: np.ndarray) -> np.ndarray:
        """
        Apply challenge to delay chain configuration.
        
        Challenge bits determine whether delay elements are crossed or straight.
        0 = straight, 1 = crossed
        
        Args:
            challenge: Binary array of length delay_stages
            
        Returns:
            Effective delay differences after challenge application
        """
        # When crossed (challenge bit = 1), delay difference is inverted
        effective_delays = np.where(
            challenge == 1,
            -self.stage_delays,
            self.stage_delays
        )
        
        return effective_delays
    
    def _simulate_race(
        self,
        challenge: np.ndarray,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> int:
        """
        Simulate race condition in delay chains.
        
        Args:
            challenge: Binary challenge array
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized, 1.0 = nominal)
            add_noise: Whether to add measurement noise
            
        Returns:
            1 if upper path wins, 0 if lower path wins
        """
        # Apply challenge to get effective delays
        effective_delays = self._apply_challenge(challenge)
        
        # Temperature effect: delays increase with temperature (~0.2% per �C)
        temp_factor = 1.0 + 0.002 * (temperature - 25.0)
        
        # Voltage effect: delays decrease with higher voltage
        voltage_factor = 2.0 - voltage  # Inverse relationship
        
        # Calculate total delay difference
        total_delay_diff = np.sum(effective_delays) * temp_factor * voltage_factor
        
        # Add measurement noise
        if add_noise:
            noise_std = self.noise_level * self.base_delay * self.delay_stages
            noise = self.rng.normal(0, noise_std)
            total_delay_diff += noise
        
        # Arbiter decision: positive delay = upper path wins (output 1)
        return 1 if total_delay_diff > 0 else 0
    
    def _challenge_to_array(self, challenge: int) -> np.ndarray:
        """
        Convert integer challenge to binary array.
        
        Args:
            challenge: Integer challenge value
            
        Returns:
            Binary array of length delay_stages
        """
        # Convert to binary and pad to delay_stages length
        binary_str = format(challenge, f'0{self.delay_stages}b')
        return np.array([int(b) for b in binary_str], dtype=np.uint8)
    
    def generate_response(
        self,
        challenge: Optional[int] = None,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> int:
        """
        Generate single-bit PUF response for a challenge.
        
        Args:
            challenge: Integer challenge (0 to 2^delay_stages - 1)
                      If None, generates random challenge
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add measurement noise
            
        Returns:
            Single bit response (0 or 1)
        """
        if challenge is None:
            # Use modulo to keep within int32 range
            challenge = self.rng.randint(0, min(2**self.delay_stages, 2**31-1))
        
        challenge_array = self._challenge_to_array(challenge)
        return self._simulate_race(challenge_array, temperature, voltage, add_noise)
    
    def generate_response_vector(
        self,
        challenges: Optional[List[int]] = None,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> np.ndarray:
        """
        Generate multi-bit PUF response for multiple challenges.
        
        Args:
            challenges: List of integer challenges
                       If None, generates random challenges
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add measurement noise
            
        Returns:
            Binary array of responses
        """
        if challenges is None:
            # Generate random challenges (keep within int32 range)
            max_challenge = min(2**self.delay_stages, 2**31-1)
            challenges = self.rng.randint(
                0,
                max_challenge,
                size=self.response_bits
            )
        
        responses = np.array([
            self.generate_response(c, temperature, voltage, add_noise)
            for c in challenges
        ], dtype=np.uint8)
        
        return responses
    
    def generate_response_bytes(
        self,
        challenges: Optional[List[int]] = None,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> bytes:
        """
        Generate PUF response as bytes.
        
        Args:
            challenges: List of integer challenges
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add measurement noise
            
        Returns:
            PUF response as bytes
        """
        response = self.generate_response_vector(challenges, temperature, voltage, add_noise)
        return np.packbits(response).tobytes()
    
    def get_stable_response(
        self,
        challenges: Optional[List[int]] = None,
        num_samples: int = 10,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> np.ndarray:
        """
        Generate stable response by majority voting over multiple samples.
        
        Args:
            challenges: List of integer challenges
            num_samples: Number of samples to average
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Stable binary array
        """
        if challenges is None:
            max_challenge = min(2**self.delay_stages, 2**31-1)
            challenges = self.rng.randint(
                0,
                max_challenge,
                size=self.response_bits
            )
        
        samples = np.array([
            self.generate_response_vector(challenges, temperature, voltage, add_noise=True)
            for _ in range(num_samples)
        ])
        
        # Majority voting
        stable_response = (samples.sum(axis=0) > num_samples / 2).astype(np.uint8)
        
        return stable_response
    
    def measure_reliability(
        self,
        num_trials: int = 100,
        num_challenges: int = 64,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> float:
        """
        Measure PUF reliability (reproducibility).
        
        Args:
            num_trials: Number of trials to run
            num_challenges: Number of challenges to test
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Reliability score (0.0 to 1.0)
        """
        # Generate fixed set of challenges (keep within int32 range)
        max_challenge = min(2**self.delay_stages, 2**31-1)
        challenges = self.rng.randint(0, max_challenge, size=num_challenges)
        
        # Get reference responses
        reference = self.generate_response_vector(challenges, temperature, voltage, add_noise=False)
        
        matches = 0
        for _ in range(num_trials):
            response = self.generate_response_vector(challenges, temperature, voltage, add_noise=True)
            matches += np.sum(response == reference)
        
        reliability = matches / (num_trials * num_challenges)
        return reliability
    
    def measure_uniqueness(
        self,
        other_pufs: List['ArbiterPUF'],
        num_challenges: int = 64,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> float:
        """
        Measure inter-device uniqueness (Hamming distance).
        
        Args:
            other_pufs: List of other Arbiter PUF instances
            num_challenges: Number of challenges to test
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Average Hamming distance (0.0 to 1.0, ideal is 0.5)
        """
        # Generate fixed set of challenges (keep within int32 range)
        max_challenge = min(2**self.delay_stages, 2**31-1)
        challenges = self.rng.randint(0, max_challenge, size=num_challenges)
        
        self_response = self.generate_response_vector(challenges, temperature, voltage, add_noise=False)
        
        hamming_distances = []
        for other_puf in other_pufs:
            other_response = other_puf.generate_response_vector(challenges, temperature, voltage, add_noise=False)
            hamming_dist = np.sum(self_response != other_response) / num_challenges
            hamming_distances.append(hamming_dist)
        
        return np.mean(hamming_distances)
    
    def get_entropy(self, num_challenges: int = 1000) -> float:
        """
        Estimate min-entropy of PUF responses.
        
        Args:
            num_challenges: Number of challenges to test
            
        Returns:
            Estimated min-entropy in bits
        """
        # Generate random challenges (keep within int32 range)
        max_challenge = min(2**self.delay_stages, 2**31-1)
        challenges = self.rng.randint(0, max_challenge, size=num_challenges)
        
        # Generate responses
        responses = self.generate_response_vector(challenges, add_noise=False)
        
        # Calculate bit probability
        bit_prob = responses.mean()
        
        # Min-entropy: -log2(max(p, 1-p))
        min_entropy = -np.log2(max(bit_prob, 1 - bit_prob)) * num_challenges
        
        return min_entropy
    
    def get_delay_distribution(self) -> np.ndarray:
        """
        Get delay distribution of all stages.
        
        Returns:
            Array of stage delays
        """
        return self.stage_delays
    
    def __repr__(self) -> str:
        return (
            f"ArbiterPUF(device_id={self.device_id}, "
            f"stages={self.delay_stages}, "
            f"response_bits={self.response_bits}, "
            f"noise={self.noise_level:.2%}, "
            f"delay_var={self.delay_variation*1e12:.2f}ps)"
        )


if __name__ == "__main__":
    # Demo usage
    print("=" * 70)
    print("Arbiter PUF Demonstration")
    print("=" * 70)
    
    # Create Arbiter PUF instance
    puf = ArbiterPUF(
        delay_stages=64,
        response_bits=64,
        noise_level=0.11,
        delay_variation=1e-12,
        device_id="device_001"
    )
    
    print(f"\n{puf}")
    
    # Generate responses for specific challenges
    print("\nGenerating PUF responses for challenges...")
    challenge1 = 0x123456789ABCDEF0
    challenge2 = 0xFEDCBA9876543210
    
    response1 = puf.generate_response(challenge1)
    response2 = puf.generate_response(challenge2)
    
    print(f"Challenge 1: 0x{challenge1:016X} -> Response: {response1}")
    print(f"Challenge 2: 0x{challenge2:016X} -> Response: {response2}")
    
    # Generate response vector
    print("\nGenerating 64-bit response vector...")
    response_vector = puf.generate_response_vector()
    print(f"Response vector: {response_vector[:32]}... ({len(response_vector)} bits)")
    
    # Measure reliability
    print("\nMeasuring reliability...")
    reliability = puf.measure_reliability(num_trials=100, num_challenges=64)
    print(f"Reliability: {reliability:.2%}")
    
    # Measure entropy
    entropy = puf.get_entropy(num_challenges=1000)
    print(f"Min-entropy: {entropy:.2f} bits")
    
    # Test with different environmental conditions
    print("\nTesting environmental sensitivity...")
    temperatures = [0, 25, 50, 75]
    for temp in temperatures:
        resp = puf.generate_response(challenge1, temperature=temp, add_noise=False)
        print(f"  Temperature {temp}�C: {resp}")
    
    # Test uniqueness with other devices
    print("\nTesting uniqueness with other devices...")
    other_pufs = [
        ArbiterPUF(device_id=f"device_{i:03d}")
        for i in range(2, 11)
    ]
    uniqueness = puf.measure_uniqueness(other_pufs, num_challenges=64)
    print(f"Average Hamming distance: {uniqueness:.2%} (ideal: 50%)")
    
    # Delay distribution
    print("\nDelay chain statistics:")
    delays = puf.get_delay_distribution()
    print(f"  Mean delay difference: {delays.mean()*1e12:.4f} ps")
    print(f"  Std dev: {delays.std()*1e12:.4f} ps")
    print(f"  Min: {delays.min()*1e12:.4f} ps")
    print(f"  Max: {delays.max()*1e12:.4f} ps")
    
    # Challenge-response speed
    print("\nPerformance test...")
    import time
    start = time.time()
    for _ in range(1000):
        puf.generate_response()
    elapsed = time.time() - start
    print(f"  1000 challenge-response pairs: {elapsed*1000:.2f} ms")
    print(f"  Average per response: {elapsed*1000000:.2f} �s")
    
    print("\n" + "=" * 70)
