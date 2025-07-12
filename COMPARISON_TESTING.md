# Zimtohrli Implementation Comparison Testing

This directory contains scripts to compare the results between the original Zimtohrli binary (from https://github.com/google/zimtohrli) and our Python binding to ensure they produce identical results.

## Quick Start

### 1. Setup Original Zimtohrli Binary

```bash
# Run the setup script to build original Zimtohrli
./setup_original_zimtohrli.sh
```

This script will:
- Clone the original Zimtohrli repository (if not present)
- Build it using Bazel or CMake (whichever is available)
- Create a convenient symlink for testing

### 2. Run Quick Comparison Test

```bash
# Quick test with basic audio signals
python quick_comparison_test.py

# Or specify binary path manually
python quick_comparison_test.py --binary-path /path/to/zimtohrli
```

### 3. Run Comprehensive Comparison

```bash
# Full comprehensive testing with detailed report
python compare_implementations.py

# Save detailed JSON report
python compare_implementations.py --output-report my_comparison.json
```

## Scripts Overview

### `setup_original_zimtohrli.sh`
- Automated setup script to build the original Zimtohrli binary
- Supports both Bazel and CMake build systems
- Creates convenient symlinks for testing
- Validates the built binary

### `quick_comparison_test.py`
- Fast comparison test with basic audio signals
- Tests 4 fundamental comparison cases
- Minimal dependencies (just soundfile)
- Good for quick validation

**Test cases:**
- Identical signals (distance ≈ 0)
- Different frequency tones
- Tone vs noise
- Noise vs silence

### `compare_implementations.py`
- Comprehensive comparison with extensive test cases
- Generates detailed JSON reports
- Tests various audio types and edge cases
- Statistical analysis of differences

**Test cases include:**
- Pure tones (various frequencies)
- Complex signals (chirps, multi-tone)
- Noise signals (white, pink)
- Modified signals (quiet, noisy versions)
- Silence and extreme cases
- Cross-comparisons between all signal types

## Expected Results

Both implementations should produce **identical** results within numerical precision:

- **Distance tolerance**: ≤ 1e-6 (one millionth)
- **MOS tolerance**: ≤ 1e-4 (one ten-thousandth)

Since Zimtohrli is deterministic, any differences beyond floating-point precision indicate implementation discrepancies.

## Example Output

### Quick Test Success
```
🧪 Quick comparison test: Zimtohrli binary vs Python binding
Binary: ./zimtohrli_binary

📊 Generating test audio...

🔬 Running 4 test cases...

1. sine_1000hz vs sine_1000hz (identical signals)
   Binary:  0.00000000
   Python:  0.00000000
   Diff:    0.00e+00
   Status:  ✅ MATCH

2. sine_1000hz vs sine_440hz (different frequencies)
   Binary:  0.01234567
   Python:  0.01234567
   Diff:    1.23e-08
   Status:  ✅ MATCH

🎉 SUCCESS! All tests passed - implementations are identical!
```

### Comprehensive Test Success
```
📋 COMPARISON SUMMARY
============================================================
Total comparison pairs: 14
Successful comparisons: 14
Matching results: 14
Success rate: 100.0%
Match rate: 100.0%

🎉 PERFECT MATCH! Python binding produces identical results to original binary.
```

## Troubleshooting

### Binary Not Found
```bash
# Option 1: Run setup script
./setup_original_zimtohrli.sh

# Option 2: Build manually
git clone https://github.com/google/zimtohrli.git
cd zimtohrli
bazel build //cpp/zimtohrli:zimtohrli

# Option 3: Use CMake
mkdir build && cd build
cmake .. && make
```

### Dependencies Missing
```bash
# Install required Python packages
pip install soundfile numpy

# For the original binary, you need:
# - Bazel or CMake
# - C++ compiler
# - Audio libraries (flac, vorbis, etc.)
```

### Build Failures
- **Bazel issues**: Check Bazel version compatibility
- **CMake issues**: Ensure all dependencies are installed
- **Permission errors**: Make sure you have write access to the directory

## Implementation Details

### Comparison Methodology

1. **Audio Generation**: Creates identical test signals using NumPy
2. **File I/O**: Saves signals as WAV files (both implementations read files)
3. **Execution**: Runs both implementations on identical input files
4. **Result Parsing**: Extracts distance values and compares numerically
5. **Tolerance Checking**: Verifies differences are within acceptable precision

### Why File-Based Testing?

We use file-based testing because:
- The original binary only accepts file inputs
- Ensures identical input data (no in-memory vs file differences)
- Tests the complete pipeline including audio loading
- Validates our file handling matches the original

### Distance vs MOS

- **Distance**: Raw Zimtohrli distance (0-1, lower = more similar)
- **MOS**: Mean Opinion Score (1-5, higher = better quality)
- Both implementations should produce identical distance values
- MOS is computed from distance using: `MOS = distance_to_mos(distance)`

## Integration with CI/CD

You can integrate these tests into your CI/CD pipeline:

```bash
# In your CI script
./setup_original_zimtohrli.sh
python quick_comparison_test.py
if [ $? -eq 0 ]; then
    echo "✅ Comparison tests passed"
else
    echo "❌ Comparison tests failed"
    exit 1
fi
```

## Contributing

When modifying the Python binding:

1. **Always run comparison tests** before committing
2. **All tests must pass** with identical results
3. **Add new test cases** for new functionality
4. **Update tolerances carefully** - they should remain very strict

The comparison tests are the gold standard for validating that our Python binding maintains perfect compatibility with the original Zimtohrli implementation.