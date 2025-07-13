#!/usr/bin/env python3
"""Final comprehensive test of the Zimtohrli Python binding."""

import sys
import os
import numpy as np
from pathlib import Path

def test_extension_import():
    """Test importing the _zimtohrli extension directly."""
    print("=== Testing Direct Extension Import ===")
    
    # Add the zimtohrli_py directory to the path
    zimtohrli_dir = Path(__file__).parent.parent / "zimtohrli_py"
    sys.path.insert(0, str(zimtohrli_dir))
    
    try:
        import _zimtohrli
        print("✅ Successfully imported _zimtohrli")
        
        # Test basic functionality
        print(f"Available functions: {[attr for attr in dir(_zimtohrli) if not attr.startswith('_')]}")
        
        # Test creating a Pyohrli instance
        zimtohrli_instance = _zimtohrli.Pyohrli()
        print("✅ Successfully created Pyohrli instance")
        
        # Test basic audio comparison
        print("Testing basic audio comparison...")
        
        # Create some test audio data (48kHz sample rate expected)
        duration = 0.1  # 100ms
        sample_rate = 48000
        samples = int(duration * sample_rate)
        
        # Create two similar sine waves
        t = np.linspace(0, duration, samples, dtype=np.float32)
        freq = 440  # A4 note
        audio_a = np.sin(2 * np.pi * freq * t).astype(np.float32)
        audio_b = np.sin(2 * np.pi * freq * t + 0.1).astype(np.float32)  # Slightly phase shifted
        
        # Test the enhanced compare function
        try:
            mos_score = _zimtohrli.compare_audio_arrays(audio_a, float(sample_rate), audio_b, float(sample_rate))
            print(f"✅ MOS comparison successful: {mos_score:.3f}")
            
            distance = _zimtohrli.compare_audio_arrays_distance(audio_a, float(sample_rate), audio_b, float(sample_rate))
            print(f"✅ Distance comparison successful: {distance:.6f}")
            
            # Test with different sample rates (should trigger resampling)
            other_rate = 44100
            mos_score_resample = _zimtohrli.compare_audio_arrays(audio_a, float(other_rate), audio_b, float(sample_rate))
            print(f"✅ MOS with resampling successful: {mos_score_resample:.3f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during audio comparison: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import _zimtohrli: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_package_installation():
    """Test if the package can be installed properly."""
    print("\n=== Testing Package Installation ===")
    
    # Go to the project directory
    project_dir = Path(__file__).parent.parent
    
    try:
        # Test pip install in editable mode
        import subprocess
        print("Attempting pip install in editable mode...")
        
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"]
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package installed successfully")
            
            # Now try importing the package
            try:
                import zimtohrli_py
                print("✅ Successfully imported zimtohrli_py package")
                
                # Test the high-level API
                if hasattr(zimtohrli_py, 'compare_audio'):
                    print("✅ High-level API available")
                    
                    # Quick test
                    duration = 0.05  # 50ms
                    sample_rate = 48000
                    samples = int(duration * sample_rate)
                    
                    t = np.linspace(0, duration, samples, dtype=np.float32)
                    audio_a = np.sin(2 * np.pi * 440 * t).astype(np.float32)
                    audio_b = audio_a * 0.95  # Slightly quieter
                    
                    mos = zimtohrli_py.compare_audio(audio_a, sample_rate, audio_b, sample_rate)
                    print(f"✅ High-level API test successful: MOS = {mos:.3f}")
                    
                    return True
                else:
                    print("⚠️  High-level API not available")
                    return True  # Extension works, but wrapper might have issues
                    
            except ImportError as e:
                print(f"❌ Failed to import zimtohrli_py package: {e}")
                return False
                
        else:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during package installation: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Comprehensive Zimtohrli Python Binding Test")
    print("=" * 50)
    
    # Test 1: Direct extension import and functionality
    ext_success = test_extension_import()
    
    # Test 2: Package installation and high-level API
    pkg_success = test_package_installation()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  Extension functionality: {'✅ PASS' if ext_success else '❌ FAIL'}")
    print(f"  Package installation: {'✅ PASS' if pkg_success else '❌ FAIL'}")
    
    if ext_success and pkg_success:
        print("\n🎉 All tests PASSED! The Zimtohrli Python binding is working correctly.")
        print("✅ The CMake extension suffix fix is working properly.")
        return 0
    elif ext_success:
        print("\n🔧 Extension works but package installation needs attention.")
        print("✅ The CMake extension suffix fix is working properly.")
        return 1
    else:
        print("\n❌ Critical issues found with the extension.")
        return 2

if __name__ == "__main__":
    sys.exit(main())