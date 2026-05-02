"""
Sentinel-Integrated AI Modules for RAQT Quantum Security Framework

This package provides machine learning-based security enhancements aligned with
Pakistan's National Center for Quantum Computing (NCQC) Sentinel Framework.

Modules:
    - raqt_anomaly_detector: ML-based eavesdropping detection for RAQT protocol
    - puf_modeling_defense: ML-based protection against PUF modeling attacks

Educational Alignment:
    - BSQC Semester 5: Hardware Root of Trust (PUF Security)
    - BSQC Semester 7: Secure Quantum Networks (RAQT Security)

References:
    - Sentinel Framework (2024): NCQC Curriculum Proposal
    - Christandl-Wehner (2004): Quantum Anonymous Transmission
    - Gassend et al. (2002): Physical Unclonable Functions
"""

from .raqt_anomaly_detector import RAQTAnomalyDetector
from .puf_modeling_defense import PUFModelingDefense

__all__ = [
    'RAQTAnomalyDetector',
    'PUFModelingDefense',
]

__version__ = '1.0.0'
__author__ = 'RAQT Quantum Security Team'
__sentinel_alignment__ = 'NCQC Sentinel Framework 2024'

# Made with Bob
