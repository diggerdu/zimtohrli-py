#!/usr/bin/env python3
"""Test script to verify Python extension suffix configuration."""

import sysconfig
import sys
import subprocess
import os
from pathlib import Path

def test_extension_suffix():
    """Test the Python extension suffix logic."""
    print("🔍 Testing Python extension suffix configuration...")
    
    # Get the expected suffix
    expected_suffix = sysconfig.get_config_var('EXT_SUFFIX')
    print(f"✅ Expected extension suffix: {expected_suffix}")
    
    # Test the CMake command that we use
    python_executable = sys.executable
    print(f"✅ Python executable: {python_executable}")
    
    try:
        cmd = [python_executable, '-c', "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        cmake_suffix = result.stdout.strip()
        print(f"✅ CMake would get suffix: {cmake_suffix}")
        
        if cmake_suffix == expected_suffix:
            print("✅ CMake suffix matches expected suffix!")
            return True
        else:
            print(f"❌ Mismatch: expected {expected_suffix}, got {cmake_suffix}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run suffix command: {e}")
        return False

def test_installation():
    """Test the actual installation process."""
    print("\n🔧 Testing installation process...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Try to build the extension
    try:
        cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            print("Build output:")
            print(result.stdout)
            
            # Check if the extension file exists
            expected_suffix = sysconfig.get_config_var('EXT_SUFFIX')
            expected_file = project_dir / f"zimtohrli_py/_zimtohrli{expected_suffix}"
            
            if expected_file.exists():
                print(f"✅ Extension file found: {expected_file}")
                return True
            else:
                print(f"❌ Extension file not found: {expected_file}")
                print("Files in zimtohrli_py/:")
                zimtohrli_dir = project_dir / "zimtohrli_py"
                if zimtohrli_dir.exists():
                    for f in zimtohrli_dir.iterdir():
                        print(f"  {f}")
                return False
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Build failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Zimtohrli Python extension configuration...")
    
    # Test 1: Extension suffix logic
    suffix_ok = test_extension_suffix()
    
    # Test 2: Actual installation
    if suffix_ok:
        install_ok = test_installation()
        
        if install_ok:
            print("\n🎉 All tests passed! The extension suffix fix is working.")
        else:
            print("\n❌ Installation test failed.")
    else:
        print("\n❌ Extension suffix test failed.")
    
    print("\n📋 Summary:")
    print(f"  Extension suffix test: {'✅' if suffix_ok else '❌'}")
    if suffix_ok:
        print(f"  Installation test: {'✅' if install_ok else '❌'}")