#!/usr/bin/env python3
"""Test importing the built extension."""

import sys
import os
from pathlib import Path

def test_import():
    """Test importing the zimtohrli extension."""
    print("=== Testing Extension Import ===")
    print()
    
    # Add the zimtohrli_py directory to the path
    zimtohrli_dir = Path(__file__).parent.parent / "zimtohrli_py"
    sys.path.insert(0, str(zimtohrli_dir))
    
    print(f"Added to path: {zimtohrli_dir}")
    print(f"Extension file exists: {(zimtohrli_dir / '_zimtohrli.cpython-312-x86_64-linux-gnu.so').exists()}")
    print()
    
    try:
        print("Attempting to import _zimtohrli...")
        import _zimtohrli
        print("✅ Successfully imported _zimtohrli!")
        
        # Test some basic functionality if available
        print(f"Module: {_zimtohrli}")
        print(f"Module file: {getattr(_zimtohrli, '__file__', 'N/A')}")
        
        # Try to get module attributes
        attrs = [attr for attr in dir(_zimtohrli) if not attr.startswith('_')]
        print(f"Available functions/attributes: {attrs}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import _zimtohrli: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_zimtohrli_py():
    """Test importing the main zimtohrli_py module."""
    print("\n=== Testing Main Module Import ===")
    print()
    
    try:
        print("Attempting to import zimtohrli_py...")
        import zimtohrli_py
        print("✅ Successfully imported zimtohrli_py!")
        
        print(f"Module: {zimtohrli_py}")
        print(f"Module file: {getattr(zimtohrli_py, '__file__', 'N/A')}")
        
        # Check if the core functions are available
        if hasattr(zimtohrli_py, 'compute_zimtohrli'):
            print("✅ compute_zimtohrli function found!")
        else:
            print("⚠️  compute_zimtohrli function not found")
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import zimtohrli_py: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_import()
    success2 = test_zimtohrli_py()
    
    if success1 and success2:
        print("\n🎉 All import tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some import tests failed!")
        sys.exit(1)