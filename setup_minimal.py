"""
Minimal setup script for debugging installation issues.
This version has reduced dependencies and better error handling.
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import numpy


class MinimalCMakeExtension(Extension):
    """Minimal CMake extension for debugging."""
    
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class MinimalCMakeBuild(build_ext):
    """Minimal CMake build for debugging."""
    
    def build_extension(self, ext):
        if isinstance(ext, MinimalCMakeExtension):
            self.build_cmake_minimal(ext)
        else:
            super().build_extension(ext)
    
    def build_cmake_minimal(self, ext):
        """Build with minimal CMake configuration."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        # Use minimal CMakeLists.txt for debugging
        cmake_lists_minimal = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists_simple.txt"
        cmake_lists_original = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists.txt"
        
        # Backup original and use minimal version
        if cmake_lists_minimal.exists():
            print("Using minimal CMakeLists.txt for debugging...")
            cmake_lists_original.rename(cmake_lists_original.with_suffix('.txt.backup'))
            cmake_lists_minimal.rename(cmake_lists_original)
        
        try:
            cfg = 'Debug' if self.debug else 'Release'
            
            cmake_args = [
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'-DCMAKE_BUILD_TYPE={cfg}',
                '-DCMAKE_VERBOSE_MAKEFILE=ON',  # Enable verbose output
            ]
            
            build_args = ['--config', cfg]
            
            # Limit parallel jobs to avoid hanging
            build_args.extend(['--parallel', '1'])
            
            build_temp = Path(self.build_temp) / ext.name
            if not build_temp.exists():
                build_temp.mkdir(parents=True)
            
            source_dir = Path(__file__).parent / "zimtohrli_py" / "src"
            
            print(f"CMake configure: {source_dir} -> {build_temp}")
            print(f"CMake args: {cmake_args}")
            
            # Configure with timeout
            configure_cmd = ['cmake', str(source_dir)] + cmake_args
            print(f"Running: {' '.join(configure_cmd)}")
            
            result = subprocess.run(
                configure_cmd,
                cwd=build_temp,
                timeout=300,  # 5 minute timeout
                capture_output=False  # Show output in real-time
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, configure_cmd)
            
            # Build with timeout
            build_cmd = ['cmake', '--build', '.'] + build_args
            print(f"Running: {' '.join(build_cmd)}")
            
            result = subprocess.run(
                build_cmd,
                cwd=build_temp,
                timeout=600,  # 10 minute timeout
                capture_output=False  # Show output in real-time
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, build_cmd)
                
        except subprocess.TimeoutExpired as e:
            print(f"Build timed out: {e}")
            print("This usually indicates:")
            print("1. Network issues downloading dependencies")
            print("2. Missing system libraries")
            print("3. Insufficient memory/CPU")
            raise
        except subprocess.CalledProcessError as e:
            print(f"Build failed with return code {e.returncode}")
            print("Check the detailed output above for specific errors.")
            raise
        finally:
            # Restore original CMakeLists.txt
            if cmake_lists_original.with_suffix('.txt.backup').exists():
                cmake_lists_original.unlink(missing_ok=True)
                cmake_lists_original.with_suffix('.txt.backup').rename(cmake_lists_original)


def check_minimal_dependencies():
    """Check minimal dependencies and provide helpful error messages."""
    print("Checking minimal dependencies...")
    
    missing = []
    
    # Check cmake
    try:
        subprocess.run(['cmake', '--version'], capture_output=True, check=True)
        print("✅ CMake found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ CMake not found")
        missing.append("cmake")
    
    # Check pkg-config
    try:
        subprocess.run(['pkg-config', '--version'], capture_output=True, check=True)
        print("✅ pkg-config found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pkg-config not found")
        missing.append("pkg-config")
    
    # Check critical libraries
    critical_libs = ['flac', 'soxr']
    for lib in critical_libs:
        try:
            subprocess.run(['pkg-config', '--exists', lib], capture_output=True, check=True)
            print(f"✅ {lib} found")
        except subprocess.CalledProcessError:
            print(f"❌ {lib} not found")
            missing.append(f"lib{lib}")
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("\nQuick fix commands:")
        print("Ubuntu/Debian:")
        print("  sudo apt install cmake pkg-config libflac-dev libsoxr-dev")
        print("Conda:")
        print("  conda install -c conda-forge cmake pkg-config libflac soxr")
        return False
    
    print("✅ All minimal dependencies found")
    return True


if __name__ == "__main__":
    print("Zimtohrli Minimal Setup (Debug Mode)")
    print("=" * 40)
    
    if not check_minimal_dependencies():
        print("\n⚠️  Install missing dependencies before proceeding.")
        sys.exit(1)
    
    setup(
        name="zimtohrli-debug",
        version="1.0.0-debug",
        ext_modules=[
            MinimalCMakeExtension('zimtohrli_py._zimtohrli', 'zimtohrli_py/src'),
        ],
        cmdclass={
            'build_ext': MinimalCMakeBuild,
        },
        packages=["zimtohrli_py"],
        python_requires=">=3.8",
        install_requires=["numpy>=1.19.0"],
        include_dirs=[numpy.get_include()],
    )