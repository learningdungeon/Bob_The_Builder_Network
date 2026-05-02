# 🔒 Secure RAQT Protocol - PUF+PQC Integration

A hardware-rooted, quantum-resistant implementation of the Remote Anonymous Quantum Transmission (RAQT) protocol with Physical Unclonable Functions (PUFs) and NIST-approved Post-Quantum Cryptography.

## 🎯 Overview

This project enhances the RAQT protocol (Christandl-Wehner 2004) with:

- **Hardware Root of Trust**: PUF-based device authentication (SRAM, Ring Oscillator, Arbiter)
- **Post-Quantum Security**: NIST-approved Dilithium and ML-KEM (Kyber)
- **Quantum-Resistant Encryption**: AES-256-GCM with PUF-derived keys
- **Tamper Detection**: Real-time physical security monitoring
- **Anonymous Transmission**: Preserves quantum anonymity properties

## 📋 Features

### 🔐 Security Stack

1. **Physical Unclonable Functions (PUFs)**
   - SRAM PUF: 2048 cells, 256-bit responses, 15% noise tolerance
   - Ring Oscillator PUF: 128 pairs, 100-150 MHz frequency range
   - Arbiter PUF: 64 stages, picosecond-level delay variations
   - Hybrid Fusion: 5 algorithms (weighted average, majority voting, XOR, concatenation, confidence-based)

2. **Error Correction**
   - BCH(255, 131, 18) codes
   - Fuzzy extractor for stable key generation
   - Handles up to 15-20% bit error rate

3. **Post-Quantum Cryptography**
   - CRYSTALS-Dilithium3: Digital signatures (NIST Level 3, 192-bit quantum security)
   - ML-KEM-768 (Kyber): Key encapsulation (NIST Level 3)
   - HKDF-SHA3-256: Key derivation

4. **Classical Encryption**
   - AES-256-GCM: Authenticated encryption
   - PUF-derived session keys
   - Perfect forward secrecy

5. **Tamper Detection**
   - Real-time PUF response monitoring
   - 20% deviation threshold
   - Automatic compromise detection

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "BOB the Builder Quantum Network"

# Install dependencies
pip install -r requirements.txt

# Optional: Install NetSquid (requires license)
# pip install netsquid
```

### Running the Demo (Without NetSquid)

Test the security layer independently:

```bash
python examples/demo_security_layer.py
```

This demonstrates:
- PUF authentication
- Fuzzy extractor key generation
- PQC authentication (Dilithium + ML-KEM)
- AES-256-GCM encryption
- Tamper detection

### Running Full Secure RAQT (With NetSquid)

```bash
python src/raqt/secure_raqt.py
```

This runs the complete protocol with quantum transmission.

## 📁 Project Structure

```
BOB the Builder Quantum Network/
├── src/
│   ├── puf/                    # PUF implementations
│   │   ├── sram_puf.py        # SRAM PUF
│   │   ├── ro_puf.py          # Ring Oscillator PUF
│   │   ├── arbiter_puf.py     # Arbiter PUF
│   │   ├── fusion.py          # Hybrid PUF fusion
│   │   └── fuzzy_extractor.py # BCH error correction
│   ├── crypto/                 # Cryptographic protocols
│   │   └── pqc.py             # PQC (Dilithium + ML-KEM)
│   └── raqt/                   # RAQT protocol
│       └── secure_raqt.py     # Secure RAQT integration
├── examples/
│   └── demo_security_layer.py # Standalone security demo
├── tests/                      # Unit and integration tests
├── docs/                       # Documentation
├── configs/                    # Configuration files
├── benchmarks/                 # Performance benchmarks
├── PUF_RAQT_Architecture_Plan.md  # Complete architecture
├── requirements.txt            # Python dependencies
└── README_SECURE_RAQT.md      # This file
```

## 🔧 Configuration

### Security Levels

```python
from src.raqt.secure_raqt import SecureRAQTProtocol, SecurityLevel

# Choose security level
protocol = SecureRAQTProtocol(
    num_nodes=4,
    security_level=SecurityLevel.HIGH  # LOW, MEDIUM, HIGH, CRITICAL
)
```

### PUF Parameters

```python
from src.puf.sram_puf import SRAMPUF

