# Source Code

Core implementation of the RAQT Quantum Security Framework. Built with IBM BOB.

## Architecture
```
src/
├── ai/ # AI-powered security modules
│ ├── raqt_anomaly_detector.py # ML-based eavesdropping detection
│ └── puf_modeling_defense.py # PUF modeling attack defense
├── auth/ # Authentication protocols
│ └── zkp_auth.py # Zero-Knowledge Proof authentication
├── crypto/ # Post-Quantum Cryptography
│ └── pqc.py # Dilithium + ML-KEM + key derivation
├── puf/ # Physical Unclonable Functions
│ ├── sram_puf.py # SRAM startup-state PUF
│ ├── ro_puf.py # Ring Oscillator frequency PUF
│ ├── arbiter_puf.py # Arbiter delay-chain PUF
│ ├── fusion.py # Hybrid PUF fusion (5 methods)
│ └── fuzzy_extractor.py # BCH error correction key extractor
├── raqt/ # Quantum protocol integration
│ └── secure_raqt.py # RAQT + PUF + PQC + AI integration
├── security/ # Hardware security
│ ├── clone_detection.py # PUF-based device fingerprinting
│ └── timing_attack_mitigation.py # Constant-time operations
└── utils/ # Utilities (reserved for future use)
```

## Module Details

### AI (`src/ai/`)
- **Anomaly Detector**: Isolation Forest model extracting 16 security features from RAQT protocol executions. Detects biased XOR patterns, elevated error rates, basis choice bias, and timing anomalies.
- **PUF Defense**: Evaluates PUF resilience against 4 ML attack types (Random Forest, Gradient Boosting, SVM, Neural Network). Generates automated mitigation strategies.

### PUF (`src/puf/`)
- Three PUF implementations with configurable noise, temperature sensitivity, and device parameters
- Five fusion algorithms: Majority Voting, Weighted Average, Concatenation, XOR Fusion, Confidence-Based
- BCH(255, 131, 18) fuzzy extractor for stable key generation from noisy PUF responses

### Cryptography (`src/crypto/`)
- CRYSTALS-Dilithium signature scheme (NIST PQC Standard)
- ML-KEM key encapsulation (NIST PQC Standard)
- HKDF-based key derivation from PUF seeds
- Simulated for demonstration; production deployment uses liboqs

### Authentication (`src/auth/`)
- Schnorr-based Zero-Knowledge Proofs
- Set membership proofs for anonymous node authentication
- Unlinkable credentials with accumulator-based revocation

### Security (`src/security/`)
- Statistical clone detection using PUF response analysis
- Constant-time comparison, selection, and blinding operations
- Timing attack vulnerability assessment

## Quick Start

**AI Anomaly Detection**
```python
from src.ai.raqt_anomaly_detector import RAQTAnomalyDetector
```
**PUF Modeling Defense**
```python
from src.ai.puf_modeling_defense import PUFModelingDefense
```
**Hybrid PUF**
```bash
from src.puf.fusion import PUFFusion, FusionMethod
```
**PQC Authentication**
```bash
from src.crypto.pqc import PQCAuthenticationProtocol
```
**Dependencies**
```bash
pip install -r requirements.txt
```
**Key dependencies:** 
> numpy, scikit-learn, cryptography

**Notes**
> All PQC implementations are simulated for demonstration

**The RAQT integration (src/raqt/secure_raqt.py) requires NetSquid license for quantum simulation**

All other modules run without external hardware or licenses
