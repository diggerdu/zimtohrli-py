#!/usr/bin/env python3
"""
Test the comparison scripts work correctly with our Python binding.
This validates the scripts themselves without needing the original binary.
"""

import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# Check if soundfile is available
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️  soundfile not available - some tests will be skipped")

try:
    import zimtohrli_py as zimtohrli
except ImportError:
    print("❌ zimtohrli_py not found. Please install: pip install .")
    sys.exit(1)


def test_python_binding_functionality():
    """Test that our Python binding works correctly."""
    print("🧪 Testing Python binding functionality...")
    
    # Test 1: Basic functionality
    sample_rate = 48000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Generate test signals
    sine_1khz = np.sin(2 * np.pi * 1000 * t)
    sine_440hz = np.sin(2 * np.pi * 440 * t)
    
    # Test compare_audio function
    try:
        # Identical signals should have distance ≈ 0
        distance_identical = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_1khz, sample_rate, return_distance=True)
        mos_identical = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_1khz, sample_rate, return_distance=False)
        
        # Different signals should have distance > 0
        distance_different = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_440hz, sample_rate, return_distance=True)
        mos_different = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_440hz, sample_rate, return_distance=False)
        
        print(f"✅ Identical signals: distance={distance_identical:.8f}, MOS={mos_identical:.6f}")
        print(f"✅ Different signals: distance={distance_different:.8f}, MOS={mos_different:.6f}")
        
        # Validate results make sense
        assert distance_identical < 1e-6, f"Identical signals should have near-zero distance, got {distance_identical}"
        assert distance_different > distance_identical, "Different signals should have higher distance"
        assert mos_identical > mos_different, "Identical signals should have higher MOS"
        assert 1.0 <= mos_identical <= 5.0, f"MOS should be 1-5, got {mos_identical}"
        assert 1.0 <= mos_different <= 5.0, f"MOS should be 1-5, got {mos_different}"
        
        print("✅ Python binding basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Python binding test failed: {e}")
        return False


