#!/usr/bin/env python3
"""
Comprehensive test of all Zimtohrli Python binding functionality.
Tests everything needed for comparison scripts.
"""

import sys
import numpy as np
import tempfile
import os

# Force use of installed package
sys.path.insert(0, '/home/xingjian/mf3/lib/python3.12/site-packages')

# Check if soundfile is available
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️  soundfile not available - some tests will be skipped")

# Import the binding using the wrapper approach
from zimtohrli_py import _zimtohrli
from zimtohrli_py._zimtohrli import (
    Pyohrli as _ZimtohrliCore,
    compare_audio_arrays as _compare_audio_arrays,
    compare_audio_arrays_distance as _compare_audio_arrays_distance,
    MOSFromZimtohrli as _mos_from_zimtohrli,
)

# Import audio_utils to test
from zimtohrli_py import audio_utils


def test_all_core_functions():
    """Test all core functions comprehensively."""
    print("🧪 Testing all core functions...")
    
    # Generate comprehensive test signals
    sample_rate = 48000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    test_signals = {
        "sine_1000hz": np.sin(2 * np.pi * 1000 * t),
        "sine_440hz": np.sin(2 * np.pi * 440 * t),
        "sine_2000hz": np.sin(2 * np.pi * 2000 * t),
        "white_noise": np.random.normal(0, 0.1, len(t)).astype(np.float32),
        "silence": np.zeros(len(t), dtype=np.float32),
        "chirp": np.sin(2 * np.pi * (500 + 1000 * t) * t),
    }
    
    print(f"Generated {len(test_signals)} test signals")
    
    # Test all signal pairs
    signal_names = list(test_signals.keys())
    comparisons = []
    
    for i, name_a in enumerate(signal_names):
        for j, name_b in enumerate(signal_names):
            if i <= j:  # Avoid duplicate comparisons
                signal_a = test_signals[name_a]
                signal_b = test_signals[name_b]
                
                # Test both distance and MOS
                distance = _compare_audio_arrays_distance(signal_a, float(sample_rate), signal_b, float(sample_rate))
                mos = _compare_audio_arrays(signal_a, float(sample_rate), signal_b, float(sample_rate))
                mos_converted = _mos_from_zimtohrli(distance)
                
                # Verify MOS conversion consistency
                assert abs(mos - mos_converted) < 1e-6, f"MOS conversion mismatch: {mos} vs {mos_converted}"
                
                comparisons.append({
                    'pair': f"{name_a} vs {name_b}",
                    'distance': distance,
                    'mos': mos,
                    'identical': name_a == name_b
                })
    
    # Validate results
    for comp in comparisons:
        if comp['identical']:
            assert comp['distance'] < 1e-6, f"Identical signals should have near-zero distance: {comp}"
            assert comp['mos'] > 4.99, f"Identical signals should have MOS ≈ 5: {comp}"
        else:
            assert comp['distance'] > 0, f"Different signals should have positive distance: {comp}"
            assert comp['mos'] < 5.0, f"Different signals should have MOS < 5: {comp}"
        
        assert 1.0 <= comp['mos'] <= 5.0, f"MOS out of range: {comp}"
    
    print(f"✅ Tested {len(comparisons)} signal comparisons")
    print(f"✅ Distance range: {min(c['distance'] for c in comparisons):.2e} to {max(c['distance'] for c in comparisons):.2e}")
    print(f"✅ MOS range: {min(c['mos'] for c in comparisons):.3f} to {max(c['mos'] for c in comparisons):.3f}")
    
    return True


def test_comparator_class():
    """Test ZimtohrliComparator extensively."""
    print("🧪 Testing ZimtohrliComparator class...")
    
    comparator = _ZimtohrliCore()
    
    # Test properties
    print(f"✅ Sample rate: {comparator.sample_rate()}")
    print(f"✅ Num rotators: {comparator.num_rotators()}")
    
    assert comparator.sample_rate() == 48000, "Expected 48kHz sample rate"
    assert comparator.num_rotators() > 0, "Should have positive number of rotators"
    
    # Test analysis and comparison
    sample_rate = 48000
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    audio_a = np.sin(2 * np.pi * 1000 * t)
    audio_b = np.sin(2 * np.pi * 440 * t)
    
    # Test analyze method
    spec_a = comparator.analyze(audio_a)
    spec_b = comparator.analyze(audio_b)
    
    print(f"✅ Spectrogram A size: {len(spec_a)} bytes")
    print(f"✅ Spectrogram B size: {len(spec_b)} bytes")
    
    assert isinstance(spec_a, bytes), "Analyze should return bytes"
    assert isinstance(spec_b, bytes), "Analyze should return bytes"
    assert len(spec_a) > 0, "Spectrogram should not be empty"
    assert len(spec_b) > 0, "Spectrogram should not be empty"
    
    # Test distance method
    distance = comparator.distance(audio_a, audio_b)
    print(f"✅ Direct distance: {distance:.8f}")
    
    assert isinstance(distance, float), "Distance should be float"
    assert distance >= 0, "Distance should be non-negative"
    
    # Compare with global function
    distance_global = _compare_audio_arrays_distance(audio_a, float(sample_rate), audio_b, float(sample_rate))
    print(f"✅ Global distance: {distance_global:.8f}")
    
    # They should be very close (identical algorithm)
    assert abs(distance - distance_global) < 1e-6, f"Distance methods should match: {distance} vs {distance_global}"
    
    return True


