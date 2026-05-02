# Configuration Files

This directory contains configuration files for different deployment scenarios of the RAQT Quantum Network with PUF+PQC security layer.

## Available Configurations

### 1. `default.yaml` - Base Configuration
The default configuration that serves as the foundation for all other configurations. Contains balanced settings suitable for general use.

**Use Case:** Starting point for custom configurations

**Key Features:**
- Standard PUF parameters (SRAM: 2048 cells, RO: 128 pairs, Arbiter: 64 stages)
- NIST Level 3 PQC (Dilithium3, ML-KEM-768)
- Balanced security and performance
- All monitoring features enabled

---

### 2. `development.yaml` - Development Environment
Optimized for local development and debugging with relaxed security settings and verbose logging.

**Use Case:** Local development, debugging, rapid iteration

**Key Features:**
- Reduced PUF complexity for faster generation
- Lower security levels for faster operations (Dilithium2, ML-KEM-512)
- DEBUG logging level
- Relaxed monitoring thresholds
- Experimental features enabled
- Longer timeouts for debugging

**Performance:**
- SRAM PUF: 1024 cells, 128 bits
- RO PUF: 64 pairs, 64 bits
- Arbiter PUF: 32 stages, 32 bits

---

### 3. `production.yaml` - Production Deployment
Maximum security and reliability for production environments with strict monitoring and high availability features.

**Use Case:** Production deployment, critical infrastructure

**Key Features:**
- Maximum PUF complexity (SRAM: 4096 cells, RO: 256 pairs, Arbiter: 128 stages)
- Highest security level (Dilithium5, ML-KEM-1024, SHA3-512)
- Frequent key rotation (30 minutes)
- Strict monitoring thresholds
- WARNING-level logging only
- High availability and rate limiting
- Audit logging enabled
- Automated backups

**Security:**
- 256-bit quantum security
- Pedersen commitment ZKP
- 512-bit challenges
- All clone detection methods

---

### 4. `testing.yaml` - Automated Testing
Optimized for CI/CD pipelines and automated testing with minimal complexity and deterministic behavior.

**Use Case:** Unit tests, integration tests, CI/CD pipelines

**Key Features:**
- Minimal PUF parameters for fast execution
- Low noise levels for predictable results
- Deterministic mode with fixed seed (42)
- Single retry attempt
- Relaxed monitoring
- Test data generation
- Coverage tracking (80% minimum)

**Performance:**
- SRAM PUF: 512 cells, 64 bits
- RO PUF: 32 pairs, 32 bits
- Arbiter PUF: 16 stages, 16 bits
- No retries, fast timeouts

---

### 5. `research.yaml` - Academic Research
Comprehensive configuration for academic research with full data collection, statistical analysis, and experimental features.

**Use Case:** Academic research, experiments, parameter studies

**Key Features:**
- Standard parameters with full configurability
- All experimental features enabled
- Comprehensive data collection (CSV output)
- Statistical analysis (95% confidence, 1000 samples)
- Visualization generation (PNG, PDF, SVG)
- Experiment tracking and metadata
- Parameter sweep support
- Reproducibility controls

**Research Tools:**
- Automated metric collection
- Bootstrap analysis (10,000 iterations)
- Version control integration
- Random state saving
- Parameter exploration

---

## Configuration Structure

All configuration files follow this structure:

```yaml
version: "1.0"
environment: "<environment_name>"
extends: "default.yaml"  # Optional inheritance

network:
  protocol: "RAQT"
  quantum_channel: {...}
  classical_channel: {...}

puf:
  sram: {...}
  ro: {...}
  arbiter: {...}
  fusion: {...}
  fuzzy_extractor: {...}

pqc:
  dilithium: {...}
  mlkem: {...}
  hkdf: {...}

encryption: {...}
authentication: {...}
monitoring: {...}
logging: {...}
performance: {...}
experimental: {...}
```

---

## Usage

### Loading a Configuration

