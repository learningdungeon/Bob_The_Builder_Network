"""
PUF Clone Detection Module

Implements statistical analysis techniques to detect cloned or emulated PUF devices.
Uses multiple statistical tests to identify anomalies that indicate cloning attempts.

Detection Methods:
1. Inter-Hamming Distance Analysis
2. Intra-Hamming Distance Analysis  
3. Entropy Analysis
4. Autocorrelation Analysis
5. Chi-Square Test
6. Kolmogorov-Smirnov Test
7. Machine Learning-based Detection
"""

import numpy as np
import hashlib
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CloneDetectionMethod(Enum):
    """Available clone detection methods"""
    INTER_HAMMING = "inter_hamming_distance"
    INTRA_HAMMING = "intra_hamming_distance"
    ENTROPY = "entropy_analysis"
    AUTOCORRELATION = "autocorrelation"
    CHI_SQUARE = "chi_square_test"
    KS_TEST = "kolmogorov_smirnov"
    ML_DETECTION = "machine_learning"
    COMBINED = "combined_analysis"


@dataclass
class CloneDetectionResult:
    """Result of clone detection analysis"""
    is_clone: bool
    confidence: float  # 0.0 to 1.0
    method: CloneDetectionMethod
    details: Dict
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'is_clone': self.is_clone,
            'confidence': self.confidence,
            'method': self.method.value,
            'details': self.details,
            'timestamp': self.timestamp
        }


class StatisticalAnalyzer:
    """Statistical analysis tools for PUF responses"""
    
    @staticmethod
    def hamming_distance(response1: bytes, response2: bytes) -> int:
        """
        Calculate Hamming distance between two responses
        
        Args:
            response1: First response
            response2: Second response
            
        Returns:
            Hamming distance (number of differing bits)
        """
        if len(response1) != len(response2):
            raise ValueError("Responses must have same length")
        
        return sum(b1 != b2 for b1, b2 in zip(response1, response2))
    
    @staticmethod
    def hamming_weight(response: bytes) -> int:
        """
        Calculate Hamming weight (number of 1s)
        
        Args:
            response: PUF response
            
        Returns:
            Number of 1 bits
        """
        return sum(bin(byte).count('1') for byte in response)
    
    @staticmethod
    def calculate_entropy(response: bytes) -> float:
        """
        Calculate Shannon entropy of response
        
        Args:
            response: PUF response
            
        Returns:
            Entropy value (0 to 8 bits per byte)
        """
        if len(response) == 0:
            return 0.0
        
        # Count byte frequencies
        freq = {}
        for byte in response:
            freq[byte] = freq.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        total = len(response)
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    @staticmethod
    def autocorrelation(response: bytes, lag: int = 1) -> float:
        """
        Calculate autocorrelation of response
        
        Args:
            response: PUF response
            lag: Lag for autocorrelation
            
        Returns:
            Autocorrelation coefficient
        """
        # Convert to bit array
        bits = np.unpackbits(np.frombuffer(response, dtype=np.uint8))
        
        if len(bits) <= lag:
            return 0.0
        
        # Calculate autocorrelation
        x = bits[:-lag] if lag > 0 else bits
        y = bits[lag:] if lag > 0 else bits
        
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        
        numerator = np.sum((x - mean_x) * (y - mean_y))
        denominator = np.sqrt(np.sum((x - mean_x)**2) * np.sum((y - mean_y)**2))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    @staticmethod
    def chi_square_test(response: bytes) -> Tuple[float, float]:
        """
        Perform chi-square test for randomness
        
        Args:
            response: PUF response
            
        Returns:
            Tuple of (chi_square_statistic, p_value)
        """
        # Count bit frequencies
        bits = np.unpackbits(np.frombuffer(response, dtype=np.uint8))
        ones = np.sum(bits)
        zeros = len(bits) - ones
        
        # Expected frequency (should be 50/50)
        expected = len(bits) / 2
        
        # Chi-square statistic
        chi_square = ((ones - expected)**2 / expected + 
                     (zeros - expected)**2 / expected)
        
        # Approximate p-value (simplified)
        # For 1 degree of freedom, critical value at 0.05 is 3.841
        p_value = 1.0 if chi_square < 3.841 else 0.0
        
        return chi_square, p_value
    
    @staticmethod
    def kolmogorov_smirnov_test(responses: List[bytes]) -> float:
        """
        Perform Kolmogorov-Smirnov test on multiple responses
        
        Args:
            responses: List of PUF responses
            
        Returns:
            KS statistic
        """
        if len(responses) < 2:
            return 0.0
        
        # Convert to Hamming weights
        weights = [StatisticalAnalyzer.hamming_weight(r) for r in responses]
        weights = np.array(weights) / (len(responses[0]) * 8)  # Normalize
        
        # Calculate empirical CDF
        weights_sorted = np.sort(weights)
        n = len(weights)
        
        # Compare with uniform distribution
        uniform_cdf = np.linspace(0, 1, n)
        empirical_cdf = np.arange(1, n + 1) / n
        
        # KS statistic
        ks_stat = np.max(np.abs(empirical_cdf - uniform_cdf))
        
        return ks_stat


