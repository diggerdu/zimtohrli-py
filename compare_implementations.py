#!/usr/bin/env python3
"""
Compare results between original Zimtohrli binary and Python binding.

This script generates test audio files, runs both implementations,
and verifies that they produce identical results.
"""

import os
import sys
import subprocess
import tempfile
import numpy as np
import json
from pathlib import Path
import soundfile as sf
from typing import Tuple, List, Dict, Any
import argparse

try:
    import zimtohrli_py as zimtohrli
except ImportError:
    print("❌ zimtohrli_py not found. Please install the Python binding first.")
    sys.exit(1)


class ZimtohrliComparison:
    """Compare original Zimtohrli binary with Python binding."""
    
    def __init__(self, binary_path: str = None):
        """Initialize with path to original zimtohrli binary."""
        self.binary_path = binary_path or self.find_zimtohrli_binary()
        self.temp_dir = None
        self.test_results = []
        
    def find_zimtohrli_binary(self) -> str:
        """Try to find the zimtohrli binary in common locations."""
        possible_paths = [
            "zimtohrli",
            "./zimtohrli", 
            "../zimtohrli",
            "/usr/local/bin/zimtohrli",
            os.path.expanduser("~/zimtohrli/bazel-bin/cpp/zimtohrli/zimtohrli"),
            os.path.expanduser("~/zimtohrli/build/cpp/zimtohrli/zimtohrli"),
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Found zimtohrli binary: {path}")
                    return path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
                
        print("❌ Zimtohrli binary not found. Please specify path with --binary-path")
        print("   You can build it from: https://github.com/google/zimtohrli")
        print("   Typical locations:")
        for path in possible_paths:
            print(f"     {path}")
        sys.exit(1)
        
    def setup_temp_directory(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp(prefix="zimtohrli_comparison_")
        print(f"📁 Using temp directory: {self.temp_dir}")
        
    def cleanup_temp_directory(self):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory")
            
    def generate_test_audio(self, duration: float = 1.0, sample_rate: int = 48000) -> List[Tuple[str, np.ndarray, str]]:
        """Generate various test audio signals."""
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        
        test_cases = [
            # Pure tones
            ("sine_1000hz", np.sin(2 * np.pi * 1000 * t), "1kHz sine wave"),
            ("sine_440hz", np.sin(2 * np.pi * 440 * t), "440Hz sine wave"),
            ("sine_2000hz", np.sin(2 * np.pi * 2000 * t), "2kHz sine wave"),
            
            # Complex signals
            ("chirp", np.sin(2 * np.pi * t * (1000 + 500 * t)), "Linear chirp 1-1.5kHz"),
            ("multi_tone", 
             0.3 * np.sin(2 * np.pi * 440 * t) + 
             0.3 * np.sin(2 * np.pi * 880 * t) + 
             0.3 * np.sin(2 * np.pi * 1320 * t),
             "Multi-tone (440+880+1320 Hz)"),
            
            # Noise signals
            ("white_noise", np.random.normal(0, 0.1, len(t)).astype(np.float32), "White noise"),
            ("pink_noise", self._generate_pink_noise(len(t)), "Pink noise"),
            
            # Modified signals (for comparison testing)
            ("sine_1000hz_quiet", 0.5 * np.sin(2 * np.pi * 1000 * t), "1kHz sine wave (quieter)"),
            ("sine_1000hz_noisy", 
             np.sin(2 * np.pi * 1000 * t) + 0.05 * np.random.normal(0, 1, len(t)).astype(np.float32),
             "1kHz sine wave + noise"),
             
            # Silence and extremes
            ("silence", np.zeros(len(t), dtype=np.float32), "Silence"),
        ]
        
        return test_cases
        
    def _generate_pink_noise(self, num_samples: int) -> np.ndarray:
        """Generate pink noise (1/f noise)."""
        # Simple pink noise generation using FFT
        white_noise = np.random.normal(0, 1, num_samples)
        fft = np.fft.fft(white_noise)
        
        # Apply 1/f filter
        freqs = np.fft.fftfreq(num_samples)
        freqs[0] = 1e-10  # Avoid division by zero
        pink_filter = 1 / np.sqrt(np.abs(freqs))
        pink_filter[0] = 1  # DC component
        
        pink_fft = fft * pink_filter
        pink_noise = np.real(np.fft.ifft(pink_fft))
        
        # Normalize
        pink_noise = pink_noise / np.max(np.abs(pink_noise)) * 0.1
        return pink_noise.astype(np.float32)
        
    def save_audio_files(self, test_cases: List[Tuple[str, np.ndarray, str]], 
                        sample_rate: int = 48000) -> Dict[str, str]:
        """Save test audio to WAV files."""
        file_paths = {}
        
        for name, audio, description in test_cases:
            file_path = os.path.join(self.temp_dir, f"{name}.wav")
            sf.write(file_path, audio, sample_rate)
            file_paths[name] = file_path
            print(f"💾 Saved: {name}.wav ({description})")
            
        return file_paths
        
    def run_binary_comparison(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """Run original zimtohrli binary and parse results."""
        try:
            # Run zimtohrli binary
            cmd = [self.binary_path, file_a, file_b]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Binary failed: {result.stderr}",
                    "distance": None,
                    "mos": None
                }
                
            # Parse output - zimtohrli typically outputs distance as the last number
            output_lines = result.stdout.strip().split('\n')
            distance = None
            
            for line in output_lines:
                # Look for distance value (typically the main output)
                try:
                    # Try to parse as a float (distance value)
                    if line.strip() and not line.startswith('#'):
                        distance = float(line.strip())
                        break
                except ValueError:
                    continue
                    
            if distance is None:
                return {
                    "success": False,
                    "error": f"Could not parse distance from output: {result.stdout}",
                    "distance": None,
                    "mos": None
                }
                
            # Convert distance to MOS using the same formula as Python binding
            mos = zimtohrli.zimtohrli_distance_to_mos(distance)
            
            return {
                "success": True,
                "distance": distance,
                "mos": mos,
                "raw_output": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Binary execution timed out",
                "distance": None,
                "mos": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception running binary: {e}",
                "distance": None,
                "mos": None
            }
            
    def run_python_comparison(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """Run Python binding comparison."""
        try:
            # Use the high-level API that handles file loading
            mos = zimtohrli.load_and_compare_audio_files(file_a, file_b, return_distance=False)
            distance = zimtohrli.load_and_compare_audio_files(file_a, file_b, return_distance=True)
            
            return {
                "success": True,
                "distance": distance,
                "mos": mos
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Python binding failed: {e}",
                "distance": None,
                "mos": None
            }
            
    def compare_pair(self, name_a: str, name_b: str, file_paths: Dict[str, str]) -> Dict[str, Any]:
        """Compare a pair of audio files using both implementations."""
        file_a = file_paths[name_a]
        file_b = file_paths[name_b]
        
        print(f"\n🔍 Comparing: {name_a} vs {name_b}")
        
        # Run both implementations
        binary_result = self.run_binary_comparison(file_a, file_b)
        python_result = self.run_python_comparison(file_a, file_b)
        
        # Analyze results
        comparison = {
            "pair": f"{name_a}_vs_{name_b}",
            "binary": binary_result,
            "python": python_result,
            "match": False,
            "distance_diff": None,
            "mos_diff": None,
            "tolerance_met": False
        }
        
        if binary_result["success"] and python_result["success"]:
            distance_diff = abs(binary_result["distance"] - python_result["distance"])
            mos_diff = abs(binary_result["mos"] - python_result["mos"])
            
            comparison["distance_diff"] = distance_diff
            comparison["mos_diff"] = mos_diff
            
            # Define tolerances (zimtohrli is deterministic, so differences should be tiny)
            distance_tolerance = 1e-6
            mos_tolerance = 1e-4
            
            tolerance_met = (distance_diff <= distance_tolerance and mos_diff <= mos_tolerance)
            comparison["tolerance_met"] = tolerance_met
            comparison["match"] = tolerance_met
            
            print(f"   Binary:  distance={binary_result['distance']:.8f}, MOS={binary_result['mos']:.6f}")
            print(f"   Python:  distance={python_result['distance']:.8f}, MOS={python_result['mos']:.6f}")
            print(f"   Diff:    Δdistance={distance_diff:.2e}, ΔMOS={mos_diff:.2e}")
            print(f"   Status:  {'✅ MATCH' if tolerance_met else '❌ MISMATCH'}")
            
        else:
            print(f"   Status:  ❌ ERROR")
            if not binary_result["success"]:
                print(f"     Binary error: {binary_result['error']}")
            if not python_result["success"]:
                print(f"     Python error: {python_result['error']}")
                
        return comparison
        
    def run_comprehensive_comparison(self) -> Dict[str, Any]:
        """Run comprehensive comparison between implementations."""
        print("🧪 Starting comprehensive comparison between Zimtohrli implementations")
        print(f"   Binary: {self.binary_path}")
        print(f"   Python: zimtohrli_py v{getattr(zimtohrli, '__version__', 'unknown')}")
        
        # Setup
        self.setup_temp_directory()
        
        try:
            # Generate test audio
            print("\n📊 Generating test audio...")
            test_cases = self.generate_test_audio()
            file_paths = self.save_audio_files(test_cases)
            
            # Define comparison pairs
            comparison_pairs = [
                # Identical signals (should have distance ≈ 0)
                ("sine_1000hz", "sine_1000hz"),
                ("white_noise", "white_noise"),
                ("silence", "silence"),
                
                # Different signals
                ("sine_1000hz", "sine_440hz"),
                ("sine_1000hz", "sine_2000hz"),
                ("sine_440hz", "sine_2000hz"),
                
                # Signal vs modified version
                ("sine_1000hz", "sine_1000hz_quiet"),
                ("sine_1000hz", "sine_1000hz_noisy"),
                
                # Complex signals
                ("sine_1000hz", "chirp"),
                ("sine_1000hz", "multi_tone"),
                ("white_noise", "pink_noise"),
                ("multi_tone", "chirp"),
                
                # Silence comparisons
                ("silence", "sine_1000hz"),
                ("silence", "white_noise"),
            ]
            
            # Run comparisons
            print(f"\n🔬 Running {len(comparison_pairs)} comparison pairs...")
            results = []
            
            for name_a, name_b in comparison_pairs:
                result = self.compare_pair(name_a, name_b, file_paths)
                results.append(result)
                self.test_results.append(result)
                
            # Analyze overall results
            successful_comparisons = [r for r in results if r["binary"]["success"] and r["python"]["success"]]
            matching_comparisons = [r for r in successful_comparisons if r["match"]]
            
            summary = {
                "total_pairs": len(comparison_pairs),
                "successful_pairs": len(successful_comparisons),
                "matching_pairs": len(matching_comparisons),
                "success_rate": len(successful_comparisons) / len(comparison_pairs),
                "match_rate": len(matching_comparisons) / len(successful_comparisons) if successful_comparisons else 0,
                "results": results
            }
            
            return summary
            
        finally:
            self.cleanup_temp_directory()
            
    def print_summary(self, summary: Dict[str, Any]):
        """Print comparison summary."""
        print("\n" + "="*60)
        print("📋 COMPARISON SUMMARY")
        print("="*60)
        
        print(f"Total comparison pairs: {summary['total_pairs']}")
        print(f"Successful comparisons: {summary['successful_pairs']}")
        print(f"Matching results: {summary['matching_pairs']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Match rate: {summary['match_rate']:.1%}")
        
        if summary['match_rate'] == 1.0 and summary['success_rate'] == 1.0:
            print("\n🎉 PERFECT MATCH! Python binding produces identical results to original binary.")
        elif summary['match_rate'] >= 0.95:
            print(f"\n✅ EXCELLENT! {summary['match_rate']:.1%} of comparisons match within tolerance.")
        elif summary['match_rate'] >= 0.8:
            print(f"\n⚠️  GOOD: {summary['match_rate']:.1%} of comparisons match, but some differences found.")
        else:
            print(f"\n❌ ISSUES: Only {summary['match_rate']:.1%} of comparisons match. Significant differences detected.")
            
        # Show failures
        failures = [r for r in summary['results'] if not r.get('match', False)]
        if failures:
            print(f"\n❌ Failed/mismatched comparisons ({len(failures)}):")
            for failure in failures:
                print(f"   {failure['pair']}")
                if not failure['binary']['success']:
                    print(f"     Binary error: {failure['binary']['error']}")
                if not failure['python']['success']:
                    print(f"     Python error: {failure['python']['error']}")
                if failure.get('distance_diff'):
                    print(f"     Distance diff: {failure['distance_diff']:.2e}")
                    
        print("\n" + "="*60)
        
    def save_detailed_report(self, summary: Dict[str, Any], output_file: str = "zimtohrli_comparison_report.json"):
        """Save detailed comparison report to JSON file."""
        report = {
            "comparison_metadata": {
                "binary_path": self.binary_path,
                "python_version": getattr(zimtohrli, '__version__', 'unknown'),
                "timestamp": str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip()),
                "total_pairs": summary['total_pairs'],
                "successful_pairs": summary['successful_pairs'],
                "matching_pairs": summary['matching_pairs'],
                "success_rate": summary['success_rate'],
                "match_rate": summary['match_rate']
            },
            "detailed_results": summary['results']
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📄 Detailed report saved to: {output_file}")


def main():
    """Main function to run the comparison."""
    parser = argparse.ArgumentParser(description="Compare Zimtohrli binary with Python binding")
    parser.add_argument("--binary-path", help="Path to original zimtohrli binary")
    parser.add_argument("--output-report", default="zimtohrli_comparison_report.json", 
                       help="Output file for detailed report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        # Create comparison instance
        comparison = ZimtohrliComparison(binary_path=args.binary_path)
        
        # Run comprehensive comparison
        summary = comparison.run_comprehensive_comparison()
        
        # Print results
        comparison.print_summary(summary)
        
        # Save detailed report
        comparison.save_detailed_report(summary, args.output_report)
        
        # Exit with appropriate code
        if summary['match_rate'] == 1.0 and summary['success_rate'] == 1.0:
            print("\n✅ All tests passed! Implementations are identical.")
            sys.exit(0)
        else:
            print(f"\n⚠️  Some tests failed or showed differences.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Comparison interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()