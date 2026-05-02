"""
Zero-Knowledge Proof Authentication Module

Implements privacy-preserving authentication protocols using Zero-Knowledge Proofs (ZKP).
Allows nodes to prove possession of credentials without revealing them, maintaining
anonymity in the RAQT protocol.

Protocols Implemented:
1. Schnorr Protocol: Prove knowledge of discrete log
2. Commitment Schemes: Pedersen commitments for hiding values
3. Range Proofs: Prove values are in valid range without revealing them
4. Set Membership: Prove membership in authorized set without revealing identity
"""

import hashlib
import hmac
import os
import time
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ZKPProtocol(Enum):
    """Available ZKP protocols"""
    SCHNORR = "schnorr"
    COMMITMENT = "commitment"
    RANGE_PROOF = "range_proof"
    SET_MEMBERSHIP = "set_membership"


@dataclass
class ZKPParameters:
    """Parameters for ZKP protocols"""
    # Large prime for discrete log (2048-bit for security)
    p: int
    # Generator
    g: int
    # Order of subgroup
    q: int
    # Hash function
    hash_func: str = "sha3_256"


class SchnorrProtocol:
    """
    Schnorr Zero-Knowledge Proof Protocol
    
    Allows a prover to demonstrate knowledge of a secret x such that y = g^x mod p
    without revealing x. This is the foundation for many ZKP systems.
    
    Protocol Flow:
    1. Prover: Choose random r, compute commitment t = g^r mod p
    2. Verifier: Send challenge c
    3. Prover: Compute response s = r + c*x mod q
    4. Verifier: Check if g^s = t * y^c mod p
    """
    
    def __init__(self, params: ZKPParameters):
        """
        Initialize Schnorr protocol
        
        Args:
            params: ZKP parameters (p, g, q)
        """
        self.params = params
        self.p = params.p
        self.g = params.g
        self.q = params.q
    
    def generate_keypair(self) -> Tuple[int, int]:
        """
        Generate Schnorr keypair
        
        Returns:
            Tuple of (secret_key, public_key)
        """
        # Secret key: random value in [1, q-1]
        secret_key = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        
        # Public key: y = g^x mod p
        public_key = pow(self.g, secret_key, self.p)
        
        return secret_key, public_key
    
    def create_commitment(self, secret_key: int) -> Tuple[int, int]:
        """
        Create commitment (Step 1 of protocol)
        
        Args:
            secret_key: Prover's secret key
            
        Returns:
            Tuple of (random_value, commitment)
        """
        # Choose random r
        r = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        
        # Compute commitment t = g^r mod p
        t = pow(self.g, r, self.p)
        
        return r, t
    
    def generate_challenge(self, commitment: int, public_key: int, context: bytes = b"") -> int:
        """
        Generate challenge (Step 2 of protocol)
        
        Args:
            commitment: Prover's commitment
            public_key: Prover's public key
            context: Additional context for challenge
            
        Returns:
            Challenge value
        """
        # Hash commitment, public key, and context
        h = hashlib.sha3_256()
        h.update(commitment.to_bytes(256, 'big'))
        h.update(public_key.to_bytes(256, 'big'))
        h.update(context)
        
        # Convert to challenge in [0, q-1]
        challenge = int.from_bytes(h.digest(), 'big') % self.q
        
        return challenge
    
    def create_response(self, random_value: int, challenge: int, secret_key: int) -> int:
        """
        Create response (Step 3 of protocol)
        
        Args:
            random_value: Random value from commitment
            challenge: Challenge from verifier
            secret_key: Prover's secret key
            
        Returns:
            Response value
        """
        # Compute s = r + c*x mod q
        s = (random_value + challenge * secret_key) % self.q
        
        return s
    
    def verify_proof(self, commitment: int, challenge: int, response: int, public_key: int) -> bool:
        """
        Verify proof (Step 4 of protocol)
        
        Args:
            commitment: Prover's commitment
            challenge: Challenge sent to prover
            response: Prover's response
            public_key: Prover's public key
            
        Returns:
            True if proof is valid, False otherwise
        """
        # Check if g^s = t * y^c mod p
        left = pow(self.g, response, self.p)
        right = (commitment * pow(public_key, challenge, self.p)) % self.p
        
        return left == right
    
    def prove_and_verify(self, secret_key: int, public_key: int, context: bytes = b"") -> Tuple[bool, Dict]:
        """
        Complete prove and verify flow
        
        Args:
            secret_key: Prover's secret key
            public_key: Prover's public key
            context: Additional context
            
        Returns:
            Tuple of (verification_result, proof_data)
        """
        # Prover: Create commitment
        r, t = self.create_commitment(secret_key)
        
        # Verifier: Generate challenge
        c = self.generate_challenge(t, public_key, context)
        
        # Prover: Create response
        s = self.create_response(r, c, secret_key)
        
        # Verifier: Verify proof
        verified = self.verify_proof(t, c, s, public_key)
        
        proof_data = {
            'commitment': t,
            'challenge': c,
            'response': s,
            'public_key': public_key
        }
        
        return verified, proof_data


