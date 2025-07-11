"""
Setup script for Zimtohrli Python package.
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
        """Build the CMake extension."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        debug = int(os.environ.get('DEBUG', 0)) if self.debug is None else self.debug
        cfg = 'Debug' if debug else 'Release'
        
        # CMake lets you override the generator - we check this
        cmake_generator = os.environ.get('CMAKE_GENERATOR', '')
        
        # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            f'-DCMAKE_BUILD_TYPE={cfg}',
            '-DBUILD_ZIMTOHRLI_TESTS=OFF',  # Don't build tests for package
        ]
        
        build_args = []
        
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]
        
        # Add generator args
        if cmake_generator:
            cmake_args += [f'-G{cmake_generator}']
        else:
            # Try to use ninja if available
            try:
                subprocess.check_output(['ninja', '--version'])
                cmake_args += ['-GNinja']
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only
                build_args += [f"-j{self.parallel}"]
        
        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)
        
        # Copy source files to build directory
        source_dir = Path(__file__).parent / "zimtohrli_py" / "src"
        
        print(f"Building extension {ext.name}")
        print(f"Source dir: {source_dir}")
        print(f"Build temp: {build_temp}")
        print(f"Extension dir: {extdir}")
        
        # Configure
        subprocess.check_call([
            'cmake', str(source_dir)
        ] + cmake_args, cwd=build_temp)
        
        # Build
        subprocess.check_call([
            'cmake', '--build', '.', '--target', '_zimtohrli'
        ] + build_args, cwd=build_temp)


def check_dependencies():
    """Check if required system dependencies are available."""
    required_tools = ['cmake', 'pkg-config']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.check_output([tool, '--version'], stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"WARNING: Missing required tools: {', '.join(missing_tools)}")
        print("Please install them using your system package manager:")
        print("  Ubuntu/Debian: sudo apt install cmake pkg-config")
        print("  macOS: brew install cmake pkg-config")
        print("  Or use conda: conda install cmake pkg-config")


def get_long_description():
    """Get long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


if __name__ == "__main__":
    # Check dependencies
    check_dependencies()
    
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