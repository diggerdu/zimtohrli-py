#!/usr/bin/env python3
"""
Clean setup script for Zimtohrli Python binding.
This version includes ONLY core Zimtohrli functionality.
NO ViSQOL, NO protobuf dependencies - just pure Zimtohrli.
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import numpy


class CleanZimtohrliExtension(Extension):
    """Clean Zimtohrli extension - core functionality only."""
    
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CleanZimtohrliBuild(build_ext):
    """Clean build - no ViSQOL, no protobuf."""
    
    def build_extension(self, ext):
        if isinstance(ext, CleanZimtohrliExtension):
            self.build_clean_zimtohrli(ext)
        else:
            super().build_extension(ext)
    
    def build_clean_zimtohrli(self, ext):
        """Build with only core Zimtohrli dependencies."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        # Use the clean CMakeLists.txt
        cmake_lists_clean = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists_clean.txt"
        cmake_lists_original = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists.txt"
        
        # Backup original and use clean version
        backup_made = False
        if cmake_lists_clean.exists():
            print("🧹 Using clean Zimtohrli build (no ViSQOL, no protobuf)...")
            if cmake_lists_original.exists():
                cmake_lists_original.rename(cmake_lists_original.with_suffix('.txt.backup'))
                backup_made = True
            cmake_lists_clean.rename(cmake_lists_original)
        
        try:
            cfg = 'Debug' if self.debug else 'Release'
            
            cmake_args = [
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'-DCMAKE_BUILD_TYPE={cfg}',
                '-DCMAKE_VERBOSE_MAKEFILE=ON',
            ]
            
            build_args = ['--config', cfg, '--parallel', '2']
            
            build_temp = Path(self.build_temp) / ext.name
            if not build_temp.exists():
                build_temp.mkdir(parents=True)
            
            source_dir = Path(__file__).parent / "zimtohrli_py" / "src"
            
            print(f"🔧 CMake configure: {source_dir} -> {build_temp}")
            
            # Configure
            configure_cmd = ['cmake', str(source_dir)] + cmake_args
            print(f"Running: {' '.join(configure_cmd)}")
            
            result = subprocess.run(
                configure_cmd,
                cwd=build_temp,
                timeout=60,  # Shorter timeout since no downloads
                capture_output=False
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, configure_cmd)
            
            # Build
            build_cmd = ['cmake', '--build', '.'] + build_args
            print(f"🔨 Building: {' '.join(build_cmd)}")
            
            result = subprocess.run(
                build_cmd,
                cwd=build_temp,
                timeout=180,  # Faster build without protobuf
                capture_output=False
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, build_cmd)
                
            print("✅ Clean Zimtohrli build completed successfully!")
                
        except subprocess.TimeoutExpired as e:
            print(f"❌ Build timed out: {e}")
            raise
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed with return code {e.returncode}")
            print("Check the detailed build log above for specific errors.")
            raise
        finally:
            # Restore original CMakeLists.txt
            if cmake_lists_clean.exists():
                cmake_lists_original.unlink(missing_ok=True)
                cmake_lists_clean.rename(cmake_lists_clean.with_suffix('.txt'))
            if backup_made and cmake_lists_original.with_suffix('.txt.backup').exists():
                cmake_lists_original.with_suffix('.txt.backup').rename(cmake_lists_original)


def check_clean_dependencies():
    """Check minimal dependencies for clean Zimtohrli build."""
    print("🔍 Checking dependencies for clean Zimtohrli build...")
    print("=" * 55)
    
    # Check basic build tools
    tools = ['cmake', 'pkg-config', 'gcc', 'g++']
    missing_tools = []
    for tool in tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True, timeout=10)
            print(f"✅ {tool} found")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"❌ {tool} missing")
            missing_tools.append(tool)
    
    # Check minimal libraries (only what core Zimtohrli needs)
    libs = ['flac', 'soxr']  # Removed ogg, vorbis, vorbisenc - not strictly needed
    missing_libs = []
    for lib in libs:
        try:
            subprocess.run(['pkg-config', '--exists', lib], capture_output=True, check=True, timeout=5)
            version = subprocess.run(['pkg-config', '--modversion', lib], capture_output=True, text=True, timeout=5)
            version_str = version.stdout.strip() if version.returncode == 0 else "unknown"
            print(f"✅ {lib} found ({version_str})")
        except subprocess.CalledProcessError:
            print(f"❌ {lib} missing")
            missing_libs.append(lib)
    
    if missing_tools or missing_libs:
        print(f"\n❌ Missing dependencies!")
        if missing_tools:
            print(f"Tools: {', '.join(missing_tools)}")
        if missing_libs:
            print(f"Libraries: {', '.join(missing_libs)}")
        
        print(f"\n📦 Install minimal dependencies:")
        print("Ubuntu/Debian:")
        print("  sudo apt install cmake pkg-config build-essential libflac-dev libsoxr-dev")
        print("Conda:")  
        print("  conda install -c conda-forge cmake pkg-config libflac soxr")
        print("macOS:")
        print("  brew install cmake pkg-config flac soxr")
        return False
    
    print("\n✅ All minimal dependencies found!")
    print("📦 Core Zimtohrli can be built with these dependencies only")
    print("🚫 No protobuf, no ViSQOL, no network downloads required")
    return True


if __name__ == "__main__":
    print("🧹 Zimtohrli Clean Build (Core Functionality Only)")
    print("=" * 60)
    print("📦 Includes: Core Zimtohrli perceptual audio similarity")
    print("🚫 Excludes: ViSQOL, protobuf, network dependencies")
    print("⚡ Benefits: Faster build, fewer dependencies, same core functionality")
    print()
    
    if not check_clean_dependencies():
        print("\n❌ Please install missing dependencies first.")
        sys.exit(1)
    
    setup(
        name="zimtohrli-clean",
        version="1.0.0",
        description="Clean Zimtohrli Python binding - core functionality only",
        ext_modules=[
            CleanZimtohrliExtension('zimtohrli_py._zimtohrli', 'zimtohrli_py/src'),
        ],
        cmdclass={
            'build_ext': CleanZimtohrliBuild,
        },
        packages=["zimtohrli_py"],
        python_requires=">=3.8",
        install_requires=["numpy>=1.19.0"],
        include_dirs=[numpy.get_include()],
        zip_safe=False,
    )