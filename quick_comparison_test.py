#!/usr/bin/env python3
"""
Quick comparison test between Zimtohrli binary and Python binding.
This is a simplified version for quick testing with basic audio signals.
"""

import numpy as np
import soundfile as sf
import tempfile
import subprocess
import os
import sys
from pathlib import Path

try:
    import zimtohrli_py as zimtohrli
except ImportError:
    print("❌ zimtohrli_py not found. Please install: pip install .")
    sys.exit(1)


def create_test_audio(sample_rate=48000, duration=1.0):
    """Create simple test audio signals."""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    signals = {
        "sine_1000hz": np.sin(2 * np.pi * 1000 * t),
        "sine_440hz": np.sin(2 * np.pi * 440 * t),
        "white_noise": np.random.normal(0, 0.1, len(t)).astype(np.float32),
        "silence": np.zeros(len(t), dtype=np.float32),
    }
    
    return signals, sample_rate


def save_signals_to_files(signals, sample_rate, temp_dir):
    """Save signals to WAV files."""
    file_paths = {}
    
    for name, signal in signals.items():
        file_path = os.path.join(temp_dir, f"{name}.wav")
        sf.write(file_path, signal, sample_rate)
        file_paths[name] = file_path
        
    return file_paths


def run_binary_zimtohrli(binary_path, file_a, file_b):
    """Run the original zimtohrli binary."""
    try:
        result = subprocess.run([binary_path, file_a, file_b], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None, f"Binary failed: {result.stderr}"
            
        # Parse distance from output
        output = result.stdout.strip()
        try:
            # The binary typically outputs the distance as a number
            distance = float(output.split('\n')[-1].strip())
            return distance, None
        except (ValueError, IndexError):
            return None, f"Could not parse distance from: {output}"
            
    except subprocess.TimeoutExpired:
        return None, "Binary timed out"
    except Exception as e:
        return None, f"Error running binary: {e}"


def run_python_zimtohrli(file_a, file_b):
    """Run the Python binding."""
    try:
        distance = zimtohrli.load_and_compare_audio_files(file_a, file_b, return_distance=True)
        return distance, None
    except Exception as e:
        return None, f"Python binding failed: {e}"


def compare_implementations(binary_path):
    """Compare the two implementations."""
    print("🧪 Quick comparison test: Zimtohrli binary vs Python binding")
    print(f"Binary: {binary_path}")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="zimtohrli_quick_test_")
    
    try:
        # Generate test signals
        print("📊 Generating test audio...")
        signals, sample_rate = create_test_audio()
        file_paths = save_signals_to_files(signals, sample_rate, temp_dir)
        
        # Test cases: (signal_a, signal_b, expected_description)
        test_cases = [
            ("sine_1000hz", "sine_1000hz", "identical signals (should be ~0)"),
            ("sine_1000hz", "sine_440hz", "different frequencies"),
            ("sine_1000hz", "white_noise", "tone vs noise"),
            ("white_noise", "silence", "noise vs silence"),
        ]
        
        print(f"\n🔬 Running {len(test_cases)} test cases...")
        
        all_match = True
        tolerance = 1e-6
        
        for i, (sig_a, sig_b, description) in enumerate(test_cases, 1):
            print(f"\n{i}. {sig_a} vs {sig_b} ({description})")
            
            file_a = file_paths[sig_a]
            file_b = file_paths[sig_b]
            
            # Run both implementations
            binary_distance, binary_error = run_binary_zimtohrli(binary_path, file_a, file_b)
            python_distance, python_error = run_python_zimtohrli(file_a, file_b)
            
            if binary_error:
                print(f"   ❌ Binary error: {binary_error}")
                all_match = False
                continue
                
            if python_error:
                print(f"   ❌ Python error: {python_error}")
                all_match = False
                continue
                
            # Compare results
            diff = abs(binary_distance - python_distance)
            match = diff <= tolerance
            
            print(f"   Binary:  {binary_distance:.8f}")
            print(f"   Python:  {python_distance:.8f}")
            print(f"   Diff:    {diff:.2e}")
            print(f"   Status:  {'✅ MATCH' if match else '❌ MISMATCH'}")
            
            if not match:
                all_match = False
                
        # Summary
        print("\n" + "="*50)
        if all_match:
            print("🎉 SUCCESS! All tests passed - implementations are identical!")
            return True
        else:
            print("❌ FAILURE! Some tests failed - implementations differ!")
            return False
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def find_binary():
    """Try to find the zimtohrli binary."""
    possible_paths = [
        "./zimtohrli_binary",  # Symlink from setup script
        "zimtohrli",
        "../zimtohrli/bazel-bin/cpp/zimtohrli/zimtohrli",
        "../zimtohrli/build/cpp/zimtohrli/zimtohrli",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick comparison test")
    parser.add_argument("--binary-path", help="Path to zimtohrli binary")
    args = parser.parse_args()
    
    # Find binary
    binary_path = args.binary_path or find_binary()
    
    if not binary_path:
        print("❌ Zimtohrli binary not found!")
        print("Options:")
        print("1. Run: ./setup_original_zimtohrli.sh")
        print("2. Specify path: python quick_comparison_test.py --binary-path /path/to/zimtohrli")
        print("3. Build manually from: https://github.com/google/zimtohrli")
        sys.exit(1)
        
    if not os.path.exists(binary_path):
        print(f"❌ Binary not found at: {binary_path}")
        sys.exit(1)
        
    # Test binary
    try:
        result = subprocess.run([binary_path, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print(f"❌ Binary test failed: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Could not test binary: {e}")
        sys.exit(1)
        
    # Run comparison
    success = compare_implementations(binary_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()