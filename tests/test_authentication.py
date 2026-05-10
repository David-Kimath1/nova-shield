import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.multi_factor_auth import MultiFactorAuthenticator
from core.threat_engine import ThreatEngine, ThreatLevel
from core.continuous_verification import ContinuousVerifier

class TestAuthentication(unittest.TestCase):
    
    def test_multi_factor_score(self):
        mfa = MultiFactorAuthenticator()
        result = mfa.compute_trust_score({
            'face_match': {'confidence': 0.92},
            'typing_timings': [0.1, 0.12, 0.11, 0.13]
        })
        self.assertGreater(result['final_score'], 0.5)
        self.assertIn(result['trust_level'], ['TRUSTED', 'SUSPICIOUS', 'HIGH_RISK'])
        
    def test_threat_levels(self):
        threat = ThreatEngine()
        
        # Test green level
        threat.update_threat({'unknown_face': False, 'spoof_attempt': False})
        self.assertEqual(threat.current_level, ThreatLevel.GREEN)
        
        # Test red level
        threat.update_threat({'unknown_face': True, 'spoof_attempt': True})
        self.assertEqual(threat.current_level, ThreatLevel.RED)
        
    def test_continuous_verification(self):
        verifier = ContinuousVerifier(interval_seconds=1)
        
        # Initial verification
        result = verifier.verify(0.95, True)
        self.assertTrue(result['trusted'])
        
        # Simulate time passing
        import time
        time.sleep(1.1)
        
        # Re-verification
        result = verifier.verify(0.95, True)
        self.assertTrue(result['trusted'])

if __name__ == '__main__':
    unittest.main()