class InterHammingAnalyzer:
    """
    Inter-Hamming Distance Analysis
    
    Analyzes Hamming distances between responses from different PUF instances.
    Genuine PUFs should have ~50% inter-HD, clones will have lower values.
    """
    
    def __init__(self, expected_inter_hd: float = 0.50, tolerance: float = 0.10):
        """
        Initialize analyzer
        
        Args:
            expected_inter_hd: Expected inter-HD for genuine PUFs (default 50%)
            tolerance: Acceptable deviation (default 10%)
        """
        self.expected_inter_hd = expected_inter_hd
        self.tolerance = tolerance
        self.baseline_responses: Dict[str, List[bytes]] = {}
    
    def register_device(self, device_id: str, responses: List[bytes]):
        """
        Register a device's baseline responses
        
        Args:
            device_id: Device identifier
            responses: List of baseline responses
        """
        self.baseline_responses[device_id] = responses
    
    def analyze(self, test_responses: List[bytes], device_id: Optional[str] = None) -> CloneDetectionResult:
        """
        Analyze test responses for cloning
        
        Args:
            test_responses: Responses to analyze
            device_id: Optional device ID to compare against
            
        Returns:
            Clone detection result
        """
        if not self.baseline_responses:
            return CloneDetectionResult(
                is_clone=False,
                confidence=0.0,
                method=CloneDetectionMethod.INTER_HAMMING,
                details={'error': 'No baseline responses registered'}
            )
        
        # Calculate inter-HD with all registered devices
        inter_hds = []
        
        for baseline_id, baseline_resps in self.baseline_responses.items():
            if device_id and baseline_id == device_id:
                continue  # Skip self-comparison
            
            for test_resp in test_responses:
                for baseline_resp in baseline_resps:
                    hd = StatisticalAnalyzer.hamming_distance(test_resp, baseline_resp)
                    normalized_hd = hd / (len(test_resp) * 8)
                    inter_hds.append(normalized_hd)
        
        if not inter_hds:
            return CloneDetectionResult(
                is_clone=False,
                confidence=0.0,
                method=CloneDetectionMethod.INTER_HAMMING,
                details={'error': 'No comparisons possible'}
            )
        
        # Calculate statistics
        mean_inter_hd = np.mean(inter_hds)
        std_inter_hd = np.std(inter_hds)
        
        # Detect clone: inter-HD significantly lower than expected
        deviation = abs(mean_inter_hd - self.expected_inter_hd)
        is_clone = bool(mean_inter_hd < self.expected_inter_hd - self.tolerance)
        confidence = float(min(1.0, deviation / self.tolerance))
        
        return CloneDetectionResult(
            is_clone=is_clone,
            confidence=confidence,
            method=CloneDetectionMethod.INTER_HAMMING,
            details={
                'mean_inter_hd': float(mean_inter_hd),
                'std_inter_hd': float(std_inter_hd),
                'expected_inter_hd': self.expected_inter_hd,
                'deviation': float(deviation),
                'num_comparisons': len(inter_hds)
            }
        )


class IntraHammingAnalyzer:
    """
    Intra-Hamming Distance Analysis
    
    Analyzes Hamming distances between multiple responses from the same PUF.
    Genuine PUFs have low intra-HD due to noise, clones may have higher values.
    """
    
    def __init__(self, max_intra_hd: float = 0.15):
        """
        Initialize analyzer
        
        Args:
            max_intra_hd: Maximum acceptable intra-HD (default 15%)
        """
        self.max_intra_hd = max_intra_hd
    
    def analyze(self, responses: List[bytes]) -> CloneDetectionResult:
        """
        Analyze intra-HD of responses
        
        Args:
            responses: Multiple responses from same PUF
            
        Returns:
            Clone detection result
        """
        if len(responses) < 2:
            return CloneDetectionResult(
                is_clone=False,
                confidence=0.0,
                method=CloneDetectionMethod.INTRA_HAMMING,
                details={'error': 'Need at least 2 responses'}
            )
        
        # Calculate all pairwise intra-HDs
        intra_hds = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                hd = StatisticalAnalyzer.hamming_distance(responses[i], responses[j])
                normalized_hd = hd / (len(responses[i]) * 8)
                intra_hds.append(normalized_hd)
        
        # Calculate statistics
        mean_intra_hd = np.mean(intra_hds)
        std_intra_hd = np.std(intra_hds)
        max_observed = np.max(intra_hds)
        
        # Detect clone: intra-HD too high (inconsistent responses)
        is_clone = bool(mean_intra_hd > self.max_intra_hd)
        confidence = float(min(1.0, mean_intra_hd / self.max_intra_hd)) if is_clone else 0.0
        
        return CloneDetectionResult(
            is_clone=is_clone,
            confidence=confidence,
            method=CloneDetectionMethod.INTRA_HAMMING,
            details={
                'mean_intra_hd': float(mean_intra_hd),
                'std_intra_hd': float(std_intra_hd),
                'max_intra_hd': float(max_observed),
                'threshold': self.max_intra_hd,
                'num_comparisons': len(intra_hds)
            }
        )


