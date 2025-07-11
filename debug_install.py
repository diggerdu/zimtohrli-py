#!/usr/bin/env python3
"""
Debug script to help diagnose installation issues.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_system_dependencies():
    """Check if required system dependencies are available."""
    print("🔍 Checking System Dependencies...")
    print("=" * 50)
    
    required_tools = {
        'cmake': 'cmake --version',
        'pkg-config': 'pkg-config --version',
        'ninja': 'ninja --version',
        'gcc': 'gcc --version',
        'g++': 'g++ --version'
    }
    
    missing_tools = []
    for tool, cmd in required_tools.items():
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ {tool}: {version}")
            else:
                print(f"❌ {tool}: Command failed")
                missing_tools.append(tool)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"❌ {tool}: Not found or failed")
            missing_tools.append(tool)
    
    return missing_tools

def check_pkg_config_libraries():
    """Check if required pkg-config libraries are available."""
    print("\n🔍 Checking pkg-config Libraries...")
    print("=" * 50)
    
    required_libs = ['flac', 'ogg', 'vorbis', 'vorbisenc', 'soxr']
    missing_libs = []
    
    for lib in required_libs:
        try:
            result = subprocess.run(['pkg-config', '--exists', lib], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                # Get version info
                version_result = subprocess.run(['pkg-config', '--modversion', lib],
                                              capture_output=True, text=True, timeout=5)
                version = version_result.stdout.strip() if version_result.returncode == 0 else "unknown"
                print(f"✅ {lib}: {version}")
            else:
                print(f"❌ {lib}: Not found")
                missing_libs.append(lib)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"❌ {lib}: Error checking")
            missing_libs.append(lib)
    
    return missing_libs

def check_python_environment():
    """Check Python environment and dependencies."""
    print("\n🔍 Checking Python Environment...")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check required Python packages
    required_packages = ['setuptools', 'wheel', 'numpy']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            print(f"❌ {package}: Missing")

def check_build_environment():
    """Check build environment variables."""
    print("\n🔍 Checking Build Environment...")
    print("=" * 50)
    
    important_vars = [
        'CMAKE_ARGS', 'CMAKE_BUILD_PARALLEL_LEVEL', 'CMAKE_GENERATOR',
        'PKG_CONFIG_PATH', 'CC', 'CXX', 'CFLAGS', 'CXXFLAGS'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")

def suggest_fixes(missing_tools, missing_libs):
    """Suggest fixes for missing dependencies."""
    print("\n💡 Suggested Fixes...")
    print("=" * 50)
    
    if missing_tools:
        print("Missing build tools:")
        for tool in missing_tools:
            print(f"  - {tool}")
        
        print("\nInstallation commands:")
        print("Ubuntu/Debian:")
        print("  sudo apt update")
        print("  sudo apt install build-essential cmake pkg-config ninja-build")
        
        print("\nmacOS:")
        print("  brew install cmake pkg-config ninja")
        
        print("\nConda:")
        print("  conda install -c conda-forge cmake pkg-config ninja")
    
    if missing_libs:
        print(f"\nMissing audio libraries: {', '.join(missing_libs)}")
        
        print("\nInstallation commands:")
        print("Ubuntu/Debian:")
        print("  sudo apt install libflac-dev libvorbis-dev libogg-dev libopus-dev libsoxr-dev")
        
        print("\nmacOS:")
        print("  brew install flac libvorbis libogg opus sox")
        
        print("\nConda (recommended):")
        print("  conda install -c conda-forge libflac libvorbis libogg libopus soxr")

def test_minimal_cmake():
    """Test if CMake can configure a minimal project."""
    print("\n🔍 Testing CMake Configuration...")
    print("=" * 50)
    
    test_dir = Path("cmake_test")
    test_dir.mkdir(exist_ok=True)
    
    # Create minimal CMakeLists.txt
    cmake_content = """
cmake_minimum_required(VERSION 3.15)
project(test_project)

find_package(PkgConfig REQUIRED)
pkg_check_modules(flac REQUIRED flac)
pkg_check_modules(soxr REQUIRED soxr)

message(STATUS "CMake test successful!")
"""
    
    (test_dir / "CMakeLists.txt").write_text(cmake_content)
    
    try:
        build_dir = test_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        result = subprocess.run([
            'cmake', str(test_dir), '-B', str(build_dir)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CMake configuration test passed")
            return True
        else:
            print("❌ CMake configuration test failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CMake test timed out")
        return False
    except Exception as e:
        print(f"❌ CMake test error: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)

def main():
    """Run all diagnostic checks."""
    print("🐛 Zimtohrli Installation Debug Tool")
    print("=" * 60)
    
    missing_tools = check_system_dependencies()
    missing_libs = check_pkg_config_libraries()
    check_python_environment()
    check_build_environment()
    
    print("\n🧪 Running Build Tests...")
    cmake_ok = test_minimal_cmake()
    
    print("\n📊 Summary...")
    print("=" * 50)
    
    if not missing_tools and not missing_libs and cmake_ok:
        print("✅ All dependencies appear to be available!")
        print("If installation still fails, try:")
        print("  1. pip install -v . (verbose output)")
        print("  2. Check the detailed build logs above")
        print("  3. Try building with: CMAKE_BUILD_PARALLEL_LEVEL=1 pip install .")
    else:
        print("❌ Issues detected that may cause installation to fail:")
        if missing_tools:
            print(f"  - Missing build tools: {', '.join(missing_tools)}")
        if missing_libs:
            print(f"  - Missing libraries: {', '.join(missing_libs)}")
        if not cmake_ok:
            print("  - CMake configuration failed")
        
        suggest_fixes(missing_tools, missing_libs)

if __name__ == "__main__":
    main()