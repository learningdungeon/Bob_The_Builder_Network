"""
RAQT Anomaly Detector - ML-based Eavesdropping Detection

This module implements machine learning-based anomaly detection for the RAQT
(Remote Anonymous Quantum Transmission) protocol to identify potential
eavesdropping attacks.

Educational Context:
    - BSQC Semester 7: Secure Quantum Networks
    - Sentinel Framework Section 3, Page 9: AI for Network Security

Key Features:
    - Feature extraction from RAQT execution traces
    - Isolation Forest-based anomaly detection
    - Real-time eavesdropping pattern recognition
    - Batch analysis capabilities

Attack Patterns Detected:
    1. Biased XOR results (Eve's measurement interference)
    2. Elevated error rates (quantum channel disturbance)
    3. Basis choice bias (active probing attacks)
    4. Timing anomalies (computational overhead from attacks)

References:
    - Christandl & Wehner (2004): Quantum Anonymous Transmission
    - Liu et al. (2008): Isolation Forest Algorithm
    - Sentinel Framework (2024): NCQC Curriculum Proposal
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import warnings

warnings.filterwarnings('ignore')


class RAQTAnomalyDetector:
    """
    Machine Learning-based anomaly detector for RAQT protocol security.
    
    This detector analyzes RAQT execution traces to identify potential
    eavesdropping attacks by detecting statistical anomalies in quantum
    communication patterns.
    
    Attributes:
        contamination (float): Expected proportion of anomalies (0.0-0.5)
        n_estimators (int): Number of isolation trees
        random_state (int): Random seed for reproducibility
        model (IsolationForest): Trained anomaly detection model
        scaler (StandardScaler): Feature normalization scaler
        is_trained (bool): Whether model has been trained
    """
    
    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        """
        Initialize RAQT Anomaly Detector.
        
        Args:
            contamination: Expected proportion of anomalies (default: 0.1)
            n_estimators: Number of isolation trees (default: 100)
            random_state: Random seed for reproducibility (default: 42)
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        
        # Initialize ML components
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature names for interpretability
        self.feature_names = [
            'xor_bias',           # Bias in XOR results (0=balanced, 1=all same)
            'xor_entropy',        # Shannon entropy of XOR results
            'error_rate',         # Quantum bit error rate
            'basis_bias',         # Bias in basis choices
            'basis_entropy',      # Shannon entropy of basis choices
            'execution_time',     # Total execution time
            'time_per_bit',       # Average time per bit
            'message_length',     # Length of transmitted message
            'num_parties',        # Number of participating parties
            'xor_runs',           # Number of runs in XOR sequence
            'basis_runs',         # Number of runs in basis sequence
            'xor_std',            # Standard deviation of XOR results
            'basis_std',          # Standard deviation of basis choices
            'error_variance',     # Variance in error rates
            'timing_variance',    # Variance in execution timing
            'correlation_xor_basis'  # Correlation between XOR and basis
        ]
    
    def _extract_features(self, execution: Dict[str, Any]) -> np.ndarray:
        """
        Extract 16 security-relevant features from RAQT execution.
        
        Args:
            execution: Dictionary containing RAQT execution data with keys:
                - xor_results: List of XOR results (0 or 1)
                - basis_choices: List of basis choices (0 or 1)
                - error_rate: Quantum bit error rate
                - execution_time: Total execution time
                - message_length: Length of message
                - num_parties: Number of parties
        
        Returns:
            Feature vector as numpy array
        """
        xor = np.array(execution['xor_results'])
        basis = np.array(execution['basis_choices'])
        
        # Feature 1-2: XOR statistics
        xor_bias = abs(np.mean(xor) - 0.5)  # Deviation from 50/50
        xor_entropy = self._calculate_entropy(xor)
        
        # Feature 3: Error rate
        error_rate = execution['error_rate']
        
        # Feature 4-5: Basis statistics
        basis_bias = abs(np.mean(basis) - 0.5)
        basis_entropy = self._calculate_entropy(basis)
        
        # Feature 6-7: Timing statistics
        execution_time = execution['execution_time']
        msg_len = execution['message_length']; time_per_bit = execution_time / msg_len if msg_len > 0 else 0.0
        
        # Feature 8-9: Protocol parameters
        message_length = execution['message_length']
        num_parties = execution['num_parties']
        
        # Feature 10-11: Run statistics (consecutive same values)
        xor_runs = self._count_runs(xor)
        basis_runs = self._count_runs(basis)
        
        # Feature 12-13: Variability
        xor_std = np.std(xor)
        basis_std = np.std(basis)
        
        # Feature 14-15: Advanced statistics
        error_variance = error_rate ** 2  # Proxy for error variability
        timing_variance = (execution_time - 1.0) ** 2  # Deviation from expected
        
        # Feature 16: Correlation
        correlation = np.corrcoef(xor, basis)[0, 1] if len(xor) > 1 else 0.0
        
        return np.array([
            xor_bias, xor_entropy, error_rate, basis_bias, basis_entropy,
            execution_time, time_per_bit, message_length, num_parties,
            xor_runs, basis_runs, xor_std, basis_std, error_variance,
            timing_variance, correlation
        ])
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of binary data."""
        if len(data) == 0:
            return 0.0
        
        p1 = np.mean(data)
        p0 = 1 - p1
        
        if p0 == 0 or p1 == 0:
            return 0.0
        
        return -p0 * np.log2(p0) - p1 * np.log2(p1)
    
    def _count_runs(self, data: np.ndarray) -> int:
        """Count number of runs (consecutive same values) in sequence."""
        if len(data) <= 1:
            return len(data)
        
        runs = 1
        for i in range(1, len(data)):
            if data[i] != data[i-1]:
                runs += 1
        
        return runs
    
    def train(self, executions: List[Dict[str, Any]]) -> None:
        """
        Train anomaly detector on normal RAQT executions.
        
        Args:
            executions: List of normal RAQT execution dictionaries
        
        Raises:
            ValueError: If insufficient training data provided
        """
        if len(executions) < 10:
            raise ValueError("Need at least 10 executions for training")
        
        # Extract features from all executions
        features = np.array([
            self._extract_features(exec_data)
            for exec_data in executions
        ])
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train isolation forest
        self.model.fit(features_scaled)
        self.is_trained = True
    
    def detect(
        self,
        execution: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Detect if RAQT execution shows signs of eavesdropping.
        
        Args:
            execution: RAQT execution dictionary to analyze
        
        Returns:
            Tuple of (is_anomaly, anomaly_score, details):
                - is_anomaly: True if eavesdropping detected
                - anomaly_score: Anomaly score (higher = more anomalous)
                - details: Dictionary with diagnostic information
        
        Raises:
            RuntimeError: If detector not trained
        """
        if not self.is_trained:
            raise RuntimeError("Detector must be trained before detection")
        
        # Extract and normalize features
        features = self._extract_features(execution).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        # Predict anomaly
        prediction = self.model.predict(features_scaled)[0]
        is_anomaly = bool(prediction == -1)
        
        # Get anomaly score (lower = more anomalous)
        score = self.model.score_samples(features_scaled)[0]
        anomaly_score = -score  # Invert so higher = more anomalous
        
        # Extract key metrics for interpretation
        xor = np.array(execution['xor_results'])
        basis = np.array(execution['basis_choices'])
        
        details = {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'xor_bias': float(abs(np.mean(xor) - 0.5)),
            'basis_bias': float(abs(np.mean(basis) - 0.5)),
            'error_rate': float(execution['error_rate']),
            'execution_time': float(execution['execution_time']),
            'xor_entropy': float(self._calculate_entropy(xor)),
            'basis_entropy': float(self._calculate_entropy(basis)),
            'features': features[0].tolist(),
            'feature_names': self.feature_names
        }
        
        return is_anomaly, anomaly_score, details
    
    def batch_detect(
        self,
        executions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple RAQT executions for anomalies.
        
        Args:
            executions: List of RAQT execution dictionaries
        
        Returns:
            List of detection results for each execution
        """
        results = []
        for execution in executions:
            is_anomaly, score, details = self.detect(execution)
            results.append({
                'is_anomaly': is_anomaly,
                'anomaly_score': score,
                'details': details
            })
        
        return results
    
    def export_model(self, filepath: str) -> None:
        """
        Export trained model to file.
        
        Args:
            filepath: Path to save model
        
        Raises:
            RuntimeError: If detector not trained
        """
        if not self.is_trained:
            raise RuntimeError("Cannot export untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    @classmethod
    def load_model(cls, filepath: str) -> 'RAQTAnomalyDetector':
        """
        Load trained model from file.
        
        Args:
            filepath: Path to saved model
        
        Returns:
            Loaded RAQTAnomalyDetector instance
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        detector = cls(
            contamination=model_data['contamination'],
            n_estimators=model_data['n_estimators']
        )
        detector.model = model_data['model']
        detector.scaler = model_data['scaler']
        detector.feature_names = model_data['feature_names']
        detector.is_trained = True
        
        return detector
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get relative importance of each feature (experimental).
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")
        
        # Note: Isolation Forest doesn't provide direct feature importance
        # This is a simplified heuristic based on feature variance
        importance = {}
        for i, name in enumerate(self.feature_names):
            importance[name] = 1.0 / (i + 1)  # Placeholder
        
        return importance


# Educational example usage
if __name__ == "__main__":
    print("RAQT Anomaly Detector - Educational Demo")
    print("=" * 60)
    
    # Create detector
    detector = RAQTAnomalyDetector(contamination=0.1)
    
    # Generate synthetic normal data
    print("\n1. Generating normal RAQT executions...")
    normal_data = []
    for _ in range(50):
        execution = {
            'xor_results': np.random.randint(0, 2, 100).tolist(),
            'basis_choices': np.random.randint(0, 2, 100).tolist(),
            'error_rate': np.random.uniform(0.01, 0.05),
            'execution_time': np.random.uniform(0.9, 1.1),
            'message_length': 100,
            'num_parties': 3
        }
        normal_data.append(execution)
    
    # Train detector
    print("2. Training detector...")
    detector.train(normal_data)
    print("   ✓ Training complete")
    
    # Test with normal execution
    print("\n3. Testing normal execution...")
    test_normal = normal_data[0]
    is_anomaly, score, details = detector.detect(test_normal)
    print(f"   Anomaly: {is_anomaly}, Score: {score:.4f}")
    
    # Test with attack
    print("\n4. Testing eavesdropping attack...")
    test_attack = {
        'xor_results': [1] * 70 + [0] * 30,  # Biased
        'basis_choices': np.random.randint(0, 2, 100).tolist(),
        'error_rate': 0.15,  # High error
        'execution_time': 1.5,
        'message_length': 100,
        'num_parties': 3
    }
    is_anomaly, score, details = detector.detect(test_attack)
    print(f"   Anomaly: {is_anomaly}, Score: {score:.4f}")
    print(f"   XOR bias: {details['xor_bias']:.4f}")
    
    print("\n✓ Demo complete!")

# Made with Bob