```python
import yaml

# Load configuration
with open('configs/production.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access settings
puf_config = config['puf']['sram']
security_level = config['pqc']['dilithium']['security_level']
```

### Environment Variable Override

Set the configuration file via environment variable:

```bash
export RAQT_CONFIG=configs/production.yaml
python main.py
```

### Command Line Override

```bash
python main.py --config configs/development.yaml
```

---

## Configuration Parameters

### PUF Parameters

| Parameter | Development | Testing | Default | Production | Research |
|-----------|-------------|---------|---------|------------|----------|
| SRAM cells | 1024 | 512 | 2048 | 4096 | 2048 |
| SRAM bits | 128 | 64 | 256 | 512 | 256 |
| RO pairs | 64 | 32 | 128 | 256 | 128 |
| Arbiter stages | 32 | 16 | 64 | 128 | 64 |
| Noise level | Low | Very Low | Medium | Medium | Medium |

### PQC Security Levels

| Level | Quantum Security | Classical Security | Algorithms |
|-------|------------------|-------------------|------------|
| 2 | 128-bit | 128-bit | Dilithium2, ML-KEM-512 |
| 3 | 192-bit | 192-bit | Dilithium3, ML-KEM-768 |
| 5 | 256-bit | 256-bit | Dilithium5, ML-KEM-1024 |

### Monitoring Thresholds

| Metric | Development | Testing | Default | Production |
|--------|-------------|---------|---------|------------|
| Tamper threshold | 30% | 50% | 20% | 15% |
| Inter-HD | 45% | 40% | 50% | 50% |
| Intra-HD | 20% | 25% | 15% | 12% |
| Entropy | 6.0 | 5.0 | 7.0 | 7.5 |

---

## Creating Custom Configurations

### Method 1: Extend Existing Configuration

```yaml
version: "1.0"
environment: "custom"
extends: "default.yaml"

# Override specific settings
puf:
  sram:
    cell_count: 3000
    noise_level: 0.12

logging:
  level: "INFO"
```

### Method 2: Complete Custom Configuration

Copy `default.yaml` and modify all parameters as needed.

---

## Best Practices

1. **Development**: Use `development.yaml` for local work
2. **Testing**: Use `testing.yaml` in CI/CD pipelines
3. **Staging**: Create custom config based on `production.yaml` with relaxed settings
4. **Production**: Use `production.yaml` with environment-specific overrides
5. **Research**: Use `research.yaml` and document all parameter changes

---

## Security Considerations

### Production Deployment Checklist

- [ ] Use `production.yaml` as base
- [ ] Enable all monitoring features
- [ ] Set appropriate rate limits
- [ ] Configure audit logging
- [ ] Enable automated backups
- [ ] Use strong key rotation policy
- [ ] Disable experimental features
- [ ] Set strict timeouts
- [ ] Enable high availability
- [ ] Review all thresholds

### Development Safety

- [ ] Never use production keys in development
- [ ] Keep development configs separate
- [ ] Use lower security levels for speed
- [ ] Enable verbose logging
- [ ] Use longer timeouts for debugging

---

## Troubleshooting

### Configuration Not Loading

```bash
# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('configs/your_config.yaml'))"
```

### Performance Issues

- Reduce PUF complexity (cell_count, pairs, stages)
- Lower security levels (2 instead of 3 or 5)
- Increase timeouts
- Disable unnecessary monitoring

### Security Warnings

- Check monitoring thresholds
- Verify PQC security levels
- Review key rotation intervals
- Ensure all protection features enabled

---

## Version History

- **v1.0** (2026-05): Initial release with 5 configurations
  - default.yaml
  - development.yaml
  - production.yaml
  - testing.yaml
  - research.yaml

---

## Support

For questions or issues with configurations:
1. Check this README
2. Review the threat model documentation
3. Consult the main project README
4. Open an issue on the project repository

---

**Last Updated:** May 2026  
**Maintainer:** RAQT Security Team