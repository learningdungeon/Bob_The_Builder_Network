# Examples

Demonstration scripts for the RAQT Quantum Security Framework. Built with IBM BOB.

## Running the Demos

### AI Security Modules Demo

```bash
python examples/demo_ai_modules.py
```
Demonstrates ML-based eavesdropping detection and PUF modeling attack defense. Includes real-time anomaly scoring, batch analysis, and resilience evaluation for all three PUF types.

## Full Security Layer Demo
```bash
python examples/demo_security_layer.py
```
## End-to-end demonstration of the complete security stack:
PUF authentication, fuzzy extractor key generation, Dilithium signatures, ML-KEM key encapsulation, AES-256-GCM encryption, and tamper detection.

## Files

**File	Purpose**
> demo_ai_modules.py	    AI anomaly detection + PUF modeling defense demo
> demo_security_layer.py	Complete PUF+PQC+AES security stack demo

**What You'll See**
 
**AI Demo Output** 
```
Anomaly Detection: Normal vs attacked RAQT execution comparison
PUF Defense:  SRAM, Ring Oscillator, and Arbiter PUF resilience scoring 
Mitigation Strategies: Automated recommendations per PUF type
Model Export:  Trained model saved for reuse
```
## Security Layer Demo Output
``` 
PUF Authentication: Hybrid fusion response generation
Fuzzy Extractor: Stable key generation from noisy PUF responses
Dilithium: Post-quantum digital signatures
ML-KEM: Post-quantum key encapsulation
AES-256-GCM: Authenticated encryption with session keys
``` 
## Tamper Detection: Real-time monitoring with deviation alerts

**Notes**

All demos run equally well having to incorporate external hardware or formalities

**Dependencies:**
```bash
pip install -r requirements.txt
```
The AI demo generates raqt_anomaly_model.pkl — this is auto-generated and git-ignored

For full RAQT quantum protocol integration, NetSquid license is required (src/raqt/secure_raqt.py)
