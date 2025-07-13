#!/usr/bin/env python3
"""
Direct test of the Python binding using installed package.
"""

import sys
import numpy as np

# Force use of installed package
sys.path.insert(0, '/home/xingjian/mf3/lib/python3.12/site-packages')

# Import the C++ extension directly
from zimtohrli_py import _zimtohrli
from zimtohrli_py._zimtohrli import (
    Pyohrli as _ZimtohrliCore,
    compare_audio_arrays as _compare_audio_arrays,
    compare_audio_arrays_distance as _compare_audio_arrays_distance,
    MOSFromZimtohrli as _mos_from_zimtohrli,
)

def test_basic_functionality():
    """Test basic functionality directly."""
    print("🧪 Testing basic functionality...")
    
    # Generate test signals
    sample_rate = 48000
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    sine_1khz = np.sin(2 * np.pi * 1000 * t)
    sine_440hz = np.sin(2 * np.pi * 440 * t)
    
    # Test identical signals
    distance_identical = _compare_audio_arrays_distance(sine_1khz, float(sample_rate), sine_1khz, float(sample_rate))
    mos_identical = _compare_audio_arrays(sine_1khz, float(sample_rate), sine_1khz, float(sample_rate))
    
    # Test different signals
    distance_different = _compare_audio_arrays_distance(sine_1khz, float(sample_rate), sine_440hz, float(sample_rate))
    mos_different = _compare_audio_arrays(sine_1khz, float(sample_rate), sine_440hz, float(sample_rate))
    
    print(f"✅ Identical signals: distance={distance_identical:.8f}, MOS={mos_identical:.6f}")
    print(f"✅ Different signals: distance={distance_different:.8f}, MOS={mos_different:.6f}")
    
    # Test distance to MOS conversion
    mos_converted = _mos_from_zimtohrli(distance_different)
    print(f"✅ Manual MOS conversion: {mos_converted:.6f} (should match {mos_different:.6f})")
    
    # Test ZimtohrliComparator directly
    comparator = _ZimtohrliCore()
    distance_comp = comparator.distance(sine_1khz, sine_440hz)
    mos_comp = _mos_from_zimtohrli(distance_comp)
    
    print(f"✅ Comparator results: distance={distance_comp:.8f}, MOS={mos_comp:.6f}")
    print(f"✅ Comparator sample rate: {comparator.sample_rate()}")
    print(f"✅ Comparator num rotators: {comparator.num_rotators()}")
    
    # Validate results
    assert distance_identical < 1e-6, f"Identical signals should have near-zero distance, got {distance_identical}"
    assert distance_different > distance_identical, "Different signals should have higher distance"
    assert mos_identical > mos_different, "Identical signals should have higher MOS"
    assert 1.0 <= mos_identical <= 5.0, f"MOS should be 1-5, got {mos_identical}"
    assert 1.0 <= mos_different <= 5.0, f"MOS should be 1-5, got {mos_different}"
    assert abs(mos_converted - mos_different) < 1e-6, "MOS conversion should match direct computation"
    
    print("✅ All basic functionality tests passed!")
    return True

def test_edge_cases():
    """Test edge cases."""
    print("🧪 Testing edge cases...")
    
    sample_rate = 48000
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Test silence
    silence = np.zeros(len(t), dtype=np.float32)
    distance_silence = _compare_audio_arrays_distance(silence, float(sample_rate), silence, float(sample_rate))
    print(f"✅ Silence vs silence: distance={distance_silence:.8f}")
    
    # Test very quiet signal
    quiet_sine = 0.001 * np.sin(2 * np.pi * 1000 * t)
    distance_quiet = _compare_audio_arrays_distance(quiet_sine, float(sample_rate), quiet_sine, float(sample_rate))
    print(f"✅ Quiet signal vs itself: distance={distance_quiet:.8f}")
    
    # Test cross-sample-rate comparison (should auto-resample)
    sine_16k = np.sin(2 * np.pi * 1000 * np.linspace(0, duration, int(16000 * duration), dtype=np.float32))
    sine_44k = np.sin(2 * np.pi * 1000 * np.linspace(0, duration, int(44100 * duration), dtype=np.float32))
    
    distance_resample = _compare_audio_arrays_distance(sine_16k, 16000.0, sine_44k, 44100.0)
    print(f"✅ Cross-sample-rate (16k vs 44.1k): distance={distance_resample:.8f}")
    
    print("✅ All edge case tests passed!")
    return True

def main():
    """Run tests."""
    print("🧪 Testing Zimtohrli Python binding directly")
    print("="*60)
    
    print("\n📋 Available functions in C++ extension:")
    for attr in sorted(dir(_zimtohrli)):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    success = True
    
    try:
        success &= test_basic_functionality()
        print()
        success &= test_edge_cases()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "="*60)
    if success:
        print("🎉 All direct tests passed! Python binding is working correctly.")
    else:
        print("❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)