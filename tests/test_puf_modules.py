"""
Unit Tests for PUF Modules

Tests SRAM PUF, Ring Oscillator PUF, and Arbiter PUF implementations.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.puf.sram_puf import SRAMPUF
from src.puf.ro_puf import RingOscillatorPUF
from src.puf.arbiter_puf import ArbiterPUF


class TestSRAMPUF:
    """Test cases for SRAM PUF implementation"""
    
    def test_initialization(self):
        """Test SRAM PUF initialization"""
        puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
        assert puf.cell_count == 2048
        assert puf.response_bits == 256
        assert puf.noise_level == 0.15
    
    def test_response_generation(self):
        """Test PUF response generation"""
        puf = SRAMPUF(cell_count=2048, response_bits=256)
        response = puf.generate_response()
        
        assert isinstance(response, bytes)
        assert len(response) == 256
    
    def test_response_consistency(self):
        """Test that same PUF generates consistent responses"""
        puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.0)
        
        response1 = puf.generate_response()
        response2 = puf.generate_response()
        
        # With zero noise, responses should be identical
        assert response1 == response2
    
    def test_response_with_noise(self):
        """Test that noise introduces variations"""
        puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
        
        response1 = puf.generate_response()
        response2 = puf.generate_response()
        
        # Calculate Hamming distance
        hamming_dist = sum(b1 != b2 for b1, b2 in zip(response1, response2))
        deviation = hamming_dist / len(response1)
        
        # Should have some noise but not too much
        assert 0.05 < deviation < 0.25
    
    def test_reliability_measurement(self):
        """Test reliability measurement"""
        puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
        reliability = puf.measure_reliability(num_trials=50)
        
        assert 0.0 <= reliability <= 1.0
        assert reliability > 0.75  # Should be reasonably reliable
    
    def test_uniqueness_measurement(self):
        """Test uniqueness measurement"""
        puf = SRAMPUF(cell_count=2048, response_bits=256)
        uniqueness = puf.measure_uniqueness(num_devices=10)
        
        assert 0.0 <= uniqueness <= 1.0
        assert uniqueness > 0.35  # Should be reasonably unique
    
    def test_entropy_estimation(self):
        """Test entropy estimation"""
        puf = SRAMPUF(cell_count=2048, response_bits=256)
        entropy = puf.estimate_entropy(num_samples=100)
        
        assert entropy > 0.5  # Should have reasonable entropy
    
    def test_temperature_effect(self):
        """Test temperature effect on responses"""
        puf = SRAMPUF(cell_count=2048, response_bits=256, noise_level=0.15)
        
        response_25c = puf.generate_response(temperature=25.0)
        response_50c = puf.generate_response(temperature=50.0)
        
        # Higher temperature should introduce more variation
        hamming_dist = sum(b1 != b2 for b1, b2 in zip(response_25c, response_50c))
        assert hamming_dist > 0


class TestRingOscillatorPUF:
    """Test cases for Ring Oscillator PUF implementation"""
    
    def test_initialization(self):
        """Test Ring Oscillator PUF initialization"""
        puf = RingOscillatorPUF(
            oscillator_pairs=128,
            frequency_range=(100e6, 150e6),
            noise_level=0.08
        )
        assert puf.oscillator_pairs == 128
        assert puf.frequency_range == (100e6, 150e6)
        assert puf.noise_level == 0.08
    
    def test_response_generation(self):
        """Test PUF response generation"""
        puf = RingOscillatorPUF(oscillator_pairs=128)
        response = puf.generate_response()
        
        assert isinstance(response, bytes)
        assert len(response) == 128
    
    def test_response_consistency(self):
        """Test response consistency"""
        puf = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.0)
        
        response1 = puf.generate_response()
        response2 = puf.generate_response()
        
        assert response1 == response2
    
    def test_reliability_measurement(self):
        """Test reliability measurement"""
        puf = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
        reliability = puf.measure_reliability(num_trials=50)
        
        assert 0.0 <= reliability <= 1.0
        assert reliability > 0.85  # RO-PUF should be very reliable
    
    def test_temperature_voltage_effects(self):
        """Test temperature and voltage effects"""
        puf = RingOscillatorPUF(oscillator_pairs=128, noise_level=0.08)
        
        response_normal = puf.generate_response(temperature=25.0, voltage=1.0)
        response_hot = puf.generate_response(temperature=50.0, voltage=1.0)
        response_low_v = puf.generate_response(temperature=25.0, voltage=0.9)
        
        # Different conditions should produce some variation
        assert response_normal != response_hot or response_normal != response_low_v


class TestArbiterPUF:
    """Test cases for Arbiter PUF implementation"""
    
    def test_initialization(self):
        """Test Arbiter PUF initialization"""
        puf = ArbiterPUF(delay_stages=64, delay_variation=1e-12, noise_level=0.11)
        assert puf.delay_stages == 64
        assert puf.delay_variation == 1e-12
        assert puf.noise_level == 0.11
    
    def test_response_generation(self):
        """Test PUF response generation"""
        puf = ArbiterPUF(delay_stages=64)
        challenge = 0x123456789ABCDEF0
        response = puf.generate_response(challenge=challenge)
        
        assert isinstance(response, bytes)
        assert len(response) == 64
    
    def test_challenge_response_pairs(self):
        """Test different challenges produce different responses"""
        puf = ArbiterPUF(delay_stages=64, noise_level=0.0)
        
        challenge1 = 0x1111111111111111
        challenge2 = 0x2222222222222222
        
        response1 = puf.generate_response(challenge=challenge1)
        response2 = puf.generate_response(challenge=challenge2)
        
        # Different challenges should produce different responses
        assert response1 != response2
    
    def test_response_consistency_same_challenge(self):
        """Test same challenge produces consistent response"""
        puf = ArbiterPUF(delay_stages=64, noise_level=0.0)
        challenge = 0x123456789ABCDEF0
        
        response1 = puf.generate_response(challenge=challenge)
        response2 = puf.generate_response(challenge=challenge)
        
        assert response1 == response2
    
    def test_reliability_measurement(self):
        """Test reliability measurement"""
        puf = ArbiterPUF(delay_stages=64, noise_level=0.11)
        reliability = puf.measure_reliability(num_trials=50)
        
        assert 0.0 <= reliability <= 1.0
        assert reliability > 0.80
    
    def test_challenge_space(self):
        """Test large challenge space"""
        puf = ArbiterPUF(delay_stages=64)
        
        # Test multiple random challenges
        challenges = [os.urandom(8) for _ in range(10)]
        responses = [puf.generate_response(challenge=int.from_bytes(c, 'big')) 
                    for c in challenges]
        
        # All responses should be different
        assert len(set(responses)) == len(responses)


class TestPUFIntegration:
    """Integration tests for PUF modules"""
    
    def test_all_pufs_generate_responses(self):
        """Test that all PUF types can generate responses"""
        sram = SRAMPUF(cell_count=2048, response_bits=256)
        ro = RingOscillatorPUF(oscillator_pairs=128)
        arbiter = ArbiterPUF(delay_stages=64)
        
        sram_response = sram.generate_response()
        ro_response = ro.generate_response()
        arbiter_response = arbiter.generate_response()
        
        assert len(sram_response) == 256
        assert len(ro_response) == 128
        assert len(arbiter_response) == 64
    
    def test_puf_uniqueness_across_types(self):
        """Test that different PUF types produce unique responses"""
        sram = SRAMPUF(cell_count=2048, response_bits=256)
        ro = RingOscillatorPUF(oscillator_pairs=128)
        
        # Generate multiple responses
        sram_responses = [sram.generate_response() for _ in range(5)]
        ro_responses = [ro.generate_response() for _ in range(5)]
        
        # Each type should have unique responses
        assert len(set(sram_responses)) > 1
        assert len(set(ro_responses)) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
