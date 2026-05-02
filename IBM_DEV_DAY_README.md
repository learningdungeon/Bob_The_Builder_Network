# Bob The Builder — RAQT Quantum Security Framework

**Built with IBM BOB at the IBM Dev Day BOB Hackathon**

A production-ready quantum security framework combining **Physical Unclonable Functions (PUFs)**, **Post-Quantum Cryptography (PQC)**, and **AI-powered anomaly detection** for the Remote Anonymous Quantum Transmission (RAQT) protocol.

---

## What This Is

This project implements the Christandl-Wehner 2004 quantum anonymous bit transmission protocol, enhanced with a full hardware-to-application security stack:

| Layer | Technology |
|-------|-----------|
| **Quantum Protocol** | RAQT — GHZ-state anonymous bit transmission |
| **Hardware Security** | SRAM, Ring Oscillator, and Arbiter PUFs with hybrid fusion |
| **Post-Quantum Crypto** | CRYSTALS-Dilithium + ML-KEM + HKDF + AES-256-GCM |
| **AI Security** | ML-based eavesdropping detection + PUF modeling attack defense |
| **Authentication** | Zero-knowledge proofs + tamper detection + clone detection |

---

## Built With IBM BOB

Every component of this project was designed, implemented, and debugged using IBM BOB. The BOB session logs in this repository document the full development process — from initial architecture through AI module integration.

**View the BOB session history:**   `bob_sessions/`

---

## Proven on Real Quantum Hardware

- ✅ **IBM Quantum** — 5-qubit system, secret bit = 1 confirmed
- ✅ **Origin Wuyuan** (Chinese quantum computer) — secret bit = 1 confirmed
- ✅ **Noise tolerance:** 97% success at 1% noise, 49% at 50% noise

---

## Quick Start

### What works without any special hardware:

 
**Install dependencies**
```bash
pip install -r requirements.txt
```

**Run the AI security demo**
```bash
python examples/demo_ai_modules.py
```
**Run all tests**
```bash
python -m pytest tests/ -v
```
**Run specific AI tests**
```bash
python -m pytest tests/test_ai_raqt_detector.py tests/test_ai_puf_defense.py -v
```
**What requires NetSquid (quantum network simulator):**

```bash
python src/raqt/secure_raqt.py
``` 

# Project Structure 
``` 
├── src/
│   ├── ai/              # AI anomaly detection + PUF defense
│   ├── auth/            # Zero-knowledge authentication
│   ├── crypto/          # PQC: KEM, KDF, AES, Dilithium, ML-KEM
│   ├── puf/             # SRAM, RO, Arbiter PUFs + fusion + fuzzy extractor
│   ├── raqt/            # Secure RAQT protocol with AI integration
│   └── security/        # Clone detection, timing attack mitigation
├── tests/               # Comprehensive unit tests
├── docs/                # Architecture, threat model, Sentinel Framework alignment
├── examples/            # Demo scripts for AI modules
├── configs/             # YAML configuration for different scenarios
├── benchmarks/          # Performance benchmarking
└── bob_sessions/        # IBM BOB development session logs
```
# Key Documentation

- **Executive Summary:** `EXECUTIVE_SUMMARY.md`
- **Architecture Plan:** `PUF_RAQT_Architecture_Plan.md`
- **Threat Model:** `docs/THREAT_MODEL_AND_SECURITY_ANALYSIS.md`
- **AI Modules Guide:** `docs/SENTINEL_AI_MODULES.md`
- **Sentinel Framework Alignment:** `docs/SENTINEL_FRAMEWORK_ALIGNMENT.md`
- **Installation Guide:** `INSTALL.md`

# Test Results

> AI Anomaly Detector: 24/24 tests passing

> PUF Modeling Defense: 27/28 tests passing (98%)

> PUF & Crypto Modules: Full test suite available

**Total: 51/52 tests passing**

## Hackathon Context

This project was submitted to the IBM Dev Day BOB Hackathon by a solo developer based in Sialkot, Pakistan. The entire codebase was built using IBM BOB as the primary development tool, demonstrating BOB's capability to accelerate complex quantum security research and implementation.

## What BOB helped build:

> 1. PUF simulation framework (3 types + 5 fusion algorithms)

> 2. Post-quantum cryptography integration (Dilithium + ML-KEM)

> 3. AI/ML anomaly detection for quantum networks

> 4. NCQC Sentinel Framework curriculum alignment

> 5. Complete threat model with 54 analyzed scenarios

**Author**
**Noor Ul Ain Faisal**
> IBM Qiskit Advocate
> Friend of OQI (Open Quantum Institute, CERN)
> Member, IEEE GRSS QUEST Technical Committee
> Mentor, Qiskit Advocate Mentorship Program (QAMP)
> Participant, Quantum Internet Alliance (QIA) Foundation Challenge

**License**
MIT License — see LICENSE file.

Built with ❤️ and **IBM BOB** in Sialkot, Pakistan 🇵🇰