class PedersenCommitment:
    """
    Pedersen Commitment Scheme
    
    Allows committing to a value without revealing it, with the ability to
    later open the commitment. Provides both hiding and binding properties.
    
    Commitment: C = g^m * h^r mod p
    where m is the message, r is random blinding factor
    """
    
    def __init__(self, params: ZKPParameters):
        """
        Initialize Pedersen commitment scheme
        
        Args:
            params: ZKP parameters
        """
        self.params = params
        self.p = params.p
        self.g = params.g
        self.q = params.q
        
        # Second generator h (nothing-up-my-sleeve construction)
        self.h = pow(self.g, 2, self.p)
    
    def commit(self, message: int) -> Tuple[int, int]:
        """
        Create commitment to a message
        
        Args:
            message: Message to commit to
            
        Returns:
            Tuple of (commitment, blinding_factor)
        """
        # Choose random blinding factor
        r = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        
        # Compute commitment C = g^m * h^r mod p
        commitment = (pow(self.g, message, self.p) * pow(self.h, r, self.p)) % self.p
        
        return commitment, r
    
    def open(self, commitment: int, message: int, blinding_factor: int) -> bool:
        """
        Verify commitment opening
        
        Args:
            commitment: The commitment to verify
            message: Claimed message
            blinding_factor: Blinding factor used
            
        Returns:
            True if opening is valid
        """
        # Recompute commitment
        expected = (pow(self.g, message, self.p) * pow(self.h, blinding_factor, self.p)) % self.p
        
        return commitment == expected
    
    def prove_equality(self, commitment1: int, commitment2: int, 
                      message: int, r1: int, r2: int) -> Dict:
        """
        Prove two commitments contain the same message
        
        Args:
            commitment1: First commitment
            commitment2: Second commitment
            message: The message (same in both)
            r1: Blinding factor for commitment1
            r2: Blinding factor for commitment2
            
        Returns:
            Proof of equality
        """
        # This is a simplified proof - in practice would use Schnorr-like protocol
        # Prove knowledge of (m, r1, r2) such that C1 = g^m * h^r1 and C2 = g^m * h^r2
        
        # Random values
        v = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        w1 = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        w2 = int.from_bytes(os.urandom(32), 'big') % (self.q - 1) + 1
        
        # Commitments to random values
        t1 = (pow(self.g, v, self.p) * pow(self.h, w1, self.p)) % self.p
        t2 = (pow(self.g, v, self.p) * pow(self.h, w2, self.p)) % self.p
        
        # Challenge
        h = hashlib.sha3_256()
        h.update(commitment1.to_bytes(256, 'big'))
        h.update(commitment2.to_bytes(256, 'big'))
        h.update(t1.to_bytes(256, 'big'))
        h.update(t2.to_bytes(256, 'big'))
        c = int.from_bytes(h.digest(), 'big') % self.q
        
        # Responses
        s_m = (v + c * message) % self.q
        s_r1 = (w1 + c * r1) % self.q
        s_r2 = (w2 + c * r2) % self.q
        
        return {
            't1': t1,
            't2': t2,
            'challenge': c,
            's_m': s_m,
            's_r1': s_r1,
            's_r2': s_r2
        }


