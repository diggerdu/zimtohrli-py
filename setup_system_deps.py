#!/usr/bin/env python3
"""
Setup script that uses system dependencies instead of downloading during build.
This avoids network issues during installation.
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import numpy


class SystemDepsExtension(Extension):
    """Extension that uses system dependencies."""
    
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class SystemDepsBuild(build_ext):
    """Build using system dependencies."""
    
    def build_extension(self, ext):
        if isinstance(ext, SystemDepsExtension):
            self.build_system_deps(ext)
        else:
            super().build_extension(ext)
    
    def build_system_deps(self, ext):
        """Build with system dependencies only."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        # Use the offline CMakeLists.txt
        cmake_lists_offline = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists_offline.txt"
        cmake_lists_original = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists.txt"
        
        # Backup original and use offline version
        backup_made = False
        if cmake_lists_offline.exists():
            print("Using system dependencies CMakeLists.txt...")
            if cmake_lists_original.exists():
                cmake_lists_original.rename(cmake_lists_original.with_suffix('.txt.backup'))
                backup_made = True
            cmake_lists_offline.rename(cmake_lists_original)
        
        try:
            cfg = 'Debug' if self.debug else 'Release'
            
            cmake_args = [
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'-DCMAKE_BUILD_TYPE={cfg}',
                '-DCMAKE_VERBOSE_MAKEFILE=ON',
            ]
            
            build_args = ['--config', cfg]
            
            # Limit parallel jobs to avoid issues
            build_args.extend(['--parallel', '2'])
            
            build_temp = Path(self.build_temp) / ext.name
            if not build_temp.exists():
                build_temp.mkdir(parents=True)
            
            source_dir = Path(__file__).parent / "zimtohrli_py" / "src"
            
            print(f"CMake configure: {source_dir} -> {build_temp}")
            
            # Configure
            configure_cmd = ['cmake', str(source_dir)] + cmake_args
            print(f"Running: {' '.join(configure_cmd)}")
            
            result = subprocess.run(
                configure_cmd,
                cwd=build_temp,
                timeout=120,  # 2 minute timeout
                capture_output=False
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, configure_cmd)
            
            # Build
            build_cmd = ['cmake', '--build', '.'] + build_args
            print(f"Running: {' '.join(build_cmd)}")
            
            result = subprocess.run(
                build_cmd,
                cwd=build_temp,
                timeout=300,  # 5 minute timeout
                capture_output=False
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, build_cmd)
                
        except subprocess.TimeoutExpired as e:
            print(f"Build timed out: {e}")
            print("Try installing system dependencies:")
            print("  Ubuntu: sudo apt install libprotobuf-dev libabsl-dev")
            print("  Conda: conda install -c conda-forge protobuf abseil-cpp")
            raise
        except subprocess.CalledProcessError as e:
            print(f"Build failed with return code {e.returncode}")
            print("Make sure you have system dependencies installed:")
            print("  Ubuntu: sudo apt install cmake pkg-config libflac-dev libsoxr-dev")
            print("  Conda: conda install -c conda-forge cmake pkg-config libflac soxr")
            raise
        finally:
            # Restore original CMakeLists.txt
            if cmake_lists_offline.exists():
                cmake_lists_original.unlink(missing_ok=True)
                cmake_lists_offline.rename(cmake_lists_offline.with_suffix('.txt'))
            if backup_made and cmake_lists_original.with_suffix('.txt.backup').exists():
                cmake_lists_original.with_suffix('.txt.backup').rename(cmake_lists_original)


def check_system_dependencies():
    """Check if required system dependencies are available."""
    print("Checking system dependencies for offline build...")
    
    # Check basic build tools
    tools = ['cmake', 'pkg-config']
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True, timeout=10)
            print(f"✅ {tool} found")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"❌ {tool} not found")
            return False
    
    # Check critical libraries
    libs = ['flac', 'soxr']
    for lib in libs:
        try:
            subprocess.run(['pkg-config', '--exists', lib], capture_output=True, check=True, timeout=5)
            print(f"✅ {lib} found")
        except subprocess.CalledProcessError:
            print(f"❌ {lib} not found")
            return False
    
    print("✅ All required dependencies found")
    return True


if __name__ == "__main__":
    print("Zimtohrli System Dependencies Setup")
    print("=" * 40)
    
    if not check_system_dependencies():
        print("\n❌ Missing dependencies. Install them first:")
        print("\nUbuntu/Debian:")
        print("  sudo apt install cmake pkg-config libflac-dev libsoxr-dev")
        print("\nConda:")
        print("  conda install -c conda-forge cmake pkg-config libflac soxr")
        print("\nThen try: python setup_system_deps.py build_ext --inplace")
        sys.exit(1)
    
    setup(
        name="zimtohrli-system",
        version="1.0.0",
        ext_modules=[
            SystemDepsExtension('zimtohrli_py._zimtohrli', 'zimtohrli_py/src'),
        ],
        cmdclass={
            'build_ext': SystemDepsBuild,
        },
        packages=["zimtohrli_py"],
        python_requires=">=3.8",
        install_requires=["numpy>=1.19.0"],
        include_dirs=[numpy.get_include()],
    )