"""
Simplified Performance Benchmark

Basic performance testing for RAQT quantum network components.
Measures execution time without complex dependencies.
"""

import time
import statistics
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.puf.sram_puf import SRAMPUF
from src.puf.ro_puf import RingOscillatorPUF
from src.puf.arbiter_puf import ArbiterPUF
from src.security.clone_detection import CloneDetectionSystem
from src.security.timing_attack_mitigation import ConstantTimeOps


def measure_time(func, *args, samples=100, **kwargs):
    """Measure execution time"""
    times = []
    for _ in range(samples):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'mean_ms': statistics.mean(times) * 1000,
        'std_ms': statistics.stdev(times) * 1000,
        'min_ms': min(times) * 1000,
        'max_ms': max(times) * 1000,
        'throughput_ops_sec': 1.0 / statistics.mean(times)
    }


def main():
    print("\n" + "=" * 70)
    print("RAQT PERFORMANCE BENCHMARK - SIMPLIFIED")
    print("=" * 70)
    
    results = {}
    
    # 1. SRAM PUF
    print("\n1. Benchmarking SRAM PUF...")
    sram = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    result = measure_time(sram.generate_response)
    results['SRAM_PUF'] = result
    print(f"   Mean: {result['mean_ms']:.3f} ms")
    print(f"   Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
    
    # 2. Ring Oscillator PUF
    print("\n2. Benchmarking Ring Oscillator PUF...")
    ro = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
    result = measure_time(ro.generate_response)
    results['RO_PUF'] = result
    print(f"   Mean: {result['mean_ms']:.3f} ms")
    print(f"   Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
    
    # 3. Arbiter PUF
    print("\n3. Benchmarking Arbiter PUF...")
    arbiter = ArbiterPUF(delay_stages=64, noise_level=0.11)
    result = measure_time(arbiter.generate_response)
    results['Arbiter_PUF'] = result
    print(f"   Mean: {result['mean_ms']:.3f} ms")
    print(f"   Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
    
    # 4. Clone Detection
    print("\n4. Benchmarking Clone Detection...")
    detector = CloneDetectionSystem()
    genuine_responses = [os.urandom(256) for _ in range(30)]
    detector.register_genuine_device("device_001", genuine_responses)
    test_responses = [os.urandom(256) for _ in range(20)]
    result = measure_time(detector.detect_clone, test_responses, samples=10)
    results['Clone_Detection'] = result
    print(f"   Mean: {result['mean_ms']:.3f} ms")
    print(f"   Throughput: {result['throughput_ops_sec']:.2f} ops/sec")
    
    # 5. Constant-Time Operations
    print("\n5. Benchmarking Constant-Time Comparison...")
    a = os.urandom(32)
    b = os.urandom(32)
    result = measure_time(ConstantTimeOps.ct_compare, a, b)
    results['CT_Compare'] = result
    print(f"   Mean: {result['mean_ms']:.3f} ms")
    print(f"   Throughput: {result['throughput_ops_sec']:.0f} ops/sec")
    
    # Save results
    os.makedirs('benchmarks/results', exist_ok=True)
    with open('benchmarks/results/simple_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    print("\nResults saved to: benchmarks/results/simple_benchmark.json")
    print("\nSummary:")
    for name, data in results.items():
        print(f"  {name}: {data['mean_ms']:.3f} ms ({data['throughput_ops_sec']:.0f} ops/sec)")
    print("=" * 70)


if __name__ == "__main__":
    main()

# Made with Bob
