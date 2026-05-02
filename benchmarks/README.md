# Benchmarks

Performance benchmarking suite for the RAQT Quantum Security Framework. Built with IBM BOB.

## Files

| File | Description |
|------|-------------|
| `performance_benchmark.py` | Comprehensive security layer benchmarking |
| `simple_benchmark.py` | Quick lightweight benchmark (PUF + security ops) |
| `results/` | Benchmark output directory (JSON format) |

## Quick Run

# Quick benchmark
```python
python benchmarks/simple_benchmark.py
```
# Full performance benchmark
```python
python benchmarks/performance_benchmark.py
```
# Benchmark Results
```
Performance measurements for the RAQT Quantum Security Framework.
```
## Sample Results

| Operation | Time | Throughput |
|-----------|------|------------|
| SRAM PUF Response | 0.080 ms | 12,428 ops/sec |
| Ring Oscillator PUF Response | 0.480 ms | 2,082 ops/sec |
| Arbiter PUF Response | 0.021 ms | 47,479 ops/sec |
| Clone Detection | 19.110 ms | 52 ops/sec |
| Constant-Time Comparison | 0.001 ms | 1,457,725 ops/sec |

## What's Measured

- **PUF Response Generation**: SRAM, Ring Oscillator, and Arbiter PUF performance
- **Clone Detection**: Statistical PUF analysis throughput
- **Constant-Time Operations**: Timing attack mitigation overhead
- **Fuzzy Extractor**: Enrollment and reconstruction latency
- **PQC Operations**: Dilithium signing/verification, ML-KEM encapsulation

## Notes

- All benchmarks run without external hardware or licenses
- Results are machine-dependent; use for relative comparison only
- Output saved to `benchmarks/results/` as JSON
- Arbiter PUF is fastest for single-bit responses (47K ops/sec)
- Constant-time operations show negligible performance overhead
