"""
PUF Modeling Defense - ML-based Protection Against Modeling Attacks

This module implements machine learning-based defense mechanisms to evaluate
and protect Physical Unclonable Functions (PUFs) against modeling attacks.

Educational Context:
    - BSQC Semester 5: Hardware Root of Trust
    - Sentinel Framework Section 3, Page 8: AI for Hardware Security

Key Features:
    - Simulation of 4 ML attack types (RF, GB, SVM, NN)
    - Resilience scoring against modeling attacks
    - Mitigation strategy generation
    - Comparative PUF analysis

Attack Types Simulated:
    1. Random Forest (RF) - Ensemble decision trees
    2. Gradient Boosting (GB) - Sequential weak learners
    3. Support Vector Machine (SVM) - Kernel-based classification
    4. Neural Network (NN) - Deep learning approach

References:
    - Rührmair et al. (2010): Modeling Attacks on PUFs
    - Gassend et al. (2002): Physical Unclonable Functions
    - Sentinel Framework (2024): NCQC Curriculum Proposal
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

warnings.filterwarnings('ignore')


class PUFModelingDefense:
    """
    ML-based defense system for evaluating PUF resilience against modeling attacks.
    
    This system simulates various machine learning attacks on PUF implementations
    to assess their security and generate mitigation strategies.
    
    Attributes:
        test_size (float): Proportion of data for testing (0.0-1.0)
        random_state (int): Random seed for reproducibility
        attack_models (Dict): Dictionary of ML attack models
    """
    
    def __init__(
        self,
        test_size: float = 0.3,
        random_state: int = 42
    ):
        """
        Initialize PUF Modeling Defense system.
        
        Args:
            test_size: Proportion of data for testing (default: 0.3)
            random_state: Random seed for reproducibility (default: 42)
        """
        self.test_size = test_size
        self.random_state = random_state
        
        # Initialize attack models
        self.attack_models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=random_state
            ),
            'SVM': SVC(
                kernel='rbf',
                C=1.0,
                random_state=random_state
            ),
            'Neural Network': MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=500,
                random_state=random_state
            )
        }
    
    def _challenge_to_features(self, challenge: int, num_bits: int = 32) -> np.ndarray:
        """
        Convert challenge integer to binary feature vector.
        
        Args:
            challenge: Challenge value as integer
            num_bits: Number of bits in challenge (default: 32)
        
        Returns:
            Binary feature vector
        """
        # Convert to binary and pad
        binary = format(challenge, f'0{num_bits}b')
        return np.array([int(b) for b in binary])
    
    def _response_to_binary(self, response: bytes) -> int:
        """
        Convert PUF response bytes to binary value.
        
        Args:
            response: Response as bytes
        
        Returns:
            Binary value (0 or 1)
        """
        # Use first bit of response
        return int(response[0]) % 2
    
    def evaluate_puf_resilience(
        self,
        challenges: List[int],
        responses: List[bytes],
        puf_type: str = "Generic"
    ) -> Dict[str, Any]:
        """
        Evaluate PUF resilience against ML modeling attacks.
        
        Args:
            challenges: List of challenge values
            responses: List of corresponding PUF responses
            puf_type: Type of PUF being evaluated (for reporting)
        
        Returns:
            Dictionary containing:
                - overall_score: Overall resilience score (0-100)
                - attack_results: Results for each attack type
                - mitigation_strategies: Recommended mitigations
                - puf_type: Type of PUF evaluated
        """
        if len(challenges) != len(responses):
            raise ValueError("Challenges and responses must have same length")
        
        if len(challenges) < 100:
            raise ValueError("Need at least 100 challenge-response pairs")
        
        # Convert challenges to features
        X = np.array([
            self._challenge_to_features(c)
            for c in challenges
        ])
        
        # Convert responses to binary labels
        y = np.array([
            self._response_to_binary(r)
            for r in responses
        ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Evaluate each attack
        attack_results = {}
        for attack_name, model in self.attack_models.items():
            try:
                # Train attack model
                model.fit(X_train, y_train)
                
                # Predict on test set
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                
                # Calculate resilience score (inverse of accuracy)
                # 100 = perfect resilience, 0 = completely vulnerable
                resilience_score = (1 - accuracy) * 100
                
                attack_results[attack_name] = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'resilience_score': resilience_score,
                    'vulnerable': accuracy > 0.85  # Threshold for vulnerability
                }
                
            except Exception as e:
                attack_results[attack_name] = {
                    'error': str(e),
                    'resilience_score': 0.0,
                    'vulnerable': True
                }
        
        # Calculate overall resilience score
        valid_scores = [
            result['resilience_score']
            for result in attack_results.values()
            if 'resilience_score' in result
        ]
        overall_score = np.mean(valid_scores) if valid_scores else 0.0
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigations(
            attack_results,
            overall_score,
            puf_type
        )
        
        return {
            'puf_type': puf_type,
            'overall_score': overall_score,
            'attack_results': attack_results,
            'mitigation_strategies': mitigation_strategies,
            'num_samples': len(challenges),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def _generate_mitigations(
        self,
        attack_results: Dict[str, Dict],
        overall_score: float,
        puf_type: str
    ) -> List[str]:
        """
        Generate mitigation strategies based on attack results.
        
        Args:
            attack_results: Results from attack evaluation
            overall_score: Overall resilience score
            puf_type: Type of PUF
        
        Returns:
            List of mitigation strategy recommendations
        """
        strategies = []
        
        # Check vulnerability level
        if overall_score < 30:
            strategies.append(
                "CRITICAL: PUF is highly vulnerable to modeling attacks. "
                "Consider redesigning with increased complexity."
            )
        elif overall_score < 50:
            strategies.append(
                "WARNING: PUF shows moderate vulnerability. "
                "Implement additional security measures."
            )
        else:
            strategies.append(
                "GOOD: PUF shows strong resilience against modeling attacks."
            )
        
        # Check specific attack vulnerabilities
        vulnerable_attacks = [
            name for name, result in attack_results.items()
            if result.get('vulnerable', False)
        ]
        
        if vulnerable_attacks:
            strategies.append(
                f"Vulnerable to: {', '.join(vulnerable_attacks)}. "
                "Consider XOR arbiter chains or feed-forward architectures."
            )
        
        # PUF-specific recommendations
        if puf_type == "SRAM":
            strategies.extend([
                "Increase SRAM cell count to enhance entropy",
                "Implement fuzzy extractor with strong error correction",
                "Use multiple SRAM blocks with fusion algorithms"
            ])
        elif puf_type == "Ring Oscillator":
            strategies.extend([
                "Increase number of oscillator pairs",
                "Add environmental variation compensation",
                "Implement frequency jitter to reduce predictability"
            ])
        elif puf_type == "Arbiter":
            strategies.extend([
                "Use XOR arbiter PUF with multiple chains",
                "Implement feed-forward arbiter architecture",
                "Add lightweight obfuscation to delay chains"
            ])
        
        # General recommendations
        strategies.extend([
            "Limit number of challenge-response pairs exposed",
            "Implement challenge-response pair rotation",
            "Use cryptographic hash functions on PUF outputs",
            "Monitor for unusual query patterns",
            "Implement rate limiting on PUF queries"
        ])
        
        return strategies
    
    def compare_pufs(
        self,
        puf_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple PUF implementations.
        
        Args:
            puf_evaluations: List of evaluation results from evaluate_puf_resilience
        
        Returns:
            Comparative analysis dictionary
        """
        if not puf_evaluations:
            raise ValueError("Need at least one PUF evaluation")
        
        # Sort by overall score
        sorted_pufs = sorted(
            puf_evaluations,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        # Find best and worst
        best_puf = sorted_pufs[0]
        worst_puf = sorted_pufs[-1]
        
        # Calculate statistics
        scores = [puf['overall_score'] for puf in puf_evaluations]
        
        return {
            'num_pufs_compared': len(puf_evaluations),
            'best_puf': {
                'type': best_puf['puf_type'],
                'score': best_puf['overall_score']
            },
            'worst_puf': {
                'type': worst_puf['puf_type'],
                'score': worst_puf['overall_score']
            },
            'average_score': np.mean(scores),
            'score_std': np.std(scores),
            'rankings': [
                {
                    'rank': i + 1,
                    'type': puf['puf_type'],
                    'score': puf['overall_score']
                }
                for i, puf in enumerate(sorted_pufs)
            ]
        }
    
    def generate_report(
        self,
        evaluation: Dict[str, Any],
        filepath: Optional[str] = None
    ) -> str:
        """
        Generate human-readable security report.
        
        Args:
            evaluation: Evaluation results from evaluate_puf_resilience
            filepath: Optional path to save report
        
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 80,
            f"PUF MODELING ATTACK RESILIENCE REPORT",
            "=" * 80,
            "",
            f"PUF Type: {evaluation['puf_type']}",
            f"Overall Resilience Score: {evaluation['overall_score']:.2f}/100",
            f"Samples Analyzed: {evaluation['num_samples']}",
            "",
            "ATTACK RESULTS:",
            "-" * 80
        ]
        
        for attack_name, result in evaluation['attack_results'].items():
            if 'error' in result:
                report_lines.append(f"\n{attack_name}: ERROR - {result['error']}")
            else:
                report_lines.extend([
                    f"\n{attack_name}:",
                    f"  Accuracy: {result['accuracy']:.4f}",
                    f"  Precision: {result['precision']:.4f}",
                    f"  Recall: {result['recall']:.4f}",
                    f"  F1 Score: {result['f1_score']:.4f}",
                    f"  Resilience Score: {result['resilience_score']:.2f}/100",
                    f"  Vulnerable: {'YES' if result['vulnerable'] else 'NO'}"
                ])
        
        report_lines.extend([
            "",
            "MITIGATION STRATEGIES:",
            "-" * 80
        ])
        
        for i, strategy in enumerate(evaluation['mitigation_strategies'], 1):
            report_lines.append(f"{i}. {strategy}")
        
        report_lines.extend([
            "",
            "=" * 80,
            "End of Report",
            "=" * 80
        ])
        
        report = "\n".join(report_lines)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(report)
        
        return report


# Educational example usage
if __name__ == "__main__":
    print("PUF Modeling Defense - Educational Demo")
    print("=" * 60)
    
    # Create defense system
    defense = PUFModelingDefense(test_size=0.3)
    
    # Simulate PUF data (simplified)
    print("\n1. Generating synthetic PUF data...")
    np.random.seed(42)
    challenges = list(range(1000))
    
    # Simulate responses with some pattern (vulnerable PUF)
    responses = [
        bytes([sum(int(b) for b in format(c, '032b')) % 2])
        for c in challenges
    ]
    
    # Evaluate resilience
    print("2. Evaluating PUF resilience...")
    results = defense.evaluate_puf_resilience(
        challenges=challenges,
        responses=responses,
        puf_type="Simulated"
    )
    
    print(f"\n3. Results:")
    print(f"   Overall Score: {results['overall_score']:.2f}/100")
    print(f"   Attack Results:")
    for attack, metrics in results['attack_results'].items():
        if 'accuracy' in metrics:
            print(f"     {attack}: {metrics['accuracy']:.4f} accuracy")
    
    print(f"\n4. Mitigation Strategies:")
    for i, strategy in enumerate(results['mitigation_strategies'][:3], 1):
        print(f"   {i}. {strategy}")
    
    print("\n✓ Demo complete!")

# Made with Bob
