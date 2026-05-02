"""
PUF Fusion Module

Combines multiple PUF types (SRAM, Ring Oscillator, Arbiter) using various
fusion algorithms to create a robust hybrid PUF system with enhanced security
and reliability.
"""

import numpy as np
import hashlib
from typing import Optional, List, Dict, Tuple
from enum import Enum


class FusionMethod(Enum):
    """Enumeration of available fusion methods."""
    MAJORITY_VOTING = "majority_voting"
    WEIGHTED_AVERAGE = "weighted_average"
    CONCATENATION = "concatenation"
    XOR_FUSION = "xor_fusion"
    CONFIDENCE_BASED = "confidence_based"


class PUFFusion:
    """
    Hybrid PUF fusion system combining multiple PUF types.
    
    Supports multiple fusion algorithms:
    - Majority Voting: Simple bit-wise majority across PUFs
    - Weighted Average: Confidence-weighted combination
    - Concatenation: Direct concatenation of responses
    - XOR Fusion: XOR combination for enhanced randomness
    - Confidence-Based: Adaptive weighting based on reliability
    
    Attributes:
        puf_modules: Dictionary of PUF instances
        fusion_method: Selected fusion algorithm
        weights: Weights for each PUF type (for weighted methods)
    """
    
    def __init__(
        self,
        sram_puf=None,
        ro_puf=None,
        arbiter_puf=None,
        fusion_method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize PUF fusion system.
        
        Args:
            sram_puf: SRAM PUF instance
            ro_puf: Ring Oscillator PUF instance
            arbiter_puf: Arbiter PUF instance
            fusion_method: Fusion algorithm to use
            weights: Custom weights for each PUF type
        """
        self.puf_modules = {}
        
        if sram_puf is not None:
            self.puf_modules['sram'] = sram_puf
        if ro_puf is not None:
            self.puf_modules['ro'] = ro_puf
        if arbiter_puf is not None:
            self.puf_modules['arbiter'] = arbiter_puf
        
        if not self.puf_modules:
            raise ValueError("At least one PUF module must be provided")
        
        self.fusion_method = fusion_method
        
        # Set default weights based on PUF characteristics
        if weights is None:
            self.weights = {
                'sram': 0.30,      # Lower weight due to higher noise
                'ro': 0.45,        # Higher weight due to better stability
                'arbiter': 0.25    # Medium weight
            }
        else:
            self.weights = weights
        
        # Normalize weights
        total_weight = sum(self.weights.get(k, 0) for k in self.puf_modules.keys())
        self.weights = {k: v/total_weight for k, v in self.weights.items() if k in self.puf_modules}
        
        # Calculate target response length
        self._calculate_response_length()
    
    def _calculate_response_length(self):
        """Calculate the target response length based on fusion method."""
        if self.fusion_method == FusionMethod.CONCATENATION:
            # Sum of all PUF response lengths
            self.response_length = sum(
                getattr(puf, 'response_bits', 64) 
                for puf in self.puf_modules.values()
            )
        else:
            # Use the maximum response length
            self.response_length = max(
                getattr(puf, 'response_bits', 64)
                for puf in self.puf_modules.values()
            )
    
    def _align_responses(
        self,
        responses: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Align response lengths by padding or truncating.
        
        Args:
            responses: Dictionary of PUF responses
            
        Returns:
            Dictionary of aligned responses
        """
        target_length = self.response_length
        
        aligned = {}
        for puf_type, response in responses.items():
            if len(response) < target_length:
                # Pad with repeated response
                repeats = (target_length // len(response)) + 1
                padded = np.tile(response, repeats)[:target_length]
                aligned[puf_type] = padded
            elif len(response) > target_length:
                # Truncate
                aligned[puf_type] = response[:target_length]
            else:
                aligned[puf_type] = response
        
        return aligned
    
    def _majority_voting(
        self,
        responses: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Combine responses using majority voting.
        
        Args:
            responses: Dictionary of aligned PUF responses
            
        Returns:
            Fused response array
        """
        # Stack all responses
        response_matrix = np.array(list(responses.values()))
        
        # Majority vote for each bit position
        fused = (response_matrix.sum(axis=0) > len(responses) / 2).astype(np.uint8)
        
        return fused
    
    def _weighted_average(
        self,
        responses: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Combine responses using weighted average.
        
        Args:
            responses: Dictionary of aligned PUF responses
            
        Returns:
            Fused response array
        """
        weighted_sum = np.zeros(self.response_length, dtype=float)
        
        for puf_type, response in responses.items():
            weight = self.weights.get(puf_type, 1.0 / len(responses))
            weighted_sum += response * weight
        
        # Threshold at 0.5
        fused = (weighted_sum > 0.5).astype(np.uint8)
        
        return fused
    
    def _concatenation(
        self,
        responses: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Combine responses by concatenation.
        
        Args:
            responses: Dictionary of PUF responses (not aligned)
            
        Returns:
            Concatenated response array
        """
        # Concatenate in consistent order
        ordered_responses = [responses[k] for k in sorted(responses.keys())]
        fused = np.concatenate(ordered_responses)
        
        return fused
    
    def _xor_fusion(
        self,
        responses: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Combine responses using XOR operation.
        
        Args:
            responses: Dictionary of aligned PUF responses
            
        Returns:
            XOR-fused response array
        """
        fused = np.zeros(self.response_length, dtype=np.uint8)
        
        for response in responses.values():
            fused ^= response
        
        return fused
    
    def _confidence_based(
        self,
        responses: Dict[str, np.ndarray],
        confidences: Optional[Dict[str, np.ndarray]] = None
    ) -> np.ndarray:
        """
        Combine responses using confidence-based weighting.
        
        Args:
            responses: Dictionary of aligned PUF responses
            confidences: Optional confidence scores for each bit
            
        Returns:
            Confidence-weighted fused response
        """
        if confidences is None:
            # Use default weights as confidence
            confidences = {
                puf_type: np.full(self.response_length, self.weights.get(puf_type, 1.0))
                for puf_type in responses.keys()
            }
        
        weighted_sum = np.zeros(self.response_length, dtype=float)
        total_confidence = np.zeros(self.response_length, dtype=float)
        
        for puf_type, response in responses.items():
            conf = confidences.get(puf_type, np.ones(self.response_length))
            weighted_sum += response * conf
            total_confidence += conf
        
        # Avoid division by zero
        total_confidence = np.maximum(total_confidence, 1e-10)
        
        # Weighted average
        fused = (weighted_sum / total_confidence > 0.5).astype(np.uint8)
        
        return fused
    
    def generate_response(
        self,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> np.ndarray:
        """
        Generate fused PUF response from all modules.
        
        Args:
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add environmental noise
            
        Returns:
            Fused response array
        """
        # Collect responses from all PUF modules
        responses = {}
        
        if 'sram' in self.puf_modules:
            responses['sram'] = self.puf_modules['sram'].generate_response(
                temperature=temperature,
                add_noise=add_noise
            )
        
        if 'ro' in self.puf_modules:
            responses['ro'] = self.puf_modules['ro'].generate_response(
                temperature=temperature,
                voltage=voltage,
                add_noise=add_noise
            )
        
        if 'arbiter' in self.puf_modules:
            responses['arbiter'] = self.puf_modules['arbiter'].generate_response_vector(
                temperature=temperature,
                voltage=voltage,
                add_noise=add_noise
            )
        
        # Apply fusion algorithm
        if self.fusion_method == FusionMethod.CONCATENATION:
            fused = self._concatenation(responses)
        else:
            # Align responses for other methods
            aligned = self._align_responses(responses)
            
            if self.fusion_method == FusionMethod.MAJORITY_VOTING:
                fused = self._majority_voting(aligned)
            elif self.fusion_method == FusionMethod.WEIGHTED_AVERAGE:
                fused = self._weighted_average(aligned)
            elif self.fusion_method == FusionMethod.XOR_FUSION:
                fused = self._xor_fusion(aligned)
            elif self.fusion_method == FusionMethod.CONFIDENCE_BASED:
                fused = self._confidence_based(aligned)
            else:
                raise ValueError(f"Unknown fusion method: {self.fusion_method}")
        
        return fused
    
    def generate_response_bytes(
        self,
        temperature: float = 25.0,
        voltage: float = 1.0,
        add_noise: bool = True
    ) -> bytes:
        """
        Generate fused PUF response as bytes.
        
        Args:
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            add_noise: Whether to add environmental noise
            
        Returns:
            Fused response as bytes
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
        Generate stable fused response using majority voting over samples.
        
        Args:
            num_samples: Number of samples to average
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Stable fused response
        """
        samples = np.array([
            self.generate_response(temperature, voltage, add_noise=True)
            for _ in range(num_samples)
        ])
        
        # Majority voting across samples
        stable = (samples.sum(axis=0) > num_samples / 2).astype(np.uint8)
        
        return stable
    
    def measure_reliability(
        self,
        num_trials: int = 100,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> float:
        """
        Measure reliability of fused PUF system.
        
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
        
        reliability = matches / (num_trials * len(reference))
        return reliability
    
    def measure_individual_reliabilities(
        self,
        num_trials: int = 100,
        temperature: float = 25.0,
        voltage: float = 1.0
    ) -> Dict[str, float]:
        """
        Measure reliability of each individual PUF module.
        
        Args:
            num_trials: Number of trials to run
            temperature: Operating temperature in Celsius
            voltage: Supply voltage (normalized)
            
        Returns:
            Dictionary of reliability scores per PUF type
        """
        reliabilities = {}
        
        for puf_type, puf in self.puf_modules.items():
            reliabilities[puf_type] = puf.measure_reliability(
                num_trials=num_trials,
                temperature=temperature
            )
        
        return reliabilities
    
    def get_entropy(self, num_samples: int = 1000) -> float:
        """
        Estimate min-entropy of fused PUF responses.
        
        Args:
            num_samples: Number of samples to test
            
        Returns:
            Estimated min-entropy in bits
        """
        responses = np.array([
            self.generate_response(add_noise=False)
            for _ in range(num_samples)
        ])
        
        # Calculate bit probabilities
        bit_probs = responses.mean(axis=0)
        
        # Min-entropy: -log2(max(p, 1-p))
        min_entropy = -np.log2(np.maximum(bit_probs, 1 - bit_probs)).sum()
        
        return min_entropy
    
    def compare_fusion_methods(
        self,
        num_trials: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare performance of different fusion methods.
        
        Args:
            num_trials: Number of trials per method
            
        Returns:
            Dictionary of metrics per fusion method
        """
        results = {}
        original_method = self.fusion_method
        
        for method in FusionMethod:
            self.fusion_method = method
            self._calculate_response_length()
            
            try:
                reliability = self.measure_reliability(num_trials=num_trials)
                entropy = self.get_entropy(num_samples=min(num_trials, 100))
                
                results[method.value] = {
                    'reliability': reliability,
                    'entropy': entropy,
                    'response_length': self.response_length
                }
            except Exception as e:
                results[method.value] = {'error': str(e)}
        
        # Restore original method
        self.fusion_method = original_method
        self._calculate_response_length()
        
        return results
    
    def __repr__(self) -> str:
        puf_types = ', '.join(self.puf_modules.keys())
        return (
            f"PUFFusion(pufs=[{puf_types}], "
            f"method={self.fusion_method.value}, "
            f"response_length={self.response_length})"
        )


if __name__ == "__main__":
    # Demo usage
    print("=" * 70)
    print("Hybrid PUF Fusion Demonstration")
    print("=" * 70)
    
    # Import PUF modules
    try:
        from sram_puf import SRAMPUF
        from ro_puf import RingOscillatorPUF
        from arbiter_puf import ArbiterPUF
        
        # Create individual PUF instances
        print("\nInitializing PUF modules...")
        sram = SRAMPUF(device_id="device_001")
        ro = RingOscillatorPUF(device_id="device_001")
        arbiter = ArbiterPUF(device_id="device_001")
        
        print(f"  SRAM PUF: {sram.response_bits} bits")
        print(f"  RO PUF: {ro.response_bits} bits")
        print(f"  Arbiter PUF: {arbiter.response_bits} bits")
        
        # Create hybrid PUF with weighted average fusion
        print("\nCreating hybrid PUF system...")
        hybrid = PUFFusion(
            sram_puf=sram,
            ro_puf=ro,
            arbiter_puf=arbiter,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE
        )
        
        print(f"{hybrid}")
        print(f"Weights: {hybrid.weights}")
        
        # Generate fused response
        print("\nGenerating fused responses...")
        response1 = hybrid.generate_response()
        response2 = hybrid.generate_response()
        
        print(f"Response 1: {response1[:32]}... ({len(response1)} bits)")
        print(f"Response 2: {response2[:32]}... ({len(response2)} bits)")
        
        # Measure reliability
        print("\nMeasuring hybrid PUF reliability...")
        reliability = hybrid.measure_reliability(num_trials=100)
        print(f"Fused reliability: {reliability:.2%}")
        
        # Measure individual reliabilities
        print("\nIndividual PUF reliabilities:")
        individual = hybrid.measure_individual_reliabilities(num_trials=100)
        for puf_type, rel in individual.items():
            print(f"  {puf_type.upper()}: {rel:.2%}")
        
        # Measure entropy
        entropy = hybrid.get_entropy(num_samples=100)
        print(f"\nFused min-entropy: {entropy:.2f} bits")
        
        # Compare fusion methods
        print("\nComparing fusion methods...")
        comparison = hybrid.compare_fusion_methods(num_trials=50)
        for method, metrics in comparison.items():
            if 'error' not in metrics:
                print(f"  {method}:")
                print(f"    Reliability: {metrics['reliability']:.2%}")
                print(f"    Entropy: {metrics['entropy']:.2f} bits")
                print(f"    Length: {metrics['response_length']} bits")
        
        print("\n" + "=" * 70)
        
    except ImportError as e:
        print(f"\nError: Could not import PUF modules: {e}")
        print("Make sure sram_puf.py, ro_puf.py, and arbiter_puf.py are in the same directory.")