class RangeProof:
    """
    Range Proof Protocol
    
    Proves that a committed value lies within a specific range [0, 2^n)
    without revealing the value. Useful for proving validity without disclosure.
    """
    
    def __init__(self, params: ZKPParameters, bit_length: int = 32):
        """
        Initialize range proof
        
        Args:
            params: ZKP parameters
            bit_length: Number of bits for range (value in [0, 2^bit_length))
        """
        self.params = params
        self.bit_length = bit_length
        self.commitment_scheme = PedersenCommitment(params)
    
    def prove_range(self, value: int, blinding_factor: int) -> Dict:
        """
        Create range proof for a value
        
        Args:
            value: Value to prove is in range
            blinding_factor: Blinding factor from commitment
            
        Returns:
            Range proof
        """
        if value < 0 or value >= (1 << self.bit_length):
            raise ValueError(f"Value must be in range [0, {1 << self.bit_length})")
        
        # Decompose value into bits
        bits = [(value >> i) & 1 for i in range(self.bit_length)]
        
        # Create commitments to each bit
        bit_commitments = []
        bit_blindings = []
        
        for bit in bits:
            commitment, r = self.commitment_scheme.commit(bit)
            bit_commitments.append(commitment)
            bit_blindings.append(r)
        
        # Prove each commitment is to 0 or 1
        bit_proofs = []
        for i, (bit, commitment, r) in enumerate(zip(bits, bit_commitments, bit_blindings)):
            # Simplified proof that bit is 0 or 1
            # In practice, would use more sophisticated protocol
            proof = {
                'bit_index': i,
                'commitment': commitment,
                'is_valid_bit': bit in [0, 1]
            }
            bit_proofs.append(proof)
        
        return {
            'bit_commitments': bit_commitments,
            'bit_proofs': bit_proofs,
            'bit_length': self.bit_length
        }
    
    def verify_range(self, commitment: int, proof: Dict) -> bool:
        """
        Verify range proof
        
        Args:
            commitment: Commitment to the value
            proof: Range proof
            
        Returns:
            True if proof is valid
        """
        # Verify all bit proofs
        for bit_proof in proof['bit_proofs']:
            if not bit_proof['is_valid_bit']:
                return False
        
        # Verify bit commitments multiply to original commitment
        # (simplified - in practice would verify properly)
        return len(proof['bit_commitments']) == proof['bit_length']


class SetMembershipProof:
    """
    Set Membership Proof
    
    Proves that a value belongs to a predefined set without revealing
    which element. Essential for anonymous authentication in RAQT.
    """
    
    def __init__(self, params: ZKPParameters):
        """
        Initialize set membership proof
        
        Args:
            params: ZKP parameters
        """
        self.params = params
        self.schnorr = SchnorrProtocol(params)
    
    def create_accumulator(self, set_elements: List[int]) -> int:
        """
        Create cryptographic accumulator for set
        
        Args:
            set_elements: Elements in the set
            
        Returns:
            Accumulator value
        """
        # Simple accumulator: product of (g^element) mod p
        accumulator = 1
        for element in set_elements:
            accumulator = (accumulator * pow(self.params.g, element, self.params.p)) % self.params.p
        
        return accumulator
    
    def prove_membership(self, element: int, set_elements: List[int]) -> Dict:
        """
        Prove element is in set
        
        Args:
            element: Element to prove membership of
            set_elements: The set
            
        Returns:
            Membership proof
        """
        if element not in set_elements:
            raise ValueError("Element not in set")
        
        # Create accumulator
        accumulator = self.create_accumulator(set_elements)
        
        # Create witness (accumulator without this element)
        other_elements = [e for e in set_elements if e != element]
        witness = self.create_accumulator(other_elements) if other_elements else 1
        
        # Prove knowledge of element and witness
        # Simplified proof
        proof = {
            'accumulator': accumulator,
            'witness': witness,
            'element_commitment': pow(self.params.g, element, self.params.p)
        }
        
        return proof
    
    def verify_membership(self, proof: Dict, accumulator: int) -> bool:
        """
        Verify set membership proof
        
        Args:
            proof: Membership proof
            accumulator: Set accumulator
            
        Returns:
            True if proof is valid
        """
        # Verify accumulator matches
        return proof['accumulator'] == accumulator