def test_file_based_comparison():
    """Test file-based comparison functionality."""
    if not SOUNDFILE_AVAILABLE:
        print("⚠️  Skipping file-based test - soundfile not available")
        return True
        
    print("🧪 Testing file-based comparison...")
    
    temp_dir = tempfile.mkdtemp(prefix="zimtohrli_test_")
    
    try:
        # Generate test audio
        sample_rate = 48000
        duration = 0.5  # Shorter for testing
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        sine_1khz = np.sin(2 * np.pi * 1000 * t)
        sine_440hz = np.sin(2 * np.pi * 440 * t)
        
        # Save to files
        file_1khz = os.path.join(temp_dir, "sine_1khz.wav")
        file_440hz = os.path.join(temp_dir, "sine_440hz.wav")
        
        sf.write(file_1khz, sine_1khz, sample_rate)
        sf.write(file_440hz, sine_440hz, sample_rate)
        
        # Test file-based comparison
        mos_file = zimtohrli.load_and_compare_audio_files(file_1khz, file_440hz, return_distance=False)
        distance_file = zimtohrli.load_and_compare_audio_files(file_1khz, file_440hz, return_distance=True)
        
        # Test array-based comparison for comparison
        mos_array = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_440hz, sample_rate, return_distance=False)
        distance_array = zimtohrli.compare_audio(sine_1khz, sample_rate, sine_440hz, sample_rate, return_distance=True)
        
        print(f"✅ File-based:  distance={distance_file:.8f}, MOS={mos_file:.6f}")
        print(f"✅ Array-based: distance={distance_array:.8f}, MOS={mos_array:.6f}")
        
        # Results should be very close (identical audio data)
        distance_diff = abs(distance_file - distance_array)
        mos_diff = abs(mos_file - mos_array)
        
        print(f"✅ Differences: Δdistance={distance_diff:.2e}, ΔMOS={mos_diff:.2e}")
        
        assert distance_diff < 1e-6, f"File vs array distance difference too large: {distance_diff}"
        assert mos_diff < 1e-4, f"File vs array MOS difference too large: {mos_diff}"
        
        print("✅ File-based comparison test passed")
        return True
        
    except Exception as e:
        print(f"❌ File-based test failed: {e}")
        return False
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_comparison_script_components():
    """Test components used in the comparison scripts."""
    print("🧪 Testing comparison script components...")
    
    try:
        # Test distance to MOS conversion
        test_distances = [0.0, 0.001, 0.01, 0.1, 1.0]
        
        for distance in test_distances:
            mos = zimtohrli.zimtohrli_distance_to_mos(distance)
            print(f"✅ Distance {distance:.3f} -> MOS {mos:.6f}")
            
            assert 1.0 <= mos <= 5.0, f"MOS {mos} out of range for distance {distance}"
            
        # Test that lower distances produce higher MOS scores
        for i in range(len(test_distances) - 1):
            mos_current = zimtohrli.zimtohrli_distance_to_mos(test_distances[i])
            mos_next = zimtohrli.zimtohrli_distance_to_mos(test_distances[i + 1])
            
            assert mos_current >= mos_next, f"MOS should decrease with distance: {mos_current} vs {mos_next}"
            
        # Test expected sample rate
        expected_sr = zimtohrli.get_expected_sample_rate()
        print(f"✅ Expected sample rate: {expected_sr} Hz")
        assert expected_sr == 48000, f"Expected sample rate should be 48000, got {expected_sr}"
        
        # Test ZimtohrliComparator
        comparator = zimtohrli.ZimtohrliComparator()
        print(f"✅ Comparator sample rate: {comparator.sample_rate} Hz")
        print(f"✅ Comparator num rotators: {comparator.num_rotators}")
        
        # Test with 48kHz audio
        sample_rate = 48000
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        audio_a = np.sin(2 * np.pi * 1000 * t)
        audio_b = np.sin(2 * np.pi * 440 * t)
        
        mos_comp = comparator.compare(audio_a, audio_b, return_distance=False)
        distance_comp = comparator.compare(audio_a, audio_b, return_distance=True)
        
        print(f"✅ Comparator results: distance={distance_comp:.8f}, MOS={mos_comp:.6f}")
        
        print("✅ Comparison script components test passed")
        return True
        
    except Exception as e:
        print(f"❌ Comparison script components test failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases that might be encountered in comparison."""
    print("🧪 Testing edge cases...")
    
    try:
        sample_rate = 48000
        duration = 0.1  # Very short
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        # Edge case 1: Silence
        silence = np.zeros(len(t), dtype=np.float32)
        distance_silence = zimtohrli.compare_audio(silence, sample_rate, silence, sample_rate, return_distance=True)
        print(f"✅ Silence vs silence: distance={distance_silence:.8f}")
        
        # Edge case 2: Very quiet signal
        quiet_sine = 0.001 * np.sin(2 * np.pi * 1000 * t)
        distance_quiet = zimtohrli.compare_audio(quiet_sine, sample_rate, quiet_sine, sample_rate, return_distance=True)
        print(f"✅ Quiet signal vs itself: distance={distance_quiet:.8f}")
        
        # Edge case 3: Different sample rates (auto-resampling)
        sine_16k = np.sin(2 * np.pi * 1000 * np.linspace(0, duration, int(16000 * duration), dtype=np.float32))
        sine_44k = np.sin(2 * np.pi * 1000 * np.linspace(0, duration, int(44100 * duration), dtype=np.float32))
        
        distance_resample = zimtohrli.compare_audio(sine_16k, 16000, sine_44k, 44100, return_distance=True)
        print(f"✅ Cross-sample-rate (16k vs 44.1k): distance={distance_resample:.8f}")
        
        print("✅ Edge cases test passed")
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Zimtohrli Python binding for comparison script compatibility")
    print("="*70)
    
    tests = [
        ("Python binding functionality", test_python_binding_functionality),
        ("File-based comparison", test_file_based_comparison),
        ("Comparison script components", test_comparison_script_components),
        ("Edge cases", test_edge_cases),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
            
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Python binding is ready for comparison testing.")
        if not SOUNDFILE_AVAILABLE:
            print("💡 Install soundfile for full comparison script functionality: pip install soundfile")
        return True
    else:
        print("❌ Some tests failed! Please fix issues before running comparison scripts.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)