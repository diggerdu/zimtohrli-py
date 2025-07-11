#!/usr/bin/env python3
"""
Simple test script to verify the package installs and works correctly.
"""

import sys
import numpy as np

try:
    import zimtohrli_py as zimtohrli
    print("✓ Successfully imported zimtohrli_py")
except ImportError as e:
    print(f"✗ Failed to import zimtohrli_py: {e}")
    sys.exit(1)

def main():
    """Run basic functionality tests."""
    print("Testing Zimtohrli Python Package Installation")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print("Test 1: Basic audio comparison...")
    try:
        # Generate test signals
        sample_rate = 48000
        duration = 0.1  # Short test
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        audio_a = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        audio_b = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # Test MOS
        mos = zimtohrli.compare_audio(audio_a, sample_rate, audio_b, sample_rate)
        print(f"  MOS score: {mos:.3f}")
        
        # Test distance
        distance = zimtohrli.compare_audio(audio_a, sample_rate, audio_b, sample_rate, return_distance=True)
        print(f"  Distance: {distance:.6f}")
        
        assert 1 <= mos <= 5, f"MOS out of range: {mos}"
        assert 0 <= distance <= 1, f"Distance out of range: {distance}"
        print("  ✓ PASS")
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    # Test 2: ZimtohrliComparator
    print("\nTest 2: ZimtohrliComparator class...")
    try:
        comparator = zimtohrli.ZimtohrliComparator()
        print(f"  Sample rate: {comparator.sample_rate}")
        print(f"  Num rotators: {comparator.num_rotators}")
        
        assert comparator.sample_rate == 48000
        assert comparator.num_rotators > 0
        
        # Test comparison
        mos = comparator.compare(audio_a, audio_b)
        assert 1 <= mos <= 5
        print(f"  Comparison MOS: {mos:.3f}")
        print("  ✓ PASS")
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    # Test 3: Utility functions
    print("\nTest 3: Utility functions...")
    try:
        # Test distance to MOS conversion
        mos_converted = zimtohrli.zimtohrli_distance_to_mos(distance)
        print(f"  Distance {distance:.6f} -> MOS {mos_converted:.3f}")
        
        # Test expected sample rate
        expected_sr = zimtohrli.get_expected_sample_rate()
        print(f"  Expected sample rate: {expected_sr} Hz")
        
        assert expected_sr == 48000
        assert 1 <= mos_converted <= 5
        print("  ✓ PASS")
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    # Test 4: Sample rate conversion
    print("\nTest 4: Sample rate conversion...")
    try:
        # Create 16kHz signal
        sr_16k = 16000
        t_16k = np.linspace(0, duration, int(sr_16k * duration), dtype=np.float32)
        audio_16k = np.sin(2 * np.pi * 1000 * t_16k).astype(np.float32)
        
        # Compare with 48kHz signal
        mos_resample = zimtohrli.compare_audio(audio_16k, sr_16k, audio_a, sample_rate)
        print(f"  16kHz vs 48kHz (same frequency): MOS {mos_resample:.3f}")
        
        # Should be high since same frequency content
        assert mos_resample > 3.0, f"Resampling test failed: {mos_resample}"
        print("  ✓ PASS")
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests PASSED! Package installation successful!")
    print("\nQuick usage reminder:")
    print("  import zimtohrli_py as zimtohrli")
    print("  mos = zimtohrli.compare_audio(audio_a, sr_a, audio_b, sr_b)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)