#!/bin/bash

# Debug installation script for Zimtohrli Python binding

set -e  # Exit on any error

echo "🐛 Zimtohrli Debug Installation Script"
echo "======================================"

# Function to run command with timeout and logging
run_with_timeout() {
    local timeout=$1
    local description=$2
    shift 2
    
    echo "⏳ $description..."
    echo "Command: $@"
    
    if timeout $timeout "$@"; then
        echo "✅ Success: $description"
        return 0
    else
        echo "❌ Failed: $description"
        return 1
    fi
}

# Check system dependencies
echo "🔍 Step 1: Checking system dependencies..."
python3 debug_install.py

# Try installation with different methods
echo ""
echo "🔧 Step 2: Attempting installation methods..."

# Method 1: Standard installation with verbose output
echo ""
echo "Method 1: Standard pip install with verbose output"
echo "================================================="
if run_with_timeout 600 "Standard installation" pip install -v .; then
    echo "✅ Standard installation succeeded!"
    exit 0
fi

# Method 2: Single-threaded build
echo ""
echo "Method 2: Single-threaded build (slower but more stable)"
echo "======================================================="
export CMAKE_BUILD_PARALLEL_LEVEL=1
if run_with_timeout 900 "Single-threaded build" pip install .; then
    echo "✅ Single-threaded installation succeeded!"
    exit 0
fi

# Method 3: Debug build
echo ""
echo "Method 3: Debug build with extra logging"
echo "========================================"
export DEBUG=1
export CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Debug -DCMAKE_VERBOSE_MAKEFILE=ON"
if run_with_timeout 900 "Debug build" pip install .; then
    echo "✅ Debug installation succeeded!"
    exit 0
fi

# Method 4: Manual build steps
echo ""
echo "Method 4: Manual build for debugging"
echo "===================================="

# Create build directory
mkdir -p manual_build
cd manual_build

# Configure with CMake manually
echo "Manual CMake configuration..."
if run_with_timeout 300 "CMake configure" cmake ../zimtohrli_py/src -DCMAKE_VERBOSE_MAKEFILE=ON; then
    echo "✅ CMake configuration successful"
    
    # Build manually
    echo "Manual build..."
    if run_with_timeout 600 "Manual build" make VERBOSE=1; then
        echo "✅ Manual build successful"
        echo "Check the build output above for any warnings or issues."
    else
        echo "❌ Manual build failed"
        echo "Check the detailed build output above for specific errors."
    fi
else
    echo "❌ CMake configuration failed"
    echo "This indicates missing dependencies or configuration issues."
fi

cd ..

echo ""
echo "🏁 Installation Debugging Complete"
echo "================================="
echo ""
echo "If all methods failed, please:"
echo "1. Check the detailed error messages above"
echo "2. Install missing system dependencies"
echo "3. Consider using conda for dependency management:"
echo "   conda install -c conda-forge cmake pkg-config libflac libvorbis libogg libopus soxr"
echo "4. Report the issue with the full log output"