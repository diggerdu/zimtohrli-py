"""
Setup script for Zimtohrli Python package.
Uses clean build (core Zimtohrli only) by default for reliability.
"""

import os
import sys
import subprocess
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import numpy


class CMakeExtension(Extension):
    """CMake extension for building C++ code."""
    
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build command for CMake-based extensions."""
    
    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            self.build_cmake(ext)
        else:
            super().build_extension(ext)
    
    def build_cmake(self, ext):
        """Build the CMake extension using clean build by default."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        # Use clean build by default (can override with ZIMTOHRLI_FULL_BUILD=1)
        use_clean_build = os.environ.get('ZIMTOHRLI_FULL_BUILD', '0') == '0'
        
        # Setup clean build if requested
        cmake_lists_clean = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists_clean.txt"
        cmake_lists_original = Path(__file__).parent / "zimtohrli_py" / "src" / "CMakeLists.txt"
        backup_made = False
        
        if use_clean_build and cmake_lists_clean.exists():
            print("🧹 Using clean build (core Zimtohrli only, no ViSQOL/protobuf)")
            print("   Set ZIMTOHRLI_FULL_BUILD=1 to use full build with ViSQOL")
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
                '-DCMAKE_VERBOSE_MAKEFILE=ON',  # Helpful for debugging
            ]
        
            
            build_args = ['--config', cfg, '--parallel', '2']
            
            if "CMAKE_ARGS" in os.environ:
                cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]
            
            build_temp = Path(self.build_temp) / ext.name
            if not build_temp.exists():
                build_temp.mkdir(parents=True)
            
            source_dir = Path(__file__).parent / "zimtohrli_py" / "src"
            
            print(f"🔧 Building extension {ext.name}")
            print(f"📂 Source dir: {source_dir}")
            print(f"🏗️  Build temp: {build_temp}")
            print(f"📦 Extension dir: {extdir}")
            
            # Configure
            configure_cmd = ['cmake', str(source_dir)] + cmake_args
            print(f"⚙️  Configure: {' '.join(configure_cmd)}")
            subprocess.check_call(configure_cmd, cwd=build_temp)
            
            # Build
            build_cmd = ['cmake', '--build', '.'] + build_args
            print(f"🔨 Build: {' '.join(build_cmd)}")
            subprocess.check_call(build_cmd, cwd=build_temp)
            
            print("✅ Build completed successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed with return code {e.returncode}")
            if use_clean_build:
                print("💡 Try debugging with: python debug_install.py")
            raise
        finally:
            # Restore original CMakeLists.txt if we modified it
            if use_clean_build and cmake_lists_clean.exists():
                cmake_lists_original.unlink(missing_ok=True)
                cmake_lists_clean.rename(cmake_lists_clean.with_suffix('.txt'))
            if backup_made and cmake_lists_original.with_suffix('.txt.backup').exists():
                cmake_lists_original.with_suffix('.txt.backup').rename(cmake_lists_original)


def check_dependencies():
    """Check if required system dependencies are available for clean build."""
    print("🔍 Checking dependencies for clean Zimtohrli build...")
    
    # Check build tools
    tools = ['cmake', 'pkg-config', 'gcc', 'g++']
    missing_tools = []
    for tool in tools:
        try:
            subprocess.check_output([tool, '--version'], stderr=subprocess.DEVNULL)
            print(f"✅ {tool} found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} missing")
            missing_tools.append(tool)
    
    # Check minimal libraries for clean build
    libs = ['flac', 'soxr']
    missing_libs = []
    for lib in libs:
        try:
            subprocess.check_output(['pkg-config', '--exists', lib], stderr=subprocess.DEVNULL)
            print(f"✅ {lib} found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {lib} missing")
            missing_libs.append(lib)
    
    if missing_tools or missing_libs:
        print(f"\n❌ Missing dependencies for clean build!")
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
        print("\n💡 Or run: ./install_clean.sh")
        return False
    
    print("✅ All dependencies found for clean build!")
    return True


def get_long_description():
    """Get long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


if __name__ == "__main__":
    # Check dependencies only if explicitly requested
    if os.environ.get('ZIMTOHRLI_CHECK_DEPS', '0') == '1':
        if not check_dependencies():
            sys.exit(1)
    
    setup(
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        ext_modules=[
            CMakeExtension('zimtohrli_py._zimtohrli', 'zimtohrli_py/src'),
        ],
        cmdclass={
            'build_ext': CMakeBuild,
        },
        zip_safe=False,
        python_requires=">=3.8",
        include_dirs=[numpy.get_include()],
    )