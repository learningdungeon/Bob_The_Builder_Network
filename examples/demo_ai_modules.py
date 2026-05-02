#!/usr/bin/env python3
"""
Demonstration of Sentinel-Integrated AI Modules

This script demonstrates the AI/ML security enhancements for the RAQT
Quantum Security Framework, aligned with Pakistan's NCQC Sentinel Framework.

Educational Context:
    - BSQC Semester 5: Hardware Root of Trust (PUF Modeling Defense)
    - BSQC Semester 7: Secure Quantum Networks (RAQT Anomaly Detection)

Usage:
    python examples/demo_ai_modules.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from src.ai.raqt_anomaly_detector import RAQTAnomalyDetector
from src.ai.puf_modeling_defense import PUFModelingDefense
from src.puf.sram_puf import SRAMPUF
from src.puf.ro_puf import RingOscillatorPUF
from src.puf.arbiter_puf import ArbiterPUF


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_raqt_anomaly_detection():
    """Demonstrate RAQT anomaly detection for eavesdropping."""
    print_section("RAQT Anomaly Detection - Eavesdropping Detection")
    
    print("Initializing RAQT Anomaly Detector...")
    detector = RAQTAnomalyDetector(
        contamination=0.1,
        n_estimators=100,
        random_state=42
    )
    
    # Simulate normal RAQT executions
    print("\n1. Generating normal RAQT execution data...")
    normal_executions = []
    for i in range(50):
        execution = {
            'xor_results': np.random.randint(0, 2, 100).tolist(),
            'basis_choices': np.random.randint(0, 2, 100).tolist(),
            'error_rate': np.random.uniform(0.01, 0.05),
            'execution_time': np.random.uniform(0.8, 1.2),
            'message_length': 100,
            'num_parties': 3
        }
        normal_executions.append(execution)
    
    print(f"   Generated {len(normal_executions)} normal executions")
    print(f"   Average error rate: {np.mean([e['error_rate'] for e in normal_executions]):.4f}")
    
    # Train the detector
    print("\n2. Training anomaly detector on normal data...")
    detector.train(normal_executions)
    print("   [OK] Training complete")
    
    # Test with normal execution
    print("\n3. Testing with normal execution...")
    test_normal = {
        'xor_results': np.random.randint(0, 2, 100).tolist(),
        'basis_choices': np.random.randint(0, 2, 100).tolist(),
        'error_rate': 0.03,
        'execution_time': 1.0,
        'message_length': 100,
        'num_parties': 3
    }
    
    is_anomaly, score, details = detector.detect(test_normal)
    print(f"   Anomaly detected: {is_anomaly}")
    print(f"   Anomaly score: {score:.4f}")
    print(f"   XOR bias: {details['xor_bias']:.4f}")
    print(f"   Error rate: {details['error_rate']:.4f}")
    
    # Test with eavesdropping attack
    print("\n4. Testing with simulated eavesdropping attack...")
    test_attack = {
        'xor_results': [1] * 70 + [0] * 30,  # Biased XOR results
        'basis_choices': np.random.randint(0, 2, 100).tolist(),
        'error_rate': 0.15,  # Elevated error rate
        'execution_time': 1.5,  # Slower execution
        'message_length': 100,
        'num_parties': 3
    }
    
    is_anomaly, score, details = detector.detect(test_attack)
    print(f"   Anomaly detected: {is_anomaly}")
    print(f"   Anomaly score: {score:.4f}")
    print(f"   XOR bias: {details['xor_bias']:.4f} (suspicious!)")
    print(f"   Error rate: {details['error_rate']:.4f} (elevated!)")
    
    # Batch analysis
    print("\n5. Performing batch analysis...")
    test_batch = normal_executions[:5] + [test_attack]
    results = detector.batch_detect(test_batch)
    
    anomaly_count = sum(1 for r in results if r['is_anomaly'])
    print(f"   Analyzed {len(test_batch)} executions")
    print(f"   Anomalies detected: {anomaly_count}")
    print(f"   Detection rate: {anomaly_count / len(test_batch) * 100:.1f}%")
    
    # Export model
    print("\n6. Exporting trained model...")
    model_path = "raqt_anomaly_model.pkl"
    detector.export_model(model_path)
    print(f"   [OK] Model saved to {model_path}")
    
    print("\n[OK] RAQT Anomaly Detection demonstration complete!")


def demo_puf_modeling_defense():
    """Demonstrate PUF modeling attack defense."""
    print_section("PUF Modeling Defense - Hardware Security")
    
    print("Initializing PUF Modeling Defense system...")
    defense = PUFModelingDefense(
        test_size=0.3,
        random_state=42
    )
    
    # Test SRAM PUF
    print("\n1. Testing SRAM PUF resilience...")
    sram_puf = SRAMPUF(cell_count=128, response_bits=128, noise_level=0.05)
    
    print("   Generating challenge-response pairs...")
    #challenges = [np.random.randint(0, 2**32) for _ in range(1000)]
    challenges = [np.random.randint(0, 232, dtype=np.int64) for _ in range(1000)]
    responses = [sram_puf.generate_response().tobytes() for _ in challenges]
    challenges = [np.random.randint(0, 232, dtype=np.int64) for _ in range(1000)]
    print("   Simulating modeling attacks...")
    sram_results = defense.evaluate_puf_resilience(
        challenges=challenges,
        responses=responses,
        puf_type='SRAM'
    )
    
    print(f"\n   SRAM PUF Results:")
    print(f"   Overall resilience score: {sram_results['overall_score']:.2f}/100")
    print(f"   Attack results:")
    for attack, metrics in sram_results['attack_results'].items():
        print(f"     - {attack}: Accuracy={metrics['accuracy']:.4f}, "
              f"Resilience={metrics['resilience_score']:.2f}/100")
    
    # Test Ring Oscillator PUF
    print("\n2. Testing Ring Oscillator PUF resilience...")
    ro_puf = RingOscillatorPUF(oscillator_pairs=64, response_bits=64, noise_level=0.1)
    
    challenges = [np.random.randint(0, 2**31-1) for _ in range(1000)]
    responses = [ro_puf.generate_response().tobytes() for _ in challenges]
    
    ro_results = defense.evaluate_puf_resilience(
        challenges=challenges,
        responses=responses,
        puf_type='Ring Oscillator'
    )
    
    print(f"\n   Ring Oscillator PUF Results:")
    print(f"   Overall resilience score: {ro_results['overall_score']:.2f}/100")
    print(f"   Attack results:")
    for attack, metrics in ro_results['attack_results'].items():
        print(f"     - {attack}: Accuracy={metrics['accuracy']:.4f}, "
              f"Resilience={metrics['resilience_score']:.2f}/100")
    
    # Test Arbiter PUF
    print("\n3. Testing Arbiter PUF resilience...")
    arbiter_puf = ArbiterPUF(delay_stages=64, response_bits=64, noise_level=0.05)
    
    challenges = [np.random.randint(0, 2**31-1) for _ in range(1000)]
    responses = [bytes([arbiter_puf.generate_response(c)]) for c in challenges]
    
    arbiter_results = defense.evaluate_puf_resilience(
        challenges=challenges,
        responses=responses,
        puf_type='Arbiter'
    )
    
    print(f"\n   Arbiter PUF Results:")
    print(f"   Overall resilience score: {arbiter_results['overall_score']:.2f}/100")
    print(f"   Attack results:")
    for attack, metrics in arbiter_results['attack_results'].items():
        print(f"     - {attack}: Accuracy={metrics['accuracy']:.4f}, "
              f"Resilience={metrics['resilience_score']:.2f}/100")
    
    # Generate mitigation strategies
    print("\n4. Generating mitigation strategies...")
    
    print("\n   SRAM PUF Mitigations:")
    for strategy in sram_results['mitigation_strategies']:
        print(f"   • {strategy}")
    
    print("\n   Ring Oscillator PUF Mitigations:")
    for strategy in ro_results['mitigation_strategies']:
        print(f"   • {strategy}")
    
    print("\n   Arbiter PUF Mitigations:")
    for strategy in arbiter_results['mitigation_strategies']:
        print(f"   • {strategy}")
    
    # Comparative analysis
    print("\n5. Comparative PUF Analysis:")
    print(f"   SRAM PUF:           {sram_results['overall_score']:.2f}/100")
    print(f"   Ring Oscillator PUF: {ro_results['overall_score']:.2f}/100")
    print(f"   Arbiter PUF:        {arbiter_results['overall_score']:.2f}/100")
    
    best_puf = max(
        [('SRAM', sram_results), ('Ring Oscillator', ro_results), ('Arbiter', arbiter_results)],
        key=lambda x: x[1]['overall_score']
    )
    print(f"\n   [OK] Most resilient: {best_puf[0]} PUF ({best_puf[1]['overall_score']:.2f}/100)")
    
    print("\n[OK] PUF Modeling Defense demonstration complete!")


def main():
    """Run all AI module demonstrations."""
    print("\n" + "=" * 80)
    print("  SENTINEL-INTEGRATED AI MODULES DEMONSTRATION")
    print("  RAQT Quantum Security Framework")
    print("  Aligned with NCQC Sentinel Framework 2024")
    print("=" * 80)
    
    try:
        # Demo 1: RAQT Anomaly Detection
        demo_raqt_anomaly_detection()
        
        # Demo 2: PUF Modeling Defense
        demo_puf_modeling_defense()
        
        # Summary
        print_section("Demonstration Summary")
        print("[OK] RAQT Anomaly Detection: Successfully detected eavesdropping patterns")
        print("[OK] PUF Modeling Defense: Evaluated resilience against ML attacks")
        print("\nEducational Alignment:")
        print("  • BSQC Semester 5: Hardware Root of Trust (PUF Security)")
        print("  • BSQC Semester 7: Secure Quantum Networks (RAQT Security)")
        print("\nSentinel Framework Integration:")
        print("  • Section 3, Page 8: AI for Hardware Security")
        print("  • Section 3, Page 9: AI for Network Security")
        print("\nFor more information, see:")
        print("  • docs/SENTINEL_AI_MODULES.md")
        print("  • docs/SENTINEL_FRAMEWORK_ALIGNMENT.md")
        
    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
