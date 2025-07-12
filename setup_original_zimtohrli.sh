#!/bin/bash
# Setup script to build the original Zimtohrli binary for comparison testing

set -e

echo "🔧 Setting up original Zimtohrli binary for comparison testing..."

# Check if we're already in a zimtohrli directory
if [[ "$(basename $(pwd))" == "zimtohrli-python" ]]; then
    cd ..
fi

# Clone or update original Zimtohrli repository
if [[ ! -d "zimtohrli" ]]; then
    echo "📥 Cloning original Zimtohrli repository..."
    git clone https://github.com/google/zimtohrli.git
    cd zimtohrli
else
    echo "📂 Found existing Zimtohrli repository, updating..."
    cd zimtohrli
    git pull origin main
fi

echo "🔍 Current directory: $(pwd)"

# Check for build systems
echo "🛠️  Checking available build systems..."

BUILD_METHOD=""

# Try Bazel first (preferred)
if command -v bazel &> /dev/null; then
    echo "✅ Bazel found - using Bazel build"
    BUILD_METHOD="bazel"
elif command -v cmake &> /dev/null; then
    echo "✅ CMake found - using CMake build"
    BUILD_METHOD="cmake"
else
    echo "❌ No suitable build system found"
    echo "Please install either:"
    echo "  - Bazel: https://bazel.build/install"
    echo "  - CMake: sudo apt install cmake (Ubuntu) or brew install cmake (macOS)"
    exit 1
fi

# Build using the available method
if [[ "$BUILD_METHOD" == "bazel" ]]; then
    echo "🔨 Building Zimtohrli with Bazel..."
    
    # Build the main zimtohrli binary
    bazel build //cpp/zimtohrli:zimtohrli
    
    BINARY_PATH="$(pwd)/bazel-bin/cpp/zimtohrli/zimtohrli"
    
elif [[ "$BUILD_METHOD" == "cmake" ]]; then
    echo "🔨 Building Zimtohrli with CMake..."
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Configure with CMake
    cmake .. -DCMAKE_BUILD_TYPE=Release
    
    # Build
    make -j$(nproc)
    
    BINARY_PATH="$(pwd)/cpp/zimtohrli/zimtohrli"
fi

# Verify the binary was built
if [[ -f "$BINARY_PATH" ]]; then
    echo "✅ Zimtohrli binary built successfully!"
    echo "📍 Binary location: $BINARY_PATH"
    
    # Test the binary
    echo "🧪 Testing binary..."
    if "$BINARY_PATH" --version; then
        echo "✅ Binary is working correctly"
    else
        echo "⚠️  Binary built but version check failed"
    fi
    
    # Create a symlink in the python directory for convenience
    PYTHON_DIR="$(dirname $(pwd))/zimtohrli-python"
    if [[ -d "$PYTHON_DIR" ]]; then
        SYMLINK_PATH="$PYTHON_DIR/zimtohrli_binary"
        ln -sf "$BINARY_PATH" "$SYMLINK_PATH"
        echo "🔗 Created symlink: $SYMLINK_PATH -> $BINARY_PATH"
        echo "💡 You can now run: python compare_implementations.py --binary-path ./zimtohrli_binary"
    fi
    
else
    echo "❌ Build failed - binary not found at expected location: $BINARY_PATH"
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now run comparison tests."
echo ""
echo "Usage examples:"
echo "  cd ../zimtohrli-python"
echo "  python compare_implementations.py --binary-path $BINARY_PATH"
echo "  python compare_implementations.py --binary-path ./zimtohrli_binary"
echo ""