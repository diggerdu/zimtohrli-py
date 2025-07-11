# Zimtohrli Python Package

A Python package providing bindings for Google's [Zimtohrli](https://github.com/google/zimtohrli) psychoacoustic perceptual audio similarity metric.

## What is Zimtohrli?

Zimtohrli is a perceptual audio similarity metric that quantifies how different two audio signals sound to human listeners. It's designed to:

- **Measure perceptual differences** between audio signals
- **Improve audio compression** by focusing on human-audible differences  
- **Evaluate audio quality** with scores that correlate with human perception
- **Support machine learning** models for audio processing

## Features

- 🎵 **Perceptual audio comparison** using psychoacoustic modeling
- 🔄 **Automatic sample rate conversion** (any rate → 48kHz internally)
- 📊 **MOS scores** (1-5, higher = better) and raw distances (0-1, lower = better)
- ⚡ **High performance** with minimal Python overhead
- 🛡️ **Robust input validation** and error handling
- 📦 **Easy installation** with pip

## Installation

### Quick Install

```bash
pip install zimtohrli
```

**If installation fails due to network issues:**
```bash
# Use offline installation (no network required)
./install_offline.sh
```

### System Dependencies

The package requires some system libraries. Install them first:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install cmake pkg-config libflac-dev libvorbis-dev libogg-dev libopus-dev libsoxr-dev
```

**macOS:**
```bash
brew install cmake pkg-config flac libvorbis libogg opus sox
```

**Conda (recommended):**
```bash
conda install -c conda-forge cmake pkg-config libflac libvorbis libogg libopus soxr
```

### Development Install

```bash
git clone https://github.com/google/zimtohrli.git
cd zimtohrli/zimtohrli-python
pip install -e .
```

## Quick Start

```python
import zimtohrli_py as zimtohrli
import numpy as np

# Create test audio signals (1 second at any sample rate)
sample_rate = 16000  # or 22050, 44100, 48000, etc.
t = np.linspace(0, 1, sample_rate, dtype=np.float32)

audio_a = np.sin(2 * np.pi * 1000 * t)  # 1kHz sine wave
audio_b = np.sin(2 * np.pi * 440 * t)   # 440Hz sine wave

# Compare audio and get MOS score (1-5, higher is better)
mos_score = zimtohrli.compare_audio(audio_a, sample_rate, audio_b, sample_rate)
print(f"MOS Score: {mos_score:.3f}")

# Get raw Zimtohrli distance (0-1, lower is better)  
distance = zimtohrli.compare_audio(audio_a, sample_rate, audio_b, sample_rate, return_distance=True)
print(f"Distance: {distance:.6f}")
```

## Usage Examples

### Basic Audio Comparison

```python
import zimtohrli_py as zimtohrli
import numpy as np

# Generate test signals
sr = 48000
duration = 1.0
t = np.linspace(0, duration, int(sr * duration), dtype=np.float32)

original = np.sin(2 * np.pi * 1000 * t)
compressed = original + np.random.normal(0, 0.01, len(original))

# Compare audio quality
mos = zimtohrli.compare_audio(original, sr, compressed, sr)
print(f"Audio quality MOS: {mos:.3f}")

if mos > 4.5:
    print("Excellent quality")
elif mos > 4.0:
    print("Good quality") 
elif mos > 3.0:
    print("Fair quality")
else:
    print("Poor quality")
```

### Working with Audio Files

```python
import zimtohrli_py as zimtohrli

# Requires: pip install librosa
# or: pip install soundfile

# Compare two audio files directly
mos = zimtohrli.load_and_compare_audio_files("reference.wav", "compressed.mp3")
print(f"File comparison MOS: {mos:.3f}")
```

### Batch Processing (Efficient)

```python
import zimtohrli_py as zimtohrli
import numpy as np

# For multiple comparisons, use ZimtohrliComparator for better performance
comparator = zimtohrli.ZimtohrliComparator()

print(f"Expected sample rate: {comparator.sample_rate} Hz")
print(f"Spectrogram dimensions: {comparator.num_rotators}")

# Process multiple audio pairs efficiently (must be 48kHz)
audio_pairs = [
    (generate_audio_48k(), generate_audio_48k()) 
    for _ in range(100)
]

results = []
for audio_a, audio_b in audio_pairs:
    mos = comparator.compare(audio_a, audio_b)
    results.append(mos)

print(f"Average MOS: {np.mean(results):.3f}")
```

### Automatic Sample Rate Handling

```python
# The package automatically handles different sample rates
audio_16k = np.random.randn(16000).astype(np.float32)  # 1 sec at 16kHz
audio_44k = np.random.randn(44100).astype(np.float32)  # 1 sec at 44.1kHz