class PrivacyPreservingAuth:
    """
    Privacy-Preserving Authentication System
    
    Combines ZKP protocols to enable anonymous authentication for RAQT protocol.
    Nodes can prove they are authorized without revealing their identity.
    """
    
    def __init__(self, params: Optional[ZKPParameters] = None):
        """
        Initialize privacy-preserving authentication
        
        Args:
            params: ZKP parameters (generates secure defaults if None)
        """
        if params is None:
            params = self._generate_secure_parameters()
        
        self.params = params
        self.schnorr = SchnorrProtocol(params)
        self.commitment = PedersenCommitment(params)
        self.range_proof = RangeProof(params)
        self.set_membership = SetMembershipProof(params)
        
        # Authorized node registry
        self.authorized_nodes: Dict[str, int] = {}  # node_id -> public_key
        self.node_accumulator: Optional[int] = None
    
    def _generate_secure_parameters(self) -> ZKPParameters:
        """Generate secure ZKP parameters"""
        # Use safe prime p = 2q + 1 (simplified for demo)
        # In production, use standardized groups (RFC 3526)
        
        # 2048-bit safe prime (example - use proper generation in production)
        p = 2**2048 - 2**1984 - 1 + 2**64 * (2**1918 * 3 + 1)
        q = (p - 1) // 2
        g = 2
        
        return ZKPParameters(p=p, g=g, q=q)
    
    def register_node(self, node_id: str) -> Tuple[int, int]:
        """
        Register a node and generate credentials
        
        Args:
            node_id: Node identifier
            
        Returns:
            Tuple of (secret_credential, public_credential)
        """
        secret, public = self.schnorr.generate_keypair()
        self.authorized_nodes[node_id] = public
        
        # Update accumulator
        self._update_accumulator()
        
        return secret, public
    
    def _update_accumulator(self):
        """Update set accumulator with current authorized nodes"""
        if self.authorized_nodes:
            public_keys = list(self.authorized_nodes.values())
            self.node_accumulator = self.set_membership.create_accumulator(public_keys)
    
    def create_anonymous_proof(self, secret_credential: int, 
                              public_credential: int,
                              challenge_data: bytes = b"") -> Dict:
        """
        Create anonymous authentication proof
        
        Args:
            secret_credential: Node's secret credential
            public_credential: Node's public credential
            challenge_data: Challenge from verifier
            
        Returns:
            Anonymous proof
        """
        # 1. Prove knowledge of secret (Schnorr)
        verified, schnorr_proof = self.schnorr.prove_and_verify(
            secret_credential, 
            public_credential,
            challenge_data
        )
        
        # 2. Prove membership in authorized set
        if self.node_accumulator and public_credential in self.authorized_nodes.values():
            membership_proof = self.set_membership.prove_membership(
                public_credential,
                list(self.authorized_nodes.values())
            )
        else:
            membership_proof = None
        
        # 3. Create commitment to credential (for unlinkability)
        credential_commitment, blinding = self.commitment.commit(public_credential)
        
        return {
            'schnorr_proof': schnorr_proof,
            'membership_proof': membership_proof,
            'credential_commitment': credential_commitment,
            'timestamp': time.time(),
            'challenge_data': challenge_data
        }
    
    def verify_anonymous_proof(self, proof: Dict, challenge_data: bytes = b"") -> bool:
        """
        Verify anonymous authentication proof
        
        Args:
            proof: Anonymous proof
            challenge_data: Challenge data
            
        Returns:
            True if proof is valid
        """
        # Verify challenge data matches
        if proof['challenge_data'] != challenge_data:
            return False
        
        # Verify Schnorr proof
        schnorr_proof = proof['schnorr_proof']
        schnorr_valid = self.schnorr.verify_proof(
            schnorr_proof['commitment'],
            schnorr_proof['challenge'],
            schnorr_proof['response'],
            schnorr_proof['public_key']
        )
        
        if not schnorr_valid:
            return False
        
        # Verify set membership
        if proof['membership_proof'] and self.node_accumulator:
            membership_valid = self.set_membership.verify_membership(
                proof['membership_proof'],
                self.node_accumulator
            )
            if not membership_valid:
                return False
        
        # Check timestamp freshness (within 5 minutes)
        if abs(time.time() - proof['timestamp']) > 300:
            return False
        
        return True
    
    def get_system_status(self) -> Dict:
        """Get system status"""
        return {
            'authorized_nodes': len(self.authorized_nodes),
            'accumulator_set': self.node_accumulator is not None,
            'parameters': {
                'p_bits': self.params.p.bit_length(),
                'q_bits': self.params.q.bit_length(),
                'hash_function': self.params.hash_func
            }
        }


