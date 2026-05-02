"""
Unit Tests for RAQT Anomaly Detector

Tests the machine learning-based eavesdropping detection system for the
RAQT (Remote Anonymous Quantum Transmission) protocol.

Test Coverage:
    - Detector initialization
    - Feature extraction
    - Model training
    - Anomaly detection
    - Batch processing
    - Model persistence
    - Edge cases and error handling
"""

import pytest
import numpy as np
import os
import tempfile
from src.ai.raqt_anomaly_detector import RAQTAnomalyDetector


class TestRAQTAnomalyDetectorInitialization:
    """Test detector initialization and configuration."""
    
    def test_default_initialization(self):
        """Test detector with default parameters."""
        detector = RAQTAnomalyDetector()
        
        assert detector.contamination == 0.1
        assert detector.n_estimators == 100
        assert detector.random_state == 42
        assert detector.is_trained == False
        assert len(detector.feature_names) == 16
    
    def test_custom_initialization(self):
        """Test detector with custom parameters."""
        detector = RAQTAnomalyDetector(
            contamination=0.2,
            n_estimators=50,
            random_state=123
        )
        
        assert detector.contamination == 0.2
        assert detector.n_estimators == 50
        assert detector.random_state == 123
    
    def test_feature_names(self):
        """Test that all expected features are defined."""
        detector = RAQTAnomalyDetector()
        expected_features = [
            'xor_bias', 'xor_entropy', 'error_rate', 'basis_bias',
            'basis_entropy', 'execution_time', 'time_per_bit',
            'message_length', 'num_parties', 'xor_runs', 'basis_runs',
            'xor_std', 'basis_std', 'error_variance', 'timing_variance',
            'correlation_xor_basis'
        ]
        
        assert detector.feature_names == expected_features


class TestFeatureExtraction:
    """Test feature extraction from RAQT executions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RAQTAnomalyDetector()
        self.normal_execution = {
            'xor_results': [0, 1, 0, 1, 0, 1, 0, 1] * 12 + [0, 1, 0, 1],
            'basis_choices': [0, 0, 1, 1, 0, 0, 1, 1] * 12 + [0, 0, 1, 1],
            'error_rate': 0.03,
            'execution_time': 1.0,
            'message_length': 100,
            'num_parties': 3
        }
    
    def test_feature_extraction_shape(self):
        """Test that feature extraction returns correct shape."""
        features = self.detector._extract_features(self.normal_execution)
        
        assert features.shape == (16,)
        assert isinstance(features, np.ndarray)
    
    def test_xor_bias_calculation(self):
        """Test XOR bias feature calculation."""
        # Perfectly balanced XOR
        execution = self.normal_execution.copy()
        execution['xor_results'] = [0, 1] * 50
        features = self.detector._extract_features(execution)
        
        assert abs(features[0]) < 0.01  # xor_bias should be near 0
        
        # Heavily biased XOR
        execution['xor_results'] = [1] * 100
        features = self.detector._extract_features(execution)
        
        assert features[0] == 0.5  # xor_bias should be 0.5
    
    def test_entropy_calculation(self):
        """Test entropy feature calculation."""
        # Maximum entropy (50/50 split)
        data = np.array([0, 1] * 50)
        entropy = self.detector._calculate_entropy(data)
        
        assert abs(entropy - 1.0) < 0.01  # Should be close to 1.0
        
        # Zero entropy (all same)
        data = np.array([1] * 100)
        entropy = self.detector._calculate_entropy(data)
        
        assert entropy == 0.0
    
    def test_runs_counting(self):
        """Test run counting feature."""
        # Alternating pattern (maximum runs)
        data = np.array([0, 1, 0, 1, 0, 1])
        runs = self.detector._count_runs(data)
        
        assert runs == 6
        
        # All same (minimum runs)
        data = np.array([1, 1, 1, 1])
        runs = self.detector._count_runs(data)
        
        assert runs == 1
    
    def test_feature_extraction_with_attack(self):
        """Test feature extraction detects attack patterns."""
        attack_execution = {
            'xor_results': [1] * 70 + [0] * 30,  # Biased
            'basis_choices': [0, 1] * 50,
            'error_rate': 0.15,  # Elevated
            'execution_time': 1.5,  # Slower
            'message_length': 100,
            'num_parties': 3
        }
        
        features = self.detector._extract_features(attack_execution)
        
        # Check that attack features are different
        assert features[0] > 0.1  # Higher XOR bias
        assert features[2] > 0.1  # Higher error rate
        assert features[5] > 1.2  # Longer execution time


class TestModelTraining:
    """Test model training functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RAQTAnomalyDetector(random_state=42)
        self.training_data = self._generate_normal_executions(50)
    
    def _generate_normal_executions(self, count):
        """Generate synthetic normal RAQT executions."""
        executions = []
        np.random.seed(42)
        
        for _ in range(count):
            execution = {
                'xor_results': np.random.randint(0, 2, 100).tolist(),
                'basis_choices': np.random.randint(0, 2, 100).tolist(),
                'error_rate': np.random.uniform(0.01, 0.05),
                'execution_time': np.random.uniform(0.9, 1.1),
                'message_length': 100,
                'num_parties': 3
            }
            executions.append(execution)
        
        return executions
    
    def test_training_success(self):
        """Test successful model training."""
        self.detector.train(self.training_data)
        
        assert self.detector.is_trained == True
    
    def test_training_insufficient_data(self):
        """Test training with insufficient data raises error."""
        with pytest.raises(ValueError, match="at least 10 executions"):
            self.detector.train(self.training_data[:5])
    
    def test_training_updates_scaler(self):
        """Test that training updates the feature scaler."""
        self.detector.train(self.training_data)
        
        assert hasattr(self.detector.scaler, 'mean_')
        assert hasattr(self.detector.scaler, 'scale_')


