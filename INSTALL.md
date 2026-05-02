# 🚀 Installation Guide - Secure RAQT Protocol

Quick guide to get the Secure RAQT Protocol up and running.

## 📋 Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "BOB the Builder Quantum Network"
```

### 2. Install Core Dependencies

```bash
# Install numpy and cryptography (required)
python -m pip install numpy cryptography

# Or install all dependencies from requirements.txt
python -m pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test the security layer (no NetSquid required)
python examples/demo_security_layer.py
```

You should see output demonstrating:
- ✅ PUF authentication
- ✅ Fuzzy extractor key generation
- ✅ Post-Quantum Cryptography
- ✅ AES-256-GCM encryption
- ✅ Tamper detection

## 🎯 Optional: NetSquid Installation

For full quantum protocol simulation, install NetSquid (requires license):

```bash
# Contact NetSquid team for license and installation instructions
# https://netsquid.org/
```

## 🐛 Troubleshooting

### Issue: `pip` not recognized

**Solution:** Use `python -m pip` instead:
```bash
python -m pip install numpy cryptography
```

### Issue: Permission denied

**Solution:** Install in user directory:
```bash
python -m pip install --user numpy cryptography
```

### Issue: Multiple Python versions

**Solution:** Use specific Python version:
```bash
python3.10 -m pip install numpy cryptography
```

### Issue: Import errors

**Solution:** Ensure you're in the project root directory:
```bash
cd "BOB the Builder Quantum Network"
python examples/demo_security_layer.py
```

## 📦 Package Versions

Tested with:
- `numpy >= 1.24.0`
- `cryptography >= 41.0.0`
- `Python >= 3.10`

## 🔍 Verify Installation

Run this quick test:

```python
# test_install.py
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

print("✅ NumPy version:", np.__version__)
print("✅ Cryptography installed successfully")
print("✅ All dependencies ready!")
```

```bash
python test_install.py
```

## 🚀 Next Steps

After successful installation:

1. **Run the demo:**
   ```bash
   python examples/demo_security_layer.py
   ```

2. **Read the documentation:**
   - [`README_SECURE_RAQT.md`](README_SECURE_RAQT.md) - Main documentation
   - [`PUF_RAQT_Architecture_Plan.md`](PUF_RAQT_Architecture_Plan.md) - Architecture details

3. **Explore the code:**
   - `src/puf/` - PUF implementations
   - `src/crypto/` - PQC protocols
   - `src/raqt/` - Secure RAQT integration

4. **Run tests (when available):**
   ```bash
   pytest tests/ -v
   ```

## 💡 Development Setup

For development work:

```bash
# Install development dependencies
python -m pip install pytest pytest-cov black mypy

# Install documentation tools
python -m pip install sphinx sphinx-rtd-theme

# Install visualization tools
python -m pip install matplotlib seaborn
```

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [README](README_SECURE_RAQT.md)
3. Check Python and package versions
4. Ensure you're in the correct directory

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] pip working (`python -m pip --version`)
- [ ] numpy installed
- [ ] cryptography installed
- [ ] Demo runs successfully
- [ ] No import errors

---

**Ready to secure your quantum network!** 🔒🚀