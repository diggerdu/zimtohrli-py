#!/usr/bin/env python3
"""
Create a command-line wrapper for our Python binding that mimics the original binary.

This creates a zimtohrli_binary script that behaves exactly like the original
C++ binary, allowing us to do proper comparison testing.
"""

import sys
import argparse
import os
from pathlib import Path

# Import our Python binding
try:
    import zimtohrli_py as zimtohrli
except ImportError:
    print("Error: zimtohrli_py not found. Please install: pip install .", file=sys.stderr)
    sys.exit(1)

try:
    import soundfile as sf
except ImportError:
    print("Error: soundfile not found. Please install: pip install soundfile", file=sys.stderr)
    sys.exit(1)


def main():
    """Main function that mimics the original zimtohrli binary interface."""
    
    parser = argparse.ArgumentParser(description="Zimtohrli audio comparison tool (Python binding wrapper)")
    parser.add_argument("--path_a", required=True, help="Reference audio file")
    parser.add_argument("--path_b", required=True, action='append', help="Comparison audio file(s)")
    parser.add_argument("--output_zimtohrli_distance", action='store_true', 
                       help="Output raw distance instead of MOS")
    parser.add_argument("--verbose", action='store_true', help="Verbose output")
    
    args = parser.parse_args()
    
    # Load reference file
    try:
        audio_a, sr_a = sf.read(args.path_a)
        if args.verbose:
            duration = len(audio_a) / sr_a
            print(f"Loaded {args.path_a} (1x{len(audio_a)}@{sr_a}Hz, {duration:.3f}s)", file=sys.stderr)
    except Exception as e:
        print(f"Error loading {args.path_a}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process each comparison file
    for path_b in args.path_b:
        try:
            audio_b, sr_b = sf.read(path_b)
            if args.verbose:
                duration = len(audio_b) / sr_b
                print(f"Loaded {path_b} (1x{len(audio_b)}@{sr_b}Hz, {duration:.3f}s)", file=sys.stderr)
        except Exception as e:
            print(f"Error loading {path_b}: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Ensure single channel (take first channel if stereo)
        if len(audio_a.shape) > 1:
            audio_a = audio_a[:, 0]
        if len(audio_b.shape) > 1:
            audio_b = audio_b[:, 0]
        
        # Compare using our Python binding
        try:
            if args.output_zimtohrli_distance:
                result = zimtohrli.compare_audio(audio_a, sr_a, audio_b, sr_b, return_distance=True)
            else:
                result = zimtohrli.compare_audio(audio_a, sr_a, audio_b, sr_b, return_distance=False)
            
            # Output in same format as original binary
            print(f"{result}")
            
        except Exception as e:
            print(f"Error comparing {args.path_a} vs {path_b}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()