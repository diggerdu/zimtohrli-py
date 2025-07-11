#!/usr/bin/env python3
"""
Simple verification script to test if zimtohrli-py is working correctly.
Run this after installation to ensure everything is functioning properly.
"""

import sys
import traceback
import numpy as np


def test_basic_import():
    """Test basic package import."""
    print("🔍 Testing basic import...")
    try:
        import zimtohrli_py
        print("✅ zimtohrli_py imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import zimtohrli_py: {e}")
        return False


def test_core_functions():
    """Test core functionality."""
    print("\n🔍 Testing core functions...")
    try:
        import zimtohrli_py
        
        # Test function availability
        functions = ['compare_audio', 'compare_audio_distance']
        for func_name in functions:
            if hasattr(zimtohrli_py, func_name):
                print(f"✅ {func_name} available")
            else:
                print(f"❌ {func_name} not available")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing core functions: {e}")
        return False


def test_self_comparison():
    """Test self-comparison (should return perfect score)."""
    print("\n🔍 Testing self-comparison...")
    try:
        import zimtohrli_py
        
        # Create test signal
        duration = 1.0  # 1 second
        sample_rate = 48000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        # Compare signal to itself
        score = zimtohrli_py.compare_audio(audio, sample_rate, audio, sample_rate)
        
        print(f"Self-comparison score: {score:.3f}")
        
        # Perfect match should be close to 5.0
        if 4.8 <= score <= 5.0:
            print("✅ Self-comparison test passed")
            return True
        else:
            print(f"❌ Self-comparison test failed: expected ~5.0, got {score:.3f}")
            return False
            
    except Exception as e:
        print(f"❌ Error in self-comparison test: {e}")
        traceback.print_exc()
        return False


def test_different_sample_rates():
    """Test with different sample rates (should handle resampling)."""
    print("\n🔍 Testing sample rate conversion...")
    try:
        import zimtohrli_py
        
        # Create signals at different sample rates
        duration = 0.5
        freq = 1000
        
        # 44.1 kHz signal
        sr1 = 44100
        t1 = np.linspace(0, duration, int(sr1 * duration), False)
        audio1 = np.sin(2 * np.pi * freq * t1).astype(np.float32)
        
        # 16 kHz signal (same frequency content)
        sr2 = 16000
        t2 = np.linspace(0, duration, int(sr2 * duration), False)
        audio2 = np.sin(2 * np.pi * freq * t2).astype(np.float32)
        
        # Compare signals with different sample rates
        score = zimtohrli_py.compare_audio(audio1, sr1, audio2, sr2)
        
        print(f"Cross-sample-rate score: {score:.3f}")
        
        # Should be high similarity (>4.0) since same frequency content
        if score > 4.0:
            print("✅ Sample rate conversion test passed")
            return True
        else:
            print(f"❌ Sample rate conversion test failed: expected >4.0, got {score:.3f}")
            return False
            
    except Exception as e:
        print(f"❌ Error in sample rate test: {e}")
        traceback.print_exc()
        return False


def test_distance_function():
    """Test distance function (should be inverse of MOS)."""
    print("\n🔍 Testing distance function...")
    try:
        import zimtohrli_py
        
        # Create test signals
        sample_rate = 48000
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Original signal
        audio1 = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # Slightly different signal (add small amount of noise)
        audio2 = audio1 + 0.01 * np.random.randn(len(audio1)).astype(np.float32)
        
        # Test both functions
        mos_score = zimtohrli_py.compare_audio(audio1, sample_rate, audio2, sample_rate)
        distance = zimtohrli_py.compare_audio_distance(audio1, sample_rate, audio2, sample_rate)
        
        print(f"MOS score: {mos_score:.3f}")
        print(f"Distance: {distance:.3f}")
        
        # Distance should be positive, MOS should be positive
        if mos_score > 0 and distance >= 0:
            print("✅ Distance function test passed")
            return True
        else:
            print(f"❌ Distance function test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in distance function test: {e}")
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases."""
    print("\n🔍 Testing edge cases...")
    try:
        import zimtohrli_py
        
        # Test very short audio
        short_audio = np.array([0.1, 0.2, 0.1], dtype=np.float32)
        score = zimtohrli_py.compare_audio(short_audio, 48000, short_audio, 48000)
        print(f"Short audio test: {score:.3f}")
        
        # Test zero audio
        zero_audio = np.zeros(1000, dtype=np.float32)
        score = zimtohrli_py.compare_audio(zero_audio, 48000, zero_audio, 48000)
        print(f"Zero audio test: {score:.3f}")
        
        print("✅ Edge cases test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error in edge cases test: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("🧪 Zimtohrli-py Installation Verification")
    print("=" * 50)
    
    tests = [
        test_basic_import,
        test_core_functions,
        test_self_comparison,
        test_different_sample_rates,
        test_distance_function,
        test_edge_cases,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is working correctly.")
        print("\nYou can now use zimtohrli_py in your projects:")
        print("```python")
        print("import zimtohrli_py")
        print("score = zimtohrli_py.compare_audio(audio1, sr1, audio2, sr2)")
        print("```")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Installation may have issues.")
        print("\nTry running the debug script: python debug_install.py")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)