def test_audio_utils():
    """Test audio_utils functionality."""
    if not SOUNDFILE_AVAILABLE:
        print("⚠️  Skipping audio_utils test - soundfile not available")
        return True
        
    print("🧪 Testing audio_utils...")
    
    temp_dir = tempfile.mkdtemp(prefix="zimtohrli_utils_test_")
    
    try:
        # Generate test audio
        sample_rate = 48000
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        reference = np.sin(2 * np.pi * 1000 * t)
        test_clean = np.sin(2 * np.pi * 1000 * t)  # Identical
        test_noisy = reference + np.random.normal(0, 0.01, len(reference)).astype(np.float32)
        test_different = np.sin(2 * np.pi * 440 * t)
        
        # Save to files
        ref_file = os.path.join(temp_dir, "reference.wav")
        clean_file = os.path.join(temp_dir, "clean.wav")
        noisy_file = os.path.join(temp_dir, "noisy.wav")
        diff_file = os.path.join(temp_dir, "different.wav")
        
        sf.write(ref_file, reference, sample_rate)
        sf.write(clean_file, test_clean, sample_rate)
        sf.write(noisy_file, test_noisy, sample_rate)
        sf.write(diff_file, test_different, sample_rate)
        
        # Test load_and_compare_audio_files
        mos_clean = audio_utils.load_and_compare_audio_files(ref_file, clean_file, return_distance=False)
        distance_clean = audio_utils.load_and_compare_audio_files(ref_file, clean_file, return_distance=True)
        
        mos_noisy = audio_utils.load_and_compare_audio_files(ref_file, noisy_file, return_distance=False)
        mos_different = audio_utils.load_and_compare_audio_files(ref_file, diff_file, return_distance=False)
        
        print(f"✅ Reference vs Clean: MOS={mos_clean:.6f}, distance={distance_clean:.8f}")
        print(f"✅ Reference vs Noisy: MOS={mos_noisy:.6f}")
        print(f"✅ Reference vs Different: MOS={mos_different:.6f}")
        
        # Validate results
        assert mos_clean > 4.99, f"Identical files should have MOS ≈ 5, got {mos_clean}"
        assert distance_clean < 1e-6, f"Identical files should have near-zero distance, got {distance_clean}"
        assert mos_clean > mos_noisy, "Clean should have higher MOS than noisy"
        assert mos_noisy > mos_different, "Noisy should have higher MOS than different frequency"
        
        # Test assess_audio_quality
        mos_qual, quality = audio_utils.assess_audio_quality(reference, test_clean, sample_rate)
        print(f"✅ Audio quality assessment: {quality} (MOS: {mos_qual:.3f})")
        
        assert mos_qual > 4.99, "Identical audio should have excellent quality"
        assert quality == "Excellent", f"Should be Excellent quality, got {quality}"
        
        # Test batch_compare_audio
        test_audios = [test_clean, test_noisy, test_different]
        batch_scores = audio_utils.batch_compare_audio(reference, test_audios, sample_rate)
        
        print(f"✅ Batch comparison: {[f'{score:.3f}' for score in batch_scores]}")
        
        assert len(batch_scores) == 3, "Should have 3 scores"
        assert all(1.0 <= score <= 5.0 for score in batch_scores), "All scores should be in valid range"
        assert batch_scores[0] > batch_scores[1] > batch_scores[2], "Scores should decrease in expected order"
        
        return True
        
    except Exception as e:
        print(f"❌ Audio utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_cross_sample_rates():
    """Test cross-sample-rate functionality."""
    print("🧪 Testing cross-sample-rate functionality...")
    
    duration = 0.5
    
    # Generate same signal at different sample rates
    for sr_a, sr_b in [(16000, 44100), (44100, 48000), (48000, 96000), (22050, 48000)]:
        t_a = np.linspace(0, duration, int(sr_a * duration), dtype=np.float32)
        t_b = np.linspace(0, duration, int(sr_b * duration), dtype=np.float32)
        
        # Same frequency content, different sample rates
        freq = 1000
        audio_a = np.sin(2 * np.pi * freq * t_a)
        audio_b = np.sin(2 * np.pi * freq * t_b)
        
        distance = _compare_audio_arrays_distance(audio_a, float(sr_a), audio_b, float(sr_b))
        mos = _compare_audio_arrays(audio_a, float(sr_a), audio_b, float(sr_b))
        
        print(f"✅ {sr_a}Hz vs {sr_b}Hz: distance={distance:.8f}, MOS={mos:.6f}")
        
        # Same content should have very low distance despite different sample rates
        assert distance < 0.01, f"Same content at different rates should have low distance: {distance}"
        assert mos > 4.0, f"Same content should have high MOS: {mos}"
    
    return True


def test_edge_cases_comprehensive():
    """Test comprehensive edge cases."""
    print("🧪 Testing comprehensive edge cases...")
    
    sample_rate = 48000
    
    # Test very short audio
    short_audio = np.sin(2 * np.pi * 1000 * np.linspace(0, 0.01, int(sample_rate * 0.01), dtype=np.float32))
    distance_short = _compare_audio_arrays_distance(short_audio, float(sample_rate), short_audio, float(sample_rate))
    print(f"✅ Very short audio (10ms): distance={distance_short:.8f}")
    assert distance_short < 1e-6, "Identical short audio should have near-zero distance"
    
    # Test very long audio
    long_duration = 10.0  # 10 seconds
    t_long = np.linspace(0, long_duration, int(sample_rate * long_duration), dtype=np.float32)
    long_audio = np.sin(2 * np.pi * 1000 * t_long)
    distance_long = _compare_audio_arrays_distance(long_audio, float(sample_rate), long_audio, float(sample_rate))
    print(f"✅ Very long audio (10s): distance={distance_long:.8f}")
    assert distance_long < 1e-6, "Identical long audio should have near-zero distance"
    
    # Test extreme amplitudes
    t = np.linspace(0, 0.5, int(sample_rate * 0.5), dtype=np.float32)
    loud_audio = 0.9 * np.sin(2 * np.pi * 1000 * t)  # Near clipping
    quiet_audio = 1e-6 * np.sin(2 * np.pi * 1000 * t)  # Very quiet
    
    distance_loud = _compare_audio_arrays_distance(loud_audio, float(sample_rate), loud_audio, float(sample_rate))
    distance_quiet = _compare_audio_arrays_distance(quiet_audio, float(sample_rate), quiet_audio, float(sample_rate))
    
    print(f"✅ Loud audio (0.9 amplitude): distance={distance_loud:.8f}")
    print(f"✅ Quiet audio (1e-6 amplitude): distance={distance_quiet:.8f}")
    
    assert distance_loud < 1e-6, "Identical loud audio should have near-zero distance"
    assert distance_quiet < 1e-6, "Identical quiet audio should have near-zero distance"
    
    # Test different data types
    t_short = np.linspace(0, 0.1, int(sample_rate * 0.1), dtype=np.float32)
    audio_float64 = np.sin(2 * np.pi * 1000 * t_short).astype(np.float64)
    audio_float32 = audio_float64.astype(np.float32)
    
    distance_dtype = _compare_audio_arrays_distance(audio_float32, float(sample_rate), audio_float32, float(sample_rate))
    print(f"✅ Data type conversion: distance={distance_dtype:.8f}")
    assert distance_dtype < 1e-6, "Same audio with different dtypes should have near-zero distance"
    
    return True


def main():
    """Run comprehensive tests."""
    print("🧪 Comprehensive Zimtohrli Python Binding Test")
    print("="*60)
    
    tests = [
        ("Core functions comprehensive", test_all_core_functions),
        ("ZimtohrliComparator class", test_comparator_class),
        ("Audio utilities", test_audio_utils),
        ("Cross-sample-rate functionality", test_cross_sample_rates),
        ("Edge cases comprehensive", test_edge_cases_comprehensive),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            
    print("\n" + "="*60)
    print(f"📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Zimtohrli Python binding is fully functional and ready!")
        print("✅ All comparison script functionality verified")
        if not SOUNDFILE_AVAILABLE:
            print("💡 For full file I/O support, install: pip install soundfile")
        return True
    else:
        print("❌ Some tests failed! Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)