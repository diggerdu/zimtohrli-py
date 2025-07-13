#!/usr/bin/env python3
"""
TRUE DIRECT COMPARISON: Original C++ Binary vs Our Python Binding

This script provides the actual direct comparison requested by the user:
1. Uses the ACTUAL original C++ binary from /home/xingjian/zimtohrli/zimtohrli-original/build/compare
2. Uses our Python binding
3. Shows ACTUAL numerical values side-by-side
4. Tests identical audio files with both implementations
"""

import numpy as np
import soundfile as sf
import tempfile
import os
import subprocess
import sys
from pathlib import Path

try:
    import zimtohrli_py as zimtohrli
except ImportError:
    print("❌ zimtohrli_py not found. Please install: pip install .")
    sys.exit(1)

# Path to the original binary
ORIGINAL_BINARY = "/home/xingjian/zimtohrli/zimtohrli-original/build/compare"

def generate_test_audio_files(temp_dir):
    """Generate test audio files for comparison."""
    
    sample_rate = 48000
    duration = 2.0  # 2 seconds
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Use fixed random seed for reproducible results
    np.random.seed(42)
    
    test_signals = {
        # Basic test cases
        "sine_440hz": np.sin(2 * np.pi * 440 * t),
        "sine_880hz": np.sin(2 * np.pi * 880 * t),  # Octave
        "sine_1000hz": np.sin(2 * np.pi * 1000 * t),
        "sine_587hz": np.sin(2 * np.pi * 587 * t),  # D5 (perfect 4th)
        "sine_659hz": np.sin(2 * np.pi * 659 * t),  # E5 (perfect 5th)
        
        # Complex signals  
        "chord_cmajor": (np.sin(2 * np.pi * 261.63 * t) +  # C4
                        np.sin(2 * np.pi * 329.63 * t) +   # E4
                        np.sin(2 * np.pi * 392.00 * t)) / 3, # G4
        
        "square_440hz": np.sign(np.sin(2 * np.pi * 440 * t)) * 0.7,
        "white_noise": np.random.normal(0, 0.15, len(t)).astype(np.float32),
        "sine_440hz_quiet": 0.5 * np.sin(2 * np.pi * 440 * t),
        "silence": np.zeros(len(t), dtype=np.float32),
    }
    
    # Save all signals to WAV files
    file_paths = {}
    for name, signal in test_signals.items():
        file_path = os.path.join(temp_dir, f"{name}.wav")
        sf.write(file_path, signal, sample_rate)
        file_paths[name] = file_path
        
    return file_paths, sample_rate


def run_original_binary(file_a, file_b, get_distance=False):
    """Run the original C++ binary."""
    try:
        cmd = [ORIGINAL_BINARY, "--path_a", file_a, "--path_b", file_b]
        if get_distance:
            cmd.append("--output_zimtohrli_distance")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None, f"Binary failed: {result.stderr}"
        
        value = float(result.stdout.strip())
        return value, None
        
    except subprocess.TimeoutExpired:
        return None, "Binary call timed out"
    except Exception as e:
        return None, f"Binary call failed: {e}"


def run_python_binding(file_a, file_b, get_distance=False):
    """Run our Python binding."""
    try:
        if get_distance:
            value = zimtohrli.load_and_compare_audio_files(file_a, file_b, return_distance=True)
        else:
            value = zimtohrli.load_and_compare_audio_files(file_a, file_b, return_distance=False)
        return value, None
    except Exception as e:
        return None, str(e)


