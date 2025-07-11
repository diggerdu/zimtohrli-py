#!/bin/bash

# Offline installation script for Zimtohrli Python binding
# This avoids network issues by using system dependencies only

set -e

echo "🔧 Zimtohrli Offline Installation"
echo "================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in the right directory
if [[ ! -f "setup_system_deps.py" ]]; then
    echo "❌ Error: setup_system_deps.py not found"
    echo "Please run this script from the zimtohrli-py directory"
    exit 1
fi

echo "📋 Step 1: Checking system dependencies..."

# Check basic tools
missing_tools=()
for tool in cmake pkg-config gcc g++; do
    if command_exists "$tool"; then
        echo "✅ $tool found"
    else
        echo "❌ $tool missing"
        missing_tools+=("$tool")
    fi
done

# Check pkg-config libraries
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

# Suggest installation commands if dependencies missing
if [[ ${#missing_tools[@]} -gt 0 ]] || [[ ${#missing_libs[@]} -gt 0 ]]; then
    echo ""
    echo "🚨 Missing dependencies detected!"
    echo ""
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo "Missing tools: ${missing_tools[*]}"
    fi
    
    if [[ ${#missing_libs[@]} -gt 0 ]]; then
        echo "Missing libraries: ${missing_libs[*]}"
    fi
    
    echo ""
    echo "Install them with:"
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
    exit 1
fi

echo ""
echo "🏗️  Step 2: Building with system dependencies..."

# Try building with system dependencies
if python setup_system_deps.py build_ext --inplace; then
    echo ""
    echo "✅ Build successful!"
    
    echo ""
    echo "🧪 Step 3: Testing installation..."
    
    # Test the installation
    if python -c "import zimtohrli_py; print('✅ Import successful')"; then
        echo ""
        echo "🎉 Installation completed successfully!"
        echo ""
        echo "You can now use zimtohrli_py:"
        echo "  python -c \"import zimtohrli_py; print('Zimtohrli ready!')\""
        echo ""
        echo "For comprehensive testing, run:"
        echo "  python verify_install.py"
        
    else
        echo "❌ Import test failed"
        echo "Try running: python verify_install.py"
        exit 1
    fi
    
else
    echo ""
    echo "❌ Build failed!"
    echo ""
    echo "Try debugging with:"
    echo "  python debug_install.py"
    echo ""
    echo "Or check the detailed build log above for specific errors."
    exit 1
fi

echo ""
echo "📚 Next steps:"
echo "  - Run tests: python verify_install.py"
echo "  - See usage examples in README.md"
echo "  - Check TROUBLESHOOTING.md for any issues"