# Automatically resamples to 48kHz internally
mos = zimtohrli.compare_audio(audio_16k, 16000, audio_44k, 44100)
print(f"Cross-sample-rate comparison: {mos:.3f}")
```

## API Reference

### Main Functions

#### `compare_audio(audio_a, sample_rate_a, audio_b, sample_rate_b, return_distance=False)`

Compare two audio arrays using Zimtohrli.

**Parameters:**
- `audio_a` (np.ndarray): First audio array (1D, float32)
- `sample_rate_a` (float): Sample rate of first audio in Hz
- `audio_b` (np.ndarray): Second audio array (1D, float32)  
- `sample_rate_b` (float): Sample rate of second audio in Hz
- `return_distance` (bool): Return raw distance instead of MOS

**Returns:**
- `float`: MOS score (1-5) or distance (0-1)

#### `load_and_compare_audio_files(file_a, file_b, return_distance=False)`

Compare audio files directly (requires librosa or soundfile).

### ZimtohrliComparator Class

For efficient batch processing:

```python
comparator = zimtohrli.ZimtohrliComparator()

# Properties
comparator.sample_rate      # Expected sample rate (48000)
comparator.num_rotators     # Spectrogram dimensions

# Methods  
comparator.compare(audio_a, audio_b, return_distance=False)
comparator.analyze(audio)   # Get spectrogram data
```

### Utility Functions

```python
# Convert distance to MOS
mos = zimtohrli.zimtohrli_distance_to_mos(distance)

# Get expected sample rate
sr = zimtohrli.get_expected_sample_rate()  # Returns 48000
```

## Performance

The package is highly optimized:

- **Direct memory processing**: No file I/O overhead
- **Minimal Python overhead**: ~1-2ms vs pure C++
- **Efficient resampling**: Uses SoXR library when needed
- **Batch processing**: Reuse `ZimtohrliComparator` for multiple comparisons

### Performance Tips

1. **Use ZimtohrliComparator** for multiple comparisons
2. **Keep audio at 48kHz** to avoid resampling overhead  
3. **Use float32 arrays** to avoid type conversion
4. **Process in batches** rather than one-by-one

## System Requirements

- **Python**: 3.8+
- **OS**: Linux, macOS, Windows
- **Dependencies**: numpy
- **System libraries**: cmake, pkg-config, audio codecs (flac, vorbis, ogg, opus, soxr)

## Troubleshooting

### Installation Issues

If installation fails or hangs, use the built-in debugging tools:

```bash
# Diagnose system dependencies
python debug_install.py

# Try multiple installation methods with timeouts
./install_debug.sh

# Verify installation is working
python verify_install.py
```

**Common solutions:**

1. **Missing system dependencies**: Install cmake, pkg-config, and audio libraries
2. **Conda recommended**: `conda install -c conda-forge <packages>` often works better  
3. **Build hangs**: Try `CMAKE_BUILD_PARALLEL_LEVEL=1 pip install zimtohrli`
4. **Network timeouts**: Use `pip install --timeout 1000 zimtohrli`
5. **Windows**: May need Visual Studio build tools

### Runtime Issues

1. **Import errors**: Check that system dependencies are installed
2. **Array errors**: Ensure audio is 1D float32 numpy array
3. **Sample rate errors**: Use positive, reasonable sample rates (>1000 Hz)

### Debug Tools

The package includes several debugging utilities:

- `debug_install.py` - Check system dependencies and configuration
- `install_debug.sh` - Try multiple installation methods with timeouts
- `verify_install.py` - Test that installation is working correctly
- `setup_minimal.py` - Minimal build for debugging specific issues
- `TROUBLESHOOTING.md` - Comprehensive troubleshooting guide

### Getting Help

- **Troubleshooting Guide**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
- **Documentation**: See detailed docs in the [repository](https://github.com/google/zimtohrli)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/google/zimtohrli/issues)
- **Examples**: Check the `tests/` directory for more usage examples

## Contributing

Contributions welcome! Please see the main [Zimtohrli repository](https://github.com/google/zimtohrli) for guidelines.

## License

Apache License 2.0 - see [LICENSE](https://github.com/google/zimtohrli/blob/main/LICENSE) file.

## Citation

If you use Zimtohrli in research, please cite the original paper:

```bibtex
@article{zimtohrli2024,
  title={Zimtohrli: A Psychoacoustic Perceptual Audio Similarity Metric},
  author={Google Research Team},
  journal={arXiv preprint},
  year={2024}
}
```

---

## Changelog

### v1.0.0
- Initial release
- Core Zimtohrli functionality
- Automatic sample rate conversion
- Comprehensive test suite
- Full documentation