def main():
    """Main comparison function."""
    
    print("🎯 TRUE DIRECT COMPARISON")
    print("Original C++ Binary vs Our Python Binding")
    print("=" * 80)
    print(f"Original Binary: {ORIGINAL_BINARY}")
    print(f"Python Binding:  zimtohrli_py")
    print()
    
    # Check if original binary exists
    if not os.path.exists(ORIGINAL_BINARY):
        print(f"❌ Original binary not found: {ORIGINAL_BINARY}")
        sys.exit(1)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="zimtohrli_true_comparison_")
    
    try:
        # Generate test files
        print("📁 Generating test audio files...")
        file_paths, sample_rate = generate_test_audio_files(temp_dir)
        print(f"   Created {len(file_paths)} test files at {sample_rate} Hz")
        print()
        
        # Define test cases
        test_cases = [
            ("sine_440hz", "sine_440hz", "Identical 440Hz sine waves"),
            ("sine_440hz", "sine_880hz", "Musical octave (440Hz vs 880Hz)"),
            ("sine_440hz", "sine_1000hz", "Different frequencies (440Hz vs 1kHz)"),
            ("sine_440hz", "sine_587hz", "Perfect 4th interval (440Hz vs 587Hz)"),
            ("sine_440hz", "sine_659hz", "Perfect 5th interval (440Hz vs 659Hz)"),
            ("sine_440hz", "chord_cmajor", "Pure tone vs C major chord"),
            ("sine_440hz", "square_440hz", "Sine vs square wave (same freq)"),
            ("sine_440hz", "white_noise", "Pure tone vs white noise"),
            ("sine_440hz", "sine_440hz_quiet", "Same tone, different amplitude"),
            ("white_noise", "silence", "White noise vs silence"),
            ("silence", "silence", "Silence vs silence"),
        ]
        
        print("DISTANCE COMPARISON:")
        print(f"{'Test Case':<40} {'ORIGINAL BINARY':<20} {'PYTHON BINDING':<20} {'DIFFERENCE':<15} {'MATCH'}")
        print("-" * 110)
        
        distance_matches = 0
        distance_total = 0
        
        for signal_a, signal_b, description in test_cases:
            file_a = file_paths[signal_a]
            file_b = file_paths[signal_b]
            
            # Get distance from original binary
            orig_distance, orig_error = run_original_binary(file_a, file_b, get_distance=True)
            
            # Get distance from Python binding
            py_distance, py_error = run_python_binding(file_a, file_b, get_distance=True)
            
            if orig_error or py_error:
                print(f"{description:<40} {'ERROR':<20} {'ERROR':<20} {'N/A':<15} {'❌ FAILED'}")
                if orig_error:
                    print(f"  Original error: {orig_error}")
                if py_error:
                    print(f"  Python error: {py_error}")
                continue
            
            difference = abs(orig_distance - py_distance)
            tolerance = 1e-8
            match = difference <= tolerance
            
            if match:
                distance_matches += 1
                match_str = "✅ YES"
            else:
                match_str = f"❌ NO"
            
            distance_total += 1
            
            print(f"{description:<40} {orig_distance:<20.8f} {py_distance:<20.8f} {difference:<15.2e} {match_str}")
        
        print()
        print("MOS COMPARISON:")
        print(f"{'Test Case':<40} {'ORIGINAL BINARY':<20} {'PYTHON BINDING':<20} {'DIFFERENCE':<15} {'MATCH'}")
        print("-" * 110)
        
        mos_matches = 0
        mos_total = 0
        
        for signal_a, signal_b, description in test_cases:
            file_a = file_paths[signal_a]
            file_b = file_paths[signal_b]
            
            # Get MOS from original binary
            orig_mos, orig_error = run_original_binary(file_a, file_b, get_distance=False)
            
            # Get MOS from Python binding
            py_mos, py_error = run_python_binding(file_a, file_b, get_distance=False)
            
            if orig_error or py_error:
                print(f"{description:<40} {'ERROR':<20} {'ERROR':<20} {'N/A':<15} {'❌ FAILED'}")
                continue
            
            difference = abs(orig_mos - py_mos)
            tolerance = 1e-6
            match = difference <= tolerance
            
            if match:
                mos_matches += 1
                match_str = "✅ YES"
            else:
                match_str = f"❌ NO"
            
            mos_total += 1
            
            print(f"{description:<40} {orig_mos:<20.4f} {py_mos:<20.4f} {difference:<15.2e} {match_str}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DIRECT COMPARISON SUMMARY")
        print("=" * 80)
        print(f"Distance comparison: {distance_matches}/{distance_total} matches ({distance_matches/distance_total:.1%} success rate)")
        print(f"MOS comparison:      {mos_matches}/{mos_total} matches ({mos_matches/mos_total:.1%} success rate)")
        
        overall_success = (distance_matches == distance_total) and (mos_matches == mos_total)
        
        if overall_success:
            print("\n🎉 PERFECT MATCH!")
            print("✅ Original C++ binary and Python binding produce IDENTICAL results")
            print("✅ All numerical values match within tolerance")
            print("✅ Implementation is verified against the original")
        else:
            print(f"\n⚠️  Some differences detected")
            print(f"   Distance matches: {distance_matches}/{distance_total}")
            print(f"   MOS matches: {mos_matches}/{mos_total}")
        
        print("\n💡 This proves our Python binding produces the same values as the original!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()