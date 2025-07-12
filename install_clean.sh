#!/bin/bash

# Clean installation script for Zimtohrli Python binding
# Core functionality only - no ViSQOL, no protobuf

set -e

echo "🧹 Zimtohrli Clean Installation"
echo "=============================="
echo "📦 Core Zimtohrli perceptual audio similarity only"
echo "🚫 No ViSQOL, no protobuf, no network downloads"
echo ""

# Check if we're in the right directory
if [[ ! -f "setup_clean.py" ]]; then
    echo "❌ Error: setup_clean.py not found"
    echo "Please run this script from the zimtohrli-py directory"
    exit 1
fi

echo "🔍 Step 1: Checking minimal dependencies..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check minimal tools
missing_tools=()
for tool in cmake pkg-config gcc g++; do
    if command_exists "$tool"; then
        echo "✅ $tool found"
    else
        echo "❌ $tool missing"
        missing_tools+=("$tool")
    fi
done

# Check minimal libraries
missing_libs=()
for lib in flac soxr; do
    if pkg-config --exists "$lib" 2>/dev/null; then
        version=$(pkg-config --modversion "$lib" 2>/dev/null || echo "unknown")
        echo "✅ $lib found ($version)"
    else
        echo "❌ $lib missing"
        missing_libs+=("$lib")
    fi
done

# Install missing dependencies if needed
if [[ ${#missing_tools[@]} -gt 0 ]] || [[ ${#missing_libs[@]} -gt 0 ]]; then
    echo ""
    echo "🚨 Missing minimal dependencies!"
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo "Missing tools: ${missing_tools[*]}"
    fi
    
    if [[ ${#missing_libs[@]} -gt 0 ]]; then
        echo "Missing libraries: ${missing_libs[*]}"
    fi
    
    echo ""
    echo "📦 Install minimal dependencies:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install cmake pkg-config build-essential libflac-dev libsoxr-dev"
    echo ""
    echo "Conda:"
    echo "  conda install -c conda-forge cmake pkg-config libflac soxr"
    echo ""
    echo "macOS:"
    echo "  brew install cmake pkg-config flac soxr"
    echo ""
    echo "💡 Note: Only 2 audio libraries needed (vs 5+ for full build)!"
    exit 1
fi

echo ""
echo "🏗️  Step 2: Building clean Zimtohrli..."

# Clean any previous builds
if [[ -d "build" ]]; then
    echo "🧹 Cleaning previous build..."
    rm -rf build
fi

# Build with clean setup
if python setup_clean.py build_ext --inplace; then
    echo ""
    echo "✅ Clean build successful!"
    
    echo ""
    echo "🧪 Step 3: Testing clean installation..."
    
    # Test basic import
    if python -c "import zimtohrli_py; print('✅ Clean Zimtohrli import successful')"; then
        echo ""
        echo "🎉 Clean Zimtohrli installation completed!"
        echo ""
        echo "📊 What you have:"
        echo "  ✅ Core Zimtohrli perceptual audio similarity"
        echo "  ✅ MOS score calculation (1-5 scale)"
        echo "  ✅ Distance measurement (0-1 scale)"
        echo "  ✅ Automatic sample rate conversion"
        echo "  ✅ Full Python API compatibility"
        echo ""
        echo "🚫 What was removed:"
        echo "  ❌ ViSQOL integration (wasn't used by Python binding anyway)"
        echo "  ❌ Protobuf dependency (was causing build issues)"
        echo "  ❌ Network downloads during build"
        echo ""
        echo "⚡ Benefits:"
        echo "  🚀 Faster build (no protobuf compilation)"
        echo "  📦 Fewer dependencies (2 vs 5+ libraries)"
        echo "  🔒 No network requirements"
        echo "  🎯 Same core functionality and performance"
        echo ""
        echo "🧪 Run comprehensive tests:"
        echo "  python verify_install.py"
        echo ""
        echo "📚 Usage (identical to full version):"
        echo "  import zimtohrli_py"
        echo "  score = zimtohrli_py.compare_audio(audio1, sr1, audio2, sr2)"
        
    else
        echo "❌ Import test failed"
        echo "Try running: python verify_install.py"
        exit 1
    fi
    
else
    echo ""
    echo "❌ Clean build failed!"
    echo ""
    echo "Try debugging with:"
    echo "  python debug_install.py"
    exit 1
fi