class TestAnomalyDetection:
    """Test anomaly detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RAQTAnomalyDetector(random_state=42)
        self.training_data = self._generate_normal_executions(50)
        self.detector.train(self.training_data)
    
    def _generate_normal_executions(self, count):
        """Generate synthetic normal RAQT executions."""
        executions = []
        np.random.seed(42)
        
        for _ in range(count):
            execution = {
                'xor_results': np.random.randint(0, 2, 100).tolist(),
                'basis_choices': np.random.randint(0, 2, 100).tolist(),
                'error_rate': np.random.uniform(0.01, 0.05),
                'execution_time': np.random.uniform(0.9, 1.1),
                'message_length': 100,
                'num_parties': 3
            }
            executions.append(execution)
        
        return executions
    
    def test_detect_normal_execution(self):
        """Test detection of normal execution."""
        normal_exec = self.training_data[0]
        is_anomaly, score, details = self.detector.detect(normal_exec)
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert isinstance(details, dict)
        assert 'xor_bias' in details
        assert 'error_rate' in details
    
    def test_detect_attack_execution(self):
        """Test detection of attack execution."""
        attack_exec = {
            'xor_results': [1] * 70 + [0] * 30,  # Biased
            'basis_choices': np.random.randint(0, 2, 100).tolist(),
            'error_rate': 0.15,  # Elevated
            'execution_time': 1.5,
            'message_length': 100,
            'num_parties': 3
        }
        
        is_anomaly, score, details = self.detector.detect(attack_exec)
        
        # Attack should have higher anomaly score
        assert score > 0.5
        assert details['xor_bias'] > 0.1
        assert details['error_rate'] > 0.1
    
    def test_detect_without_training(self):
        """Test detection without training raises error."""
        untrained_detector = RAQTAnomalyDetector()
        
        with pytest.raises(RuntimeError, match="must be trained"):
            untrained_detector.detect(self.training_data[0])
    
    def test_detection_details_structure(self):
        """Test that detection details have correct structure."""
        normal_exec = self.training_data[0]
        _, _, details = self.detector.detect(normal_exec)
        
        required_keys = [
            'is_anomaly', 'anomaly_score', 'xor_bias', 'basis_bias',
            'error_rate', 'execution_time', 'xor_entropy', 'basis_entropy',
            'features', 'feature_names'
        ]
        
        for key in required_keys:
            assert key in details


class TestBatchDetection:
    """Test batch detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RAQTAnomalyDetector(random_state=42)
        self.training_data = self._generate_normal_executions(50)
        self.detector.train(self.training_data)
    
    def _generate_normal_executions(self, count):
        """Generate synthetic normal RAQT executions."""
        executions = []
        np.random.seed(42)
        
        for _ in range(count):
            execution = {
                'xor_results': np.random.randint(0, 2, 100).tolist(),
                'basis_choices': np.random.randint(0, 2, 100).tolist(),
                'error_rate': np.random.uniform(0.01, 0.05),
                'execution_time': np.random.uniform(0.9, 1.1),
                'message_length': 100,
                'num_parties': 3
            }
            executions.append(execution)
        
        return executions
    
    def test_batch_detect_multiple_executions(self):
        """Test batch detection on multiple executions."""
        test_batch = self.training_data[:5]
        results = self.detector.batch_detect(test_batch)
        
        assert len(results) == 5
        assert all('is_anomaly' in r for r in results)
        assert all('anomaly_score' in r for r in results)
    
    def test_batch_detect_mixed_executions(self):
        """Test batch detection with mix of normal and attack."""
        attack_exec = {
            'xor_results': [1] * 80 + [0] * 20,
            'basis_choices': np.random.randint(0, 2, 100).tolist(),
            'error_rate': 0.20,
            'execution_time': 2.0,
            'message_length': 100,
            'num_parties': 3
        }
        
        test_batch = self.training_data[:3] + [attack_exec]
        results = self.detector.batch_detect(test_batch)
        
        # Attack should have higher score
        attack_result = results[-1]
        normal_scores = [r['anomaly_score'] for r in results[:-1]]
        
        assert attack_result['anomaly_score'] > max(normal_scores)