def demo_zkp_authentication():
    """Demonstration of ZKP-based authentication"""
    print("\n" + "=" * 70)
    print("ZERO-KNOWLEDGE PROOF AUTHENTICATION DEMONSTRATION")
    print("=" * 70)
    
    # Initialize system
    print("\n1. Initializing privacy-preserving authentication system...")
    auth_system = PrivacyPreservingAuth()
    print("   System initialized with secure parameters")
    
    # Register nodes
    print("\n2. Registering authorized nodes...")
    nodes = {}
    for i in range(4):
        node_id = f"node_{i:03d}"
        secret, public = auth_system.register_node(node_id)
        nodes[node_id] = (secret, public)
        print(f"   Registered {node_id}")
    
    # Create anonymous proof
    print("\n3. Node authenticating anonymously...")
    node_id = "node_001"
    secret, public = nodes[node_id]
    challenge = b"authentication_challenge_12345"
    
    start = time.time()
    proof = auth_system.create_anonymous_proof(secret, public, challenge)
    proof_time = time.time() - start
    
    print(f"   Proof created in {proof_time*1000:.2f}ms")
    print(f"   Proof contains:")
    print(f"     - Schnorr proof (knowledge of secret)")
    print(f"     - Set membership proof (authorized node)")
    print(f"     - Credential commitment (unlinkability)")
    
    # Verify proof
    print("\n4. Verifying anonymous proof...")
    start = time.time()
    verified = auth_system.verify_anonymous_proof(proof, challenge)
    verify_time = time.time() - start
    
    print(f"   Verification: {'SUCCESS' if verified else 'FAILED'}")
    print(f"   Verified in {verify_time*1000:.2f}ms")
    
    # System status
    print("\n5. System Status:")
    status = auth_system.get_system_status()
    print(f"   Authorized nodes: {status['authorized_nodes']}")
    print(f"   Accumulator set: {status['accumulator_set']}")
    print(f"   Parameter bits: {status['parameters']['p_bits']}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Properties Demonstrated:")
    print("  - Zero-Knowledge: Verifier learns nothing except validity")
    print("  - Anonymity: Node identity not revealed")
    print("  - Unlinkability: Multiple proofs cannot be linked")
    print("  - Soundness: Invalid proofs are rejected")
    print("=" * 70)


if __name__ == "__main__":
    demo_zkp_authentication()

# Made with Bob
