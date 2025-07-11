# Offline Installation Guide

If you're experiencing network issues during installation (like the protobuf download failure), use this offline installation method that relies only on system dependencies.

## The Problem

The standard installation tries to download protobuf from GitHub during build time:
```
[0/8] Performing download step (git clone) for 'protobuf-populate'
fatal: could not create work tree dir '': No such file or directory
CMake Error: Failed to clone repository: 'https://github.com/protocolbuffers/protobuf.git'
```

## Solution: Use System Dependencies

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install cmake pkg-config build-essential
sudo apt install libflac-dev libvorbis-dev libogg-dev libsoxr-dev
sudo apt install libprotobuf-dev libabsl-dev  # Optional but recommended
```

**Conda (Recommended):**
```bash
conda install -c conda-forge cmake pkg-config libflac libvorbis libogg soxr
conda install -c conda-forge protobuf abseil-cpp  # Optional but recommended
```

**macOS:**
```bash
brew install cmake pkg-config flac libvorbis libogg soxr
brew install protobuf abseil  # Optional but recommended
```

### Step 2: Use System Dependencies Setup

Instead of the standard `pip install .`, use:

```bash
# Method 1: Build in place
python setup_system_deps.py build_ext --inplace

# Method 2: Install locally
python setup_system_deps.py install

# Method 3: Create wheel
python setup_system_deps.py bdist_wheel
```

### Step 3: Verify Installation

```bash
python verify_install.py
```

## What's Different

The system dependencies approach:

1. **Uses system protobuf/abseil** instead of downloading during build
2. **Provides fallback implementations** for missing dependencies  
3. **Avoids network requests** during build process
4. **Faster builds** since dependencies are pre-installed
5. **More reliable** in restricted network environments

## Troubleshooting

### Missing protobuf/abseil
If you can't install system protobuf/abseil, the build will create minimal replacements automatically.

### Still getting errors?
Run the diagnostic:
```bash
python debug_install.py
```

### Alternative: Manual Build
```bash
mkdir manual_build && cd manual_build
cmake ../zimtohrli_py/src -DCMAKE_BUILD_TYPE=Release
make -j2
```

## Performance Notes

System dependency builds may have slightly different performance characteristics:
- Usually **faster compilation** due to pre-installed dependencies
- **Same runtime performance** as the standard build
- Better **compatibility** with system package managers

## When to Use This Method

Use system dependencies installation when:
- Standard `pip install` fails with network errors
- You're in a restricted network environment
- Corporate firewall blocks GitHub access
- Building in containers without internet access
- You prefer using system package managers

The system dependencies method is equally robust and often more reliable than the network-dependent standard installation.