# Customize PUF parameters
puf = SRAMPUF(
    cell_count=2048,      # Number of SRAM cells
    response_bits=256,    # Response length
    noise_level=0.15      # Noise tolerance (0-1)
)
```

### Fusion Methods

```python
from src.puf.fusion import PUFFusion, FusionMethod

fusion = PUFFusion(
    sram_puf=sram,
    ro_puf=ro,
    arbiter_puf=arbiter,
    fusion_method=FusionMethod.WEIGHTED_AVERAGE,
    weights={'sram': 0.30, 'ro': 0.45, 'arbiter': 0.25}
)
```

## 📊 Performance Metrics

### Typical Performance (on modern CPU)

| Operation | Time | Throughput |
|-----------|------|------------|
| PUF Response Generation | 1-2 ms | - |
| Fuzzy Extractor (Enrollment) | 5-10 ms | - |
| Fuzzy Extractor (Reconstruction) | 5-10 ms | - |
| Dilithium Signing | 2-5 ms | - |
| Dilithium Verification | 1-2 ms | - |
| ML-KEM Encapsulation | 1-3 ms | - |
| AES-256-GCM Encryption | - | 50-100 MB/s |

### Security Properties

| Property | Value |
|----------|-------|
| Quantum Security Level | NIST Level 3 (192-bit) |
| Classical Security | 256-bit AES |
| PUF Reliability | 85-95% |
| PUF Uniqueness | 45-55% |
| Error Correction Capacity | 18 bits (BCH) |
| Tamper Detection Threshold | 20% deviation |

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Benchmarks

```bash
python benchmarks/benchmark_security.py
```

## 📚 Documentation

### Architecture Documentation

See [`PUF_RAQT_Architecture_Plan.md`](PUF_RAQT_Architecture_Plan.md) for:
- Complete system architecture
- Security analysis
- Protocol specifications
- Implementation roadmap
- Mermaid diagrams

### API Documentation

Generate API docs:

```bash
cd docs/
sphinx-build -b html . _build/
```

## 🔬 Research Background

### RAQT Protocol

Based on:
- **Christandl & Wehner (2004)**: "Quantum Anonymous Transmissions"
- Uses GHZ states for anonymous quantum bit transmission
- Preserves sender anonymity through quantum mechanics

### Physical Unclonable Functions

- **SRAM PUF**: Exploits power-up state variations
- **Ring Oscillator PUF**: Uses frequency variations
- **Arbiter PUF**: Leverages delay chain race conditions

### Post-Quantum Cryptography

- **CRYSTALS-Dilithium**: NIST-approved lattice-based signatures
- **ML-KEM (Kyber)**: NIST-approved key encapsulation
- Both provide NIST Level 3 security (192-bit quantum resistance)

## 🛡️ Security Considerations

### Threat Model

Protected against:
- ✅ Quantum computer attacks (Shor's algorithm)
- ✅ Physical cloning attempts
- ✅ Side-channel attacks (constant-time operations)
- ✅ Man-in-the-middle attacks (mutual authentication)
- ✅ Replay attacks (nonces and timestamps)
- ✅ Physical tampering (PUF monitoring)

### Known Limitations

- PUF responses have inherent noise (15-20%)
- Requires secure enrollment phase
- NetSquid simulation vs. real quantum hardware
- Temperature sensitivity of PUFs

## 🤝 Contributing

Contributions welcome! Areas for improvement:

1. Real hardware PUF integration
2. Additional PQC algorithms (SPHINCS+, Falcon)
3. Zero-knowledge proof authentication
4. Machine learning-based PUF modeling resistance
5. Formal security proofs
6. Performance optimizations

## 📄 License

[Specify your license here]

## 📧 Contact

[Your contact information]

## 🙏 Acknowledgments

- NetSquid quantum network simulator
- NIST Post-Quantum Cryptography project
- Christandl & Wehner for RAQT protocol
- PUF research community

## 📖 References

1. Christandl, M., & Wehner, S. (2004). Quantum Anonymous Transmissions. ASIACRYPT 2004.
2. NIST Post-Quantum Cryptography Standardization (2024)
3. Gassend, B., et al. (2002). Silicon Physical Random Functions. CCS 2002.
4. Suh, G. E., & Devadas, S. (2007). Physical Unclonable Functions for Device Authentication and Secret Key Generation. DAC 2007.

---

**Built with ❤️ for quantum-secure communications**