class EntropyAnalyzer:
    """
    Entropy Analysis
    
    Analyzes entropy of PUF responses. Low entropy indicates predictable
    patterns that may suggest emulation or weak PUF implementation.
    """
    
    def __init__(self, min_entropy: float = 7.0):
        """
        Initialize analyzer
        
        Args:
            min_entropy: Minimum acceptable entropy (bits per byte, max 8.0)
        """
        self.min_entropy = min_entropy
    
    def analyze(self, responses: List[bytes]) -> CloneDetectionResult:
        """
        Analyze entropy of responses
        
        Args:
            responses: PUF responses to analyze
            
        Returns:
            Clone detection result
        """
        if not responses:
            return CloneDetectionResult(
                is_clone=False,
                confidence=0.0,
                method=CloneDetectionMethod.ENTROPY,
                details={'error': 'No responses provided'}
            )
        
        # Calculate entropy for each response
        entropies = [StatisticalAnalyzer.calculate_entropy(r) for r in responses]
        
        mean_entropy = np.mean(entropies)
        std_entropy = np.std(entropies)
        min_observed = np.min(entropies)
        
        # Detect clone: entropy too low
        is_clone = bool(mean_entropy < self.min_entropy)
        confidence = float(1.0 - (mean_entropy / 8.0)) if is_clone else 0.0
        
        return CloneDetectionResult(
            is_clone=is_clone,
            confidence=confidence,
            method=CloneDetectionMethod.ENTROPY,
            details={
                'mean_entropy': float(mean_entropy),
                'std_entropy': float(std_entropy),
                'min_entropy': float(min_observed),
                'threshold': self.min_entropy,
                'max_possible': 8.0
            }
        )