class TestModelPersistence:
    """Test model saving and loading."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RAQTAnomalyDetector(random_state=42)
        self.training_data = self._generate_normal_executions(50)
        self.detector.train(self.training_data)
        self.temp_dir = tempfile.mkdtemp()
    
    def _generate_normal_executions(self, count):
        """Generate synthetic normal RAQT executions."""
        executions = []
        np.random.seed(42)
        
        for _ in range(count):
            execution = {
                'xor_results': np.random.randint(0, 2, 100).tolist(),
                'basis_choices': np.random.randint(0, 2, 100).tolist(),
                'error_rate': np.random.uniform(0.01, 0.05),
                'execution_time': np.random.uniform(0.9, 1.1),
                'message_length': 100,
                'num_parties': 3
            }
            executions.append(execution)
        
        return executions
    
    def test_export_model(self):
        """Test model export."""
        model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        self.detector.export_model(model_path)
        
        assert os.path.exists(model_path)
    
    def test_export_untrained_model(self):
        """Test exporting untrained model raises error."""
        untrained_detector = RAQTAnomalyDetector()
        model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        
        with pytest.raises(RuntimeError, match="Cannot export untrained"):
            untrained_detector.export_model(model_path)
    
    def test_load_model(self):
        """Test model loading."""
        model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        self.detector.export_model(model_path)
        
        loaded_detector = RAQTAnomalyDetector.load_model(model_path)
        
        assert loaded_detector.is_trained == True
        assert loaded_detector.contamination == self.detector.contamination
        assert loaded_detector.n_estimators == self.detector.n_estimators
    
    def test_loaded_model_predictions(self):
        """Test that loaded model makes same predictions."""
        model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        self.detector.export_model(model_path)
        
        test_exec = self.training_data[0]
        original_result = self.detector.detect(test_exec)
        
        loaded_detector = RAQTAnomalyDetector.load_model(model_path)
        loaded_result = loaded_detector.detect(test_exec)
        
        # Results should be identical
        assert original_result[0] == loaded_result[0]  # is_anomaly
        assert abs(original_result[1] - loaded_result[1]) < 0.01  # score


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_xor_results(self):
        """Test handling of empty XOR results."""
        detector = RAQTAnomalyDetector()
        
        execution = {
            'xor_results': [],
            'basis_choices': [],
            'error_rate': 0.03,
            'execution_time': 1.0,
            'message_length': 0,
            'num_parties': 3
        }
        
        # Should not crash, but handle gracefully
        features = detector._extract_features(execution)
        assert features.shape == (16,)
    
    def test_single_bit_execution(self):
        """Test handling of single-bit execution."""
        detector = RAQTAnomalyDetector()
        
        execution = {
            'xor_results': [1],
            'basis_choices': [0],
            'error_rate': 0.0,
            'execution_time': 0.1,
            'message_length': 1,
            'num_parties': 2
        }
        
        features = detector._extract_features(execution)
        assert features.shape == (16,)
    
    def test_high_error_rate(self):
        """Test handling of very high error rate."""
        detector = RAQTAnomalyDetector()
        
        execution = {
            'xor_results': np.random.randint(0, 2, 100).tolist(),
            'basis_choices': np.random.randint(0, 2, 100).tolist(),
            'error_rate': 0.5,  # 50% error rate
            'execution_time': 1.0,
            'message_length': 100,
            'num_parties': 3
        }
        
        features = detector._extract_features(execution)
        assert features[2] == 0.5  # error_rate feature


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
