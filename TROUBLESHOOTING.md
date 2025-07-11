# Troubleshooting Installation Issues

If you're experiencing issues installing zimtohrli-py, this guide will help you diagnose and resolve common problems.

## Quick Diagnosis

Run the diagnostic script to check your system:

```bash
python debug_install.py
```

This will check for missing dependencies and provide specific installation commands for your system.

## Common Issues

### 1. Installation Hangs on "Building wheel"

**Symptoms**: Installation gets stuck at `Building wheel for zimtohrli (pyproject.toml) ... -`

### 2. Protobuf Download Failure  

**Symptoms**: 
```
[0/8] Performing download step (git clone) for 'protobuf-populate'
fatal: could not create work tree dir '': No such file or directory
CMake Error: Failed to clone repository: 'https://github.com/protocolbuffers/protobuf.git'
```

**Solutions**:
```bash
# Use offline installation (recommended)
./install_offline.sh

# Or install system protobuf first
sudo apt install libprotobuf-dev  # Ubuntu
conda install protobuf            # Conda

# Then retry normal installation
pip install zimtohrli
```

### 3. Build Hangs or Times Out

**Solutions**:
```bash
# Try single-threaded build
CMAKE_BUILD_PARALLEL_LEVEL=1 pip install zimtohrli-py

# Or use the debug installation script
./install_debug.sh
```

### 2. Missing System Dependencies

**Symptoms**: CMake errors about missing libraries (flac, soxr, etc.)

**Solutions**:
```bash
# Ubuntu/Debian
sudo apt install cmake pkg-config libflac-dev libvorbis-dev libogg-dev libopus-dev libsoxr-dev

# macOS
brew install cmake pkg-config flac libvorbis libogg opus sox

# Conda (recommended)
conda install -c conda-forge cmake pkg-config libflac libvorbis libogg libopus soxr
```

### 3. CMake Version Issues

**Symptoms**: "CMake 3.15 or higher is required"

**Solutions**:
```bash
# Ubuntu: Install newer CMake
pip install cmake

# Or download from cmake.org
```

### 4. Network/Timeout Issues

**Symptoms**: Build fails downloading protobuf dependencies

**Solutions**:
```bash
# Install with longer timeout
pip install --timeout 1000 zimtohrli-py

# Or use offline mode after downloading dependencies
pip install --no-deps zimtohrli-py
```

### 5. Memory Issues

**Symptoms**: Build process killed or out of memory errors

**Solutions**:
```bash
# Limit parallel builds
CMAKE_BUILD_PARALLEL_LEVEL=1 pip install zimtohrli-py

# Or increase system swap space
```

## Debug Installation Script

For comprehensive debugging, use the provided script:

```bash
./install_debug.sh
```

This script will:
1. Check system dependencies
2. Try multiple installation methods
3. Provide detailed error logs
4. Test manual build process

## Minimal Debug Setup

If standard installation fails, try the minimal setup:

```bash
python setup_minimal.py build_ext --inplace
```

This uses reduced dependencies and verbose output for easier debugging.

## Reporting Issues

When reporting installation issues, please include:

1. Output from `python debug_install.py`
2. Full error log from installation attempt
3. Operating system and version
4. Python version
5. Package manager used (pip, conda, etc.)

## Platform-Specific Notes

### Linux
- Ensure development packages are installed (`-dev` or `-devel` suffixes)
- Check that pkg-config can find libraries: `pkg-config --list-all | grep flac`

### macOS
- Use Homebrew for dependencies
- May need to set `PKG_CONFIG_PATH` for Homebrew libraries

### Windows
- Use conda for dependencies (recommended)
- Visual Studio Build Tools required
- May need to set environment variables for library paths

## Getting Help

1. **Check existing issues**: [GitHub Issues](https://github.com/diggerdu/zimtohrli-py/issues)
2. **Search discussions**: [GitHub Discussions](https://github.com/diggerdu/zimtohrli-py/discussions)
3. **Create new issue**: Include debug output and system information

## Success Verification

After successful installation, verify it works:

```python
import zimtohrli_py
import numpy as np

# Test with sample data
audio = np.random.randn(48000).astype(np.float32)
score = zimtohrli_py.compare_audio(audio, 48000, audio, 48000)
print(f"Self-comparison score: {score}")  # Should be ~5.0
```

## Alternative Installation Methods

If pip installation continues to fail:

1. **Build from source**:
   ```bash
   git clone https://github.com/diggerdu/zimtohrli-py.git
   cd zimtohrli-py
   python setup.py build_ext --inplace
   ```

2. **Use conda-build** (if available):
   ```bash
   conda build .
   conda install --use-local zimtohrli-py
   ```

3. **Docker installation**:
   ```dockerfile
   FROM python:3.9
   RUN apt-get update && apt-get install -y cmake pkg-config libflac-dev libsoxr-dev
   RUN pip install zimtohrli-py
   ```