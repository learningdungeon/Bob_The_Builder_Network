"""
Comprehensive Test Runner and Validation Script

Runs all tests and provides detailed validation report for the security layer.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import Dict, List, Tuple
import traceback


class TestRunner:
    """Comprehensive test runner for security layer validation"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'errors': []
        }
        self.start_time = None
        self.end_time = None
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record result"""
        try:
            print(f"\n  Running: {test_name}...", end=" ")
            start = time.time()
            test_func()
            duration = time.time() - start
            print(f"✅ PASS ({duration*1000:.2f}ms)")
            self.results['passed'].append((test_name, duration))
            return True
        except AssertionError as e:
            print(f"❌ FAIL")
            self.results['failed'].append((test_name, str(e)))
            return False
        except Exception as e:
            print(f"⚠️  ERROR")
            self.results['errors'].append((test_name, str(e), traceback.format_exc()))
            return False
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['errors'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        errors = len(self.results['errors'])
        
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/max(1,total)*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/max(1,total)*100:.1f}%)")
        print(f"⚠️  Errors: {errors} ({errors/max(1,total)*100:.1f}%)")
        print(f"\n⏱️  Total Time: {duration:.2f}s")
        
        if self.results['failed']:
            print("\n" + "-" * 70)
            print("FAILED TESTS:")
            for name, reason in self.results['failed']:
                print(f"\n  ❌ {name}")
                print(f"     Reason: {reason}")
        
        if self.results['errors']:
            print("\n" + "-" * 70)
            print("ERROR TESTS:")
            for name, error, trace in self.results['errors']:
                print(f"\n  ⚠️  {name}")
                print(f"     Error: {error}")
        
        print("\n" + "=" * 70)
        
        return passed == total


def test_puf_basic_functionality():
    """Test basic PUF functionality"""
    from src.puf.sram_puf import SRAMPUF
    from src.puf.ro_puf import RingOscillatorPUF
    from src.puf.arbiter_puf import ArbiterPUF
    
    # Test SRAM PUF
    sram = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    response = sram.generate_response()
    assert len(response) == 256, "SRAM PUF response length incorrect"
    
    # Test RO PUF
    ro = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
    response = ro.generate_response()
    assert len(response) == 128, "RO PUF response length incorrect"
    
    # Test Arbiter PUF
    arbiter = ArbiterPUF(delay_stages=64, noise_level=0.11)
    response = arbiter.generate_response(challenge=0x123456789ABCDEF0)
    assert isinstance(response, (bytes, int)), "Arbiter PUF response type incorrect"


def test_puf_reliability():
    """Test PUF reliability measurements"""
    from src.puf.sram_puf import SRAMPUF
    
    puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    reliability = puf.measure_reliability(num_trials=30)
    
    assert 0.0 <= reliability <= 1.0, "Reliability out of range"
    assert reliability > 0.70, f"Reliability too low: {reliability}"


def test_puf_fusion():
    """Test PUF fusion functionality"""
    from src.puf.sram_puf import SRAMPUF
    from src.puf.ro_puf import RingOscillatorPUF
    from src.puf.arbiter_puf import ArbiterPUF
    from src.puf.fusion import PUFFusion, FusionMethod
    
    sram = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    ro = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
    arbiter = ArbiterPUF(delay_stages=64, noise_level=0.11)
    
    fusion = PUFFusion(
        sram_puf=sram,
        ro_puf=ro,
        arbiter_puf=arbiter,
        fusion_method=FusionMethod.WEIGHTED_AVERAGE
    )
    
    response = fusion.generate_response()
    assert isinstance(response, bytes), "Fusion response type incorrect"
    assert len(response) > 0, "Fusion response empty"


def test_fuzzy_extractor():
    """Test fuzzy extractor key generation"""
    from src.puf.sram_puf import SRAMPUF
    from src.puf.fuzzy_extractor import FuzzyExtractor
    
    puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    extractor = FuzzyExtractor(response_length=256, key_length=256)
    
    # Generate key
    response = puf.generate_response()
    stable_key, helper_data = extractor.generate(response)
    
    assert len(stable_key) == 256, "Stable key length incorrect"
    assert isinstance(helper_data, dict), "Helper data type incorrect"
    
    # Test reproduction
    noisy_response = puf.generate_response()
    reproduced_key, success, errors = extractor.reproduce(noisy_response, helper_data)
    
    assert success, "Key reproduction failed"
    assert stable_key == reproduced_key, "Reproduced key doesn't match"


def test_pqc_key_derivation():
    """Test PQC key derivation"""
    from src.crypto.pqc import PQCKeyDerivation
    
    puf_seed = os.urandom(32)
    kdf = PQCKeyDerivation()
    
    # Test key derivation methods
    dilithium_seed = kdf.derive_key(b"dilithium", 32)
    mlkem_seed = kdf.derive_key(b"mlkem", 32)
    
    assert len(dilithium_seed) == 32, "Dilithium seed length incorrect"
    assert len(mlkem_seed) == 32, "ML-KEM seed length incorrect"
    assert dilithium_seed != mlkem_seed, "Seeds should be different"


def test_pqc_authentication():
    """Test PQC authentication protocol"""
    from src.crypto.pqc import PQCAuthenticationProtocol
    
    puf_seed = os.urandom(32)
    protocol = PQCAuthenticationProtocol(node_id="test_node", puf_seed=puf_seed)
    
    # Test public key generation
    public_keys = protocol.get_public_keys()
    assert 'dilithium' in public_keys, "Dilithium public key missing"
    assert 'mlkem' in public_keys, "ML-KEM public key missing"
    
    # Test authentication
    challenge = os.urandom(32)
    auth_response = protocol.authenticate(challenge)
    assert 'signature' in auth_response, "Signature missing from auth response"


def test_mutual_authentication():
    """Test mutual authentication between nodes"""
    from src.crypto.pqc import PQCAuthenticationProtocol
    
    # Create two nodes
    node_a = PQCAuthenticationProtocol(node_id="node_a", puf_seed=os.urandom(32))
    node_b = PQCAuthenticationProtocol(node_id="node_b", puf_seed=os.urandom(32))
    
    # Get public keys
    pk_a = node_a.get_public_keys()
    pk_b = node_b.get_public_keys()
    
    # Node A authenticates to Node B
    challenge_a = os.urandom(32)
    auth_a = node_a.authenticate(challenge_a)
    verified_a = node_b.verify_authentication(auth_a, challenge_a, pk_a['dilithium'])
    
    # Node B authenticates to Node A
    challenge_b = os.urandom(32)
    auth_b = node_b.authenticate(challenge_b)
    verified_b = node_a.verify_authentication(auth_b, challenge_b, pk_b['dilithium'])
    
    assert verified_a, "Node A authentication failed"
    assert verified_b, "Node B authentication failed"


def test_session_establishment():
    """Test session key establishment"""
    from src.crypto.pqc import PQCAuthenticationProtocol
    
    node_a = PQCAuthenticationProtocol(node_id="node_a", puf_seed=os.urandom(32))
    node_b = PQCAuthenticationProtocol(node_id="node_b", puf_seed=os.urandom(32))
    
    pk_b = node_b.get_public_keys()
    
    # Establish session
    ciphertext = node_a.establish_session(pk_b['mlkem'])
    session_key = node_a.get_session_key()
    
    assert isinstance(ciphertext, bytes), "Ciphertext type incorrect"
    assert isinstance(session_key, bytes), "Session key type incorrect"
    assert len(session_key) == 32, "Session key length incorrect"


def test_aes_encryption():
    """Test AES-256-GCM encryption"""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import hashlib
    
    # Generate session key
    session_key = os.urandom(32)
    aes_key = hashlib.sha256(session_key).digest()
    aesgcm = AESGCM(aes_key)
    
    # Test encryption/decryption
    plaintext = b"Test message for encryption"
    nonce = os.urandom(12)
    
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    
    assert decrypted == plaintext, "Decryption failed"


def test_tamper_detection():
    """Test tamper detection functionality"""
    from src.puf.sram_puf import SRAMPUF
    from src.puf.ro_puf import RingOscillatorPUF
    from src.puf.arbiter_puf import ArbiterPUF
    from src.puf.fusion import PUFFusion, FusionMethod
    
    sram = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    ro = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
    arbiter = ArbiterPUF(delay_stages=64, noise_level=0.11)
    
    fusion = PUFFusion(
        sram_puf=sram,
        ro_puf=ro,
        arbiter_puf=arbiter,
        fusion_method=FusionMethod.WEIGHTED_AVERAGE
    )
    
    # Get baseline
    baseline = fusion.generate_response()
    
    # Normal operation
    current = fusion.generate_response()
    hamming_dist = sum(b1 != b2 for b1, b2 in zip(baseline, current))
    deviation = hamming_dist / len(baseline)
    
    assert deviation < 0.30, f"Normal deviation too high: {deviation}"
    
    # Simulate tampering
    sram.noise_level = 0.40
    tampered = fusion.generate_response()
    hamming_dist_tampered = sum(b1 != b2 for b1, b2 in zip(baseline, tampered))
    deviation_tampered = hamming_dist_tampered / len(baseline)
    
    assert deviation_tampered > 0.20, "Tamper detection failed"


def test_complete_security_stack():
    """Test complete security stack integration"""
    from src.puf.sram_puf import SRAMPUF
    from src.puf.ro_puf import RingOscillatorPUF
    from src.puf.arbiter_puf import ArbiterPUF
    from src.puf.fusion import PUFFusion, FusionMethod
    from src.puf.fuzzy_extractor import FuzzyExtractor
    from src.crypto.pqc import PQCAuthenticationProtocol
    
    # 1. Generate PUF response
    sram = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
    ro = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
    arbiter = ArbiterPUF(delay_stages=64, noise_level=0.11)
    
    fusion = PUFFusion(
        sram_puf=sram,
        ro_puf=ro,
        arbiter_puf=arbiter,
        fusion_method=FusionMethod.WEIGHTED_AVERAGE
    )
    
    puf_response = fusion.generate_response()
    
    # 2. Extract stable key
    extractor = FuzzyExtractor(response_length=len(puf_response), key_length=256)
    stable_key, helper_data = extractor.generate(puf_response)
    
    # 3. Initialize PQC protocol
    protocol = PQCAuthenticationProtocol(node_id="test_node", puf_seed=stable_key)
    
    # 4. Test authentication
    challenge = os.urandom(32)
    auth_response = protocol.authenticate(challenge)
    public_keys = protocol.get_public_keys()
    verified = protocol.verify_authentication(auth_response, challenge, public_keys['dilithium'])
    
    assert verified, "Complete stack authentication failed"


def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("SECURE RAQT PROTOCOL - VALIDATION TEST SUITE")
    print("=" * 70)
    print("\nRunning comprehensive validation tests...")
    
    runner = TestRunner()
    runner.start_time = time.time()
    
    # Define all tests
    tests = [
        ("PUF Basic Functionality", test_puf_basic_functionality),
        ("PUF Reliability", test_puf_reliability),
        ("PUF Fusion", test_puf_fusion),
        ("Fuzzy Extractor", test_fuzzy_extractor),
        ("PQC Key Derivation", test_pqc_key_derivation),
        ("PQC Authentication", test_pqc_authentication),
        ("Mutual Authentication", test_mutual_authentication),
        ("Session Establishment", test_session_establishment),
        ("AES Encryption", test_aes_encryption),
        ("Tamper Detection", test_tamper_detection),
        ("Complete Security Stack", test_complete_security_stack),
    ]
    
    # Run all tests
    print("\n📋 Test Categories:")
    for test_name, test_func in tests:
        runner.run_test(test_name, test_func)
    
    runner.end_time = time.time()
    
    # Print summary
    all_passed = runner.print_summary()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Security layer validated successfully.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
