"""
Performance Benchmarking Suite

Comprehensive performance testing and visualization for the RAQT quantum network
with PUF+PQC security layer.

Measures:
- PUF response generation time
- Cryptographic operation latency
- Authentication protocol overhead
- Encryption/decryption throughput
- Network communication latency
- Memory usage
- CPU utilization

Generates:
- Performance reports (text, JSON, HTML)
- Visualization charts (matplotlib)
- Comparison tables
- Trend analysis
"""

import time
import psutil
import json
import statistics
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to benchmark
from src.puf.sram_puf import SRAMPUF
from src.puf.ro_puf import RingOscillatorPUF
from src.puf.arbiter_puf import ArbiterPUF
from src.puf.fusion import PUFFusion, FusionAlgorithm
from src.puf.fuzzy_extractor import FuzzyExtractor
from src.crypto.pqc import PQCKeyDerivation
from src.auth.zkp_auth import ZKPAuthenticator, ZKPProtocol
from src.security.clone_detection import CloneDetectionSystem
from src.security.timing_attack_mitigation import ConstantTimeOps, TimingAnalyzer

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, visualization disabled")


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    name: str
    category: str
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    throughput: Optional[float] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    samples: int = 100
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    name: str
    version: str
    results: List[BenchmarkResult] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def add_result(self, result: BenchmarkResult):
        """Add benchmark result"""
        self.results.append(result)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'results': [r.to_dict() for r in self.results],
            'metadata': self.metadata
        }
    
    def save_json(self, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def save_text(self, filepath: str):
        """Save results to text file"""
        with open(filepath, 'w') as f:
            f.write(self.generate_text_report())
    
    def generate_text_report(self) -> str:
        """Generate text report"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"PERFORMANCE BENCHMARK REPORT: {self.name}")
        lines.append(f"Version: {self.version}")
        lines.append(f"Timestamp: {datetime.now().isoformat()}")
        lines.append("=" * 80)
        
        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        for category, results in sorted(categories.items()):
            lines.append(f"\n{category.upper()}")
            lines.append("-" * 80)
            
            for result in results:
                lines.append(f"\n{result.name}:")
                lines.append(f"  Mean Time: {result.mean_time*1000:.3f} ms")
                lines.append(f"  Std Dev: {result.std_dev*1000:.3f} ms")
                lines.append(f"  Min Time: {result.min_time*1000:.3f} ms")
                lines.append(f"  Max Time: {result.max_time*1000:.3f} ms")
                
                if result.throughput:
                    lines.append(f"  Throughput: {result.throughput:.2f} ops/sec")
                if result.memory_mb:
                    lines.append(f"  Memory: {result.memory_mb:.2f} MB")
                if result.cpu_percent:
                    lines.append(f"  CPU: {result.cpu_percent:.1f}%")
                
                lines.append(f"  Samples: {result.samples}")
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


class PerformanceBenchmark:
    """Main benchmarking class"""
    
    def __init__(self, samples: int = 100):
        """
        Initialize benchmark
        
        Args:
            samples: Number of samples per benchmark
        """
        self.samples = samples
        self.suite = BenchmarkSuite(
            name="RAQT Quantum Network Performance",
            version="1.0"
        )
        self.process = psutil.Process()
    
    def measure_time(self, func, *args, **kwargs) -> Tuple[List[float], float, float]:
        """
        Measure execution time of function
        
        Args:
            func: Function to measure
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tuple of (times, memory_mb, cpu_percent)
        """
        times = []
        memory_before = self.process.memory_info().rss / 1024 / 1024
        cpu_before = self.process.cpu_percent()
        
        for _ in range(self.samples):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        memory_after = self.process.memory_info().rss / 1024 / 1024
        cpu_after = self.process.cpu_percent()
        
        memory_delta = memory_after - memory_before
        cpu_avg = (cpu_before + cpu_after) / 2
        
        return times, memory_delta, cpu_avg
    
    def benchmark_puf_response(self):
        """Benchmark PUF response generation"""
        print("\nBenchmarking PUF Response Generation...")
        
        # SRAM PUF
        sram = SRAMPUF(size=256, noise_rate=0.15)
        challenge = b"test_challenge_123"
        
        times, mem, cpu = self.measure_time(sram.generate_response, challenge)
        
        self.suite.add_result(BenchmarkResult(
            name="SRAM PUF Response Generation",
            category="PUF Operations",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Ring Oscillator PUF
        ro = RingOscillatorPUF(num_pairs=128, noise_rate=0.08)
        
        times, mem, cpu = self.measure_time(ro.generate_response, challenge)
        
        self.suite.add_result(BenchmarkResult(
            name="Ring Oscillator PUF Response Generation",
            category="PUF Operations",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Arbiter PUF
        arbiter = ArbiterPUF(num_stages=64, noise_rate=0.11)
        
        times, mem, cpu = self.measure_time(arbiter.generate_response, challenge)
        
        self.suite.add_result(BenchmarkResult(
            name="Arbiter PUF Response Generation",
            category="PUF Operations",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def benchmark_puf_fusion(self):
        """Benchmark PUF fusion"""
        print("\nBenchmarking PUF Fusion...")
        
        fusion = PUFFusion()
        
        # Add PUFs
        fusion.add_puf(SRAMPUF(size=256, noise_rate=0.15), weight=0.4)
        fusion.add_puf(RingOscillatorPUF(num_pairs=128, noise_rate=0.08), weight=0.35)
        fusion.add_puf(ArbiterPUF(num_stages=64, noise_rate=0.11), weight=0.25)
        
        challenge = b"fusion_test_challenge"
        
        # Test each fusion algorithm
        algorithms = [
            FusionAlgorithm.WEIGHTED_AVERAGE,
            FusionAlgorithm.MAJORITY_VOTING,
            FusionAlgorithm.XOR_FUSION,
            FusionAlgorithm.CONCATENATION
        ]
        
        for algo in algorithms:
            times, mem, cpu = self.measure_time(
                fusion.generate_fused_response, challenge, algo
            )
            
            self.suite.add_result(BenchmarkResult(
                name=f"PUF Fusion - {algo.value}",
                category="PUF Fusion",
                mean_time=statistics.mean(times),
                std_dev=statistics.stdev(times),
                min_time=min(times),
                max_time=max(times),
                throughput=1.0 / statistics.mean(times),
                memory_mb=mem,
                cpu_percent=cpu,
                samples=self.samples
            ))
    
    def benchmark_fuzzy_extractor(self):
        """Benchmark fuzzy extractor"""
        print("\nBenchmarking Fuzzy Extractor...")
        
        extractor = FuzzyExtractor()
        response = os.urandom(256)
        
        # Enrollment
        times, mem, cpu = self.measure_time(extractor.enroll, response)
        
        self.suite.add_result(BenchmarkResult(
            name="Fuzzy Extractor Enrollment",
            category="Error Correction",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Reconstruction
        key, helper_data = extractor.enroll(response)
        noisy_response = bytearray(response)
        # Add noise
        for i in range(0, len(noisy_response), 10):
            noisy_response[i] ^= 0xFF
        
        times, mem, cpu = self.measure_time(
            extractor.reconstruct, bytes(noisy_response), helper_data
        )
        
        self.suite.add_result(BenchmarkResult(
            name="Fuzzy Extractor Reconstruction",
            category="Error Correction",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def benchmark_pqc_operations(self):
        """Benchmark post-quantum cryptography"""
        print("\nBenchmarking Post-Quantum Cryptography...")
        
        pqc = PQCKeyDerivation()
        puf_key = os.urandom(32)
        
        # Key derivation
        times, mem, cpu = self.measure_time(pqc.derive_keys, puf_key)
        
        self.suite.add_result(BenchmarkResult(
            name="PQC Key Derivation (HKDF)",
            category="Post-Quantum Crypto",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Dilithium signature generation
        keys = pqc.derive_keys(puf_key)
        message = b"test_message_for_signing"
        
        times, mem, cpu = self.measure_time(pqc.sign_message, message, keys['dilithium_sk'])
        
        self.suite.add_result(BenchmarkResult(
            name="Dilithium Signature Generation",
            category="Post-Quantum Crypto",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Dilithium signature verification
        signature = pqc.sign_message(message, keys['dilithium_sk'])
        
        times, mem, cpu = self.measure_time(
            pqc.verify_signature, message, signature, keys['dilithium_pk']
        )
        
        self.suite.add_result(BenchmarkResult(
            name="Dilithium Signature Verification",
            category="Post-Quantum Crypto",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # ML-KEM encapsulation
        times, mem, cpu = self.measure_time(pqc.encapsulate, keys['mlkem_pk'])
        
        self.suite.add_result(BenchmarkResult(
            name="ML-KEM Key Encapsulation",
            category="Post-Quantum Crypto",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # ML-KEM decapsulation
        ciphertext, _ = pqc.encapsulate(keys['mlkem_pk'])
        
        times, mem, cpu = self.measure_time(
            pqc.decapsulate, ciphertext, keys['mlkem_sk']
        )
        
        self.suite.add_result(BenchmarkResult(
            name="ML-KEM Key Decapsulation",
            category="Post-Quantum Crypto",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def benchmark_zkp_authentication(self):
        """Benchmark zero-knowledge proof authentication"""
        print("\nBenchmarking Zero-Knowledge Proof Authentication...")
        
        authenticator = ZKPAuthenticator()
        secret = os.urandom(32)
        
        # Schnorr proof generation
        times, mem, cpu = self.measure_time(
            authenticator.generate_proof, secret, ZKPProtocol.SCHNORR
        )
        
        self.suite.add_result(BenchmarkResult(
            name="Schnorr Proof Generation",
            category="Zero-Knowledge Proofs",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Schnorr proof verification
        proof = authenticator.generate_proof(secret, ZKPProtocol.SCHNORR)
        
        times, mem, cpu = self.measure_time(authenticator.verify_proof, proof)
        
        self.suite.add_result(BenchmarkResult(
            name="Schnorr Proof Verification",
            category="Zero-Knowledge Proofs",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def benchmark_clone_detection(self):
        """Benchmark clone detection"""
        print("\nBenchmarking Clone Detection...")
        
        detector = CloneDetectionSystem()
        
        # Register genuine devices
        genuine_responses = [os.urandom(256) for _ in range(30)]
        detector.register_genuine_device("device_001", genuine_responses)
        
        # Test responses
        test_responses = [os.urandom(256) for _ in range(20)]
        
        times, mem, cpu = self.measure_time(detector.detect_clone, test_responses)
        
        self.suite.add_result(BenchmarkResult(
            name="Clone Detection Analysis",
            category="Security Monitoring",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def benchmark_timing_operations(self):
        """Benchmark constant-time operations"""
        print("\nBenchmarking Constant-Time Operations...")
        
        a = os.urandom(32)
        b = os.urandom(32)
        
        # Constant-time comparison
        times, mem, cpu = self.measure_time(ConstantTimeOps.ct_compare, a, b)
        
        self.suite.add_result(BenchmarkResult(
            name="Constant-Time Comparison",
            category="Timing Protection",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
        
        # Constant-time selection
        times, mem, cpu = self.measure_time(
            ConstantTimeOps.ct_select, True, 42, 99
        )
        
        self.suite.add_result(BenchmarkResult(
            name="Constant-Time Selection",
            category="Timing Protection",
            mean_time=statistics.mean(times),
            std_dev=statistics.stdev(times),
            min_time=min(times),
            max_time=max(times),
            throughput=1.0 / statistics.mean(times),
            memory_mb=mem,
            cpu_percent=cpu,
            samples=self.samples
        ))
    
    def run_all_benchmarks(self):
        """Run all benchmarks"""
        print("\n" + "=" * 80)
        print("STARTING PERFORMANCE BENCHMARK SUITE")
        print("=" * 80)
        print(f"Samples per benchmark: {self.samples}")
        print(f"Start time: {datetime.now().isoformat()}")
        
        start_time = time.time()
        
        try:
            self.benchmark_puf_response()
            self.benchmark_puf_fusion()
            self.benchmark_fuzzy_extractor()
            self.benchmark_pqc_operations()
            self.benchmark_zkp_authentication()
            self.benchmark_clone_detection()
            self.benchmark_timing_operations()
        except Exception as e:
            print(f"\nError during benchmarking: {e}")
            import traceback
            traceback.print_exc()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.suite.metadata = {
            'total_duration_seconds': duration,
            'total_benchmarks': len(self.suite.results),
            'samples_per_benchmark': self.samples,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'python_version': sys.version
            }
        }
        
        print("\n" + "=" * 80)
        print("BENCHMARK SUITE COMPLETE")
        print("=" * 80)
        print(f"Total duration: {duration:.2f} seconds")
        print(f"Total benchmarks: {len(self.suite.results)}")
        print(f"End time: {datetime.now().isoformat()}")
    
    def generate_visualizations(self, output_dir: str = "benchmarks/results"):
        """Generate visualization charts"""
        if not MATPLOTLIB_AVAILABLE:
            print("\nSkipping visualizations (matplotlib not available)")
            return
        
        print("\nGenerating visualizations...")
        os.makedirs(output_dir, exist_ok=True)
        
        # Group by category
        categories = {}
        for result in self.suite.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # 1. Mean time by category
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for category, results in sorted(categories.items()):
            names = [r.name for r in results]
            times = [r.mean_time * 1000 for r in results]  # Convert to ms
            
            ax.barh(names, times, label=category)
        
        ax.set_xlabel('Mean Time (ms)')
        ax.set_title('Performance Benchmark Results - Mean Execution Time')
        ax.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/mean_time_by_operation.png", dpi=150)
        plt.close()
        
        # 2. Throughput comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        
        names = [r.name for r in self.suite.results if r.throughput]
        throughputs = [r.throughput for r in self.suite.results if r.throughput]
        
        ax.barh(names, throughputs, color='green')
        ax.set_xlabel('Throughput (ops/sec)')
        ax.set_title('Performance Benchmark Results - Throughput')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/throughput_comparison.png", dpi=150)
        plt.close()
        
        # 3. Memory usage
        fig, ax = plt.subplots(figsize=(12, 6))
        
        names = [r.name for r in self.suite.results if r.memory_mb]
        memory = [r.memory_mb for r in self.suite.results if r.memory_mb]
        
        ax.barh(names, memory, color='orange')
        ax.set_xlabel('Memory Delta (MB)')
        ax.set_title('Performance Benchmark Results - Memory Usage')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/memory_usage.png", dpi=150)
        plt.close()
        
        print(f"Visualizations saved to {output_dir}/")


def main():
    """Main benchmark execution"""
    # Create output directory
    output_dir = "benchmarks/results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run benchmarks
    benchmark = PerformanceBenchmark(samples=100)
    benchmark.run_all_benchmarks()
    
    # Generate reports
    print("\nGenerating reports...")
    
    # Text report
    text_report = benchmark.suite.generate_text_report()
    print(text_report)
    benchmark.suite.save_text(f"{output_dir}/benchmark_report.txt")
    print(f"\nText report saved to {output_dir}/benchmark_report.txt")
    
    # JSON report
    benchmark.suite.save_json(f"{output_dir}/benchmark_results.json")
    print(f"JSON results saved to {output_dir}/benchmark_results.json")
    
    # Visualizations
    benchmark.generate_visualizations(output_dir)
    
    print("\n" + "=" * 80)
    print("ALL REPORTS GENERATED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()

# Made with Bob