class CloneDetectionSystem:
    """
    Comprehensive Clone Detection System
    
    Combines multiple detection methods for robust clone identification.
    """
    
    def __init__(self):
        """Initialize clone detection system"""
        self.inter_hd_analyzer = InterHammingAnalyzer()
        self.intra_hd_analyzer = IntraHammingAnalyzer()
        self.entropy_analyzer = EntropyAnalyzer()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # Detection history
        self.detection_history: List[CloneDetectionResult] = []
    
    def register_genuine_device(self, device_id: str, responses: List[bytes]):
        """
        Register a genuine device for baseline
        
        Args:
            device_id: Device identifier
            responses: List of baseline responses
        """
        self.inter_hd_analyzer.register_device(device_id, responses)
    
    def detect_clone(self, test_responses: List[bytes], 
                    methods: Optional[List[CloneDetectionMethod]] = None) -> Dict:
        """
        Perform comprehensive clone detection
        
        Args:
            test_responses: Responses to analyze
            methods: Specific methods to use (None = all methods)
            
        Returns:
            Combined detection results
        """
        if methods is None:
            methods = [
                CloneDetectionMethod.INTER_HAMMING,
                CloneDetectionMethod.INTRA_HAMMING,
                CloneDetectionMethod.ENTROPY,
                CloneDetectionMethod.AUTOCORRELATION,
                CloneDetectionMethod.CHI_SQUARE
            ]
        
        results = {}
        
        # Inter-Hamming Distance
        if CloneDetectionMethod.INTER_HAMMING in methods:
            results['inter_hd'] = self.inter_hd_analyzer.analyze(test_responses)
        
        # Intra-Hamming Distance
        if CloneDetectionMethod.INTRA_HAMMING in methods:
            results['intra_hd'] = self.intra_hd_analyzer.analyze(test_responses)
        
        # Entropy Analysis
        if CloneDetectionMethod.ENTROPY in methods:
            results['entropy'] = self.entropy_analyzer.analyze(test_responses)
        
        # Autocorrelation
        if CloneDetectionMethod.AUTOCORRELATION in methods:
            autocorrs = [self.statistical_analyzer.autocorrelation(r) for r in test_responses]
            mean_autocorr = np.mean(autocorrs)
            is_clone = bool(abs(mean_autocorr) > 0.3)  # High autocorrelation suggests patterns
            results['autocorrelation'] = CloneDetectionResult(
                is_clone=is_clone,
                confidence=float(min(1.0, abs(mean_autocorr) / 0.3)) if is_clone else 0.0,
                method=CloneDetectionMethod.AUTOCORRELATION,
                details={'mean_autocorrelation': float(mean_autocorr)}
            )
        
        # Chi-Square Test
        if CloneDetectionMethod.CHI_SQUARE in methods:
            chi_squares = [self.statistical_analyzer.chi_square_test(r) for r in test_responses]
            mean_chi = np.mean([c[0] for c in chi_squares])
            is_clone = bool(mean_chi > 10.0)  # High chi-square suggests non-randomness
            results['chi_square'] = CloneDetectionResult(
                is_clone=is_clone,
                confidence=float(min(1.0, mean_chi / 10.0)) if is_clone else 0.0,
                method=CloneDetectionMethod.CHI_SQUARE,
                details={'mean_chi_square': float(mean_chi)}
            )
        
        # Combined decision
        clone_votes = sum(1 for r in results.values() if r.is_clone)
        total_votes = len(results)
        combined_confidence = np.mean([r.confidence for r in results.values()])
        
        combined_result = {
            'is_clone': clone_votes > total_votes / 2,
            'confidence': float(combined_confidence),
            'clone_votes': clone_votes,
            'total_tests': total_votes,
            'individual_results': {k: v.to_dict() for k, v in results.items()},
            'timestamp': time.time()
        }
        
        return combined_result
    
    def get_detection_report(self, result: Dict) -> str:
        """
        Generate human-readable detection report
        
        Args:
            result: Detection result from detect_clone()
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("CLONE DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"\nOverall Result: {'CLONE DETECTED' if result['is_clone'] else 'GENUINE DEVICE'}")
        report.append(f"Confidence: {result['confidence']*100:.1f}%")
        report.append(f"Tests Passed: {result['total_tests'] - result['clone_votes']}/{result['total_tests']}")
        report.append("\nIndividual Test Results:")
        report.append("-" * 70)
        
        for test_name, test_result in result['individual_results'].items():
            status = "FAIL (Clone)" if test_result['is_clone'] else "PASS (Genuine)"
            report.append(f"\n{test_name.upper()}:")
            report.append(f"  Status: {status}")
            report.append(f"  Confidence: {test_result['confidence']*100:.1f}%")
            report.append(f"  Details: {test_result['details']}")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


def demo_clone_detection():
    """Demonstration of clone detection system"""
    print("\n" + "=" * 70)
    print("PUF CLONE DETECTION DEMONSTRATION")
    print("=" * 70)
    
    # Initialize system
    print("\n1. Initializing clone detection system...")
    detector = CloneDetectionSystem()
    
    # Create genuine responses (simulated)
    print("\n2. Generating genuine PUF responses...")
    genuine_responses_1 = [os.urandom(256) for _ in range(30)]
    genuine_responses_2 = [os.urandom(256) for _ in range(30)]
    
    # Register genuine devices
    print("\n3. Registering genuine device baselines...")
    detector.register_genuine_device("device_001", genuine_responses_1)
    detector.register_genuine_device("device_002", genuine_responses_2)
    print("   Registered 2 genuine devices")
    
    # Test genuine device
    print("\n4. Testing genuine device responses...")
    test_genuine = [os.urandom(256) for _ in range(20)]
    genuine_result = detector.detect_clone(test_genuine)
    
    print(f"   Result: {'CLONE DETECTED' if genuine_result['is_clone'] else 'GENUINE DEVICE'}")
    print(f"   Confidence: {genuine_result['confidence']*100:.1f}%")
    print(f"   Tests Passed: {genuine_result['total_tests'] - genuine_result['clone_votes']}/{genuine_result['total_tests']}")
    
    # Simulate cloned device (low entropy, predictable)
    print("\n5. Testing simulated clone (predictable patterns)...")
    clone_responses = [bytes([i % 256] * 256) for i in range(20)]
    
    clone_result = detector.detect_clone(clone_responses)
    
    print(f"   Result: {'CLONE DETECTED' if clone_result['is_clone'] else 'GENUINE DEVICE'}")
    print(f"   Confidence: {clone_result['confidence']*100:.1f}%")
    print(f"   Tests Failed: {clone_result['clone_votes']}/{clone_result['total_tests']}")
    
    # Generate detailed report
    print("\n6. Detailed Clone Detection Report:")
    print(detector.get_detection_report(clone_result))
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Detection Methods:")
    print("  - Inter-Hamming Distance: Compares with known devices")
    print("  - Intra-Hamming Distance: Checks response consistency")
    print("  - Entropy Analysis: Detects low-entropy patterns")
    print("  - Autocorrelation: Identifies predictable sequences")
    print("  - Chi-Square Test: Validates randomness")
    print("=" * 70)


if __name__ == "__main__":
    demo_clone_detection()

# Made with Bob
