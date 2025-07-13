#!/usr/bin/env python3
"""Manual test of Python extension suffix logic."""

import sysconfig
import sys
import os
from pathlib import Path

def main():
    print("=== Manual Python Extension Suffix Test ===")
    print()
    
    # Get Python information
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print()
    
    # Get the extension suffix
    ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
    print(f"Extension suffix: {ext_suffix}")
    
    if ext_suffix:
        print(f"✅ Extension suffix found: {ext_suffix}")
        
        # Test what CMake would generate
        expected_filename = f"_zimtohrli{ext_suffix}"
        print(f"Expected extension filename: {expected_filename}")
        
        # Test the CMake command that's used in the build
        import subprocess
        try:
            cmd = [sys.executable, '-c', "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            cmake_suffix = result.stdout.strip()
            print(f"CMake would get suffix: {cmake_suffix}")
            
            if cmake_suffix == ext_suffix:
                print("✅ CMake suffix matches Python suffix!")
                return True
            else:
                print(f"❌ Mismatch: expected {ext_suffix}, CMake got {cmake_suffix}")
                return False
        except Exception as e:
            print(f"❌ Error testing CMake command: {e}")
            return False
    else:
        print("❌ No extension suffix found")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Extension suffix test passed!")
        sys.exit(0)
    else:
        print("\n❌ Extension suffix test failed!")
        sys.exit(1)