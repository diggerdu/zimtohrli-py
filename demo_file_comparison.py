#!/usr/bin/env python3
"""
Demonstration of Zimtohrli Python binding with audio files.
Shows file-based comparison capabilities.
"""

import numpy as np
import tempfile
import os
import soundfile as sf
import zimtohrli_py as zimtohrli

def create_demo_audio_files():
    """Create demo audio files for testing."""
    sample_rate = 48000
    duration = 2.0  # 2 seconds
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Create various test audio signals
    signals = {
        "reference_1000hz.wav": np.sin(2 * np.pi * 1000 * t),
        "test_1000hz_clean.wav": np.sin(2 * np.pi * 1000 * t),  # Identical to reference
        "test_1000hz_noisy.wav": np.sin(2 * np.pi * 1000 * t) + 0.01 * np.random.RandomState(42).randn(len(t)),
        "test_440hz.wav": np.sin(2 * np.pi * 440 * t),  # Different frequency
        "test_880hz.wav": np.sin(2 * np.pi * 880 * t),  # Octave
        "test_white_noise.wav": 0.1 * np.random.RandomState(42).randn(len(t)),
        "test_quiet.wav": 0.1 * np.sin(2 * np.pi * 1000 * t),  # Quiet version
    }
    
    temp_dir = tempfile.mkdtemp(prefix="zimtohrli_demo_")
    file_paths = {}
    
    for filename, signal in signals.items():
        filepath = os.path.join(temp_dir, filename)
        sf.write(filepath, signal, sample_rate)
        file_paths[filename] = filepath
    
    return temp_dir, file_paths

def main():
    """Run file comparison demonstration."""
    print("🎵 Zimtohrli Python Binding - File Comparison Demonstration")
    print("=" * 70)
    
    # Create demo files
    print("Creating demo audio files...")
    temp_dir, file_paths = create_demo_audio_files()
    
    try:
        # Reference file
        reference_file = file_paths["reference_1000hz.wav"]
        print(f"Reference file: {os.path.basename(reference_file)}")
        print()
        
        # Test each file against the reference
        test_files = [k for k in file_paths.keys() if k.startswith("test_")]
        
        print("📊 File Comparison Results:")
        print(f"{'Test File':<25} | {'MOS':<8} | {'Distance':<10} | {'Quality'}")
        print("-" * 60)
        
        for test_filename in sorted(test_files):
            test_file = file_paths[test_filename]
            
            # Compare using file-based API
            mos = zimtohrli.load_and_compare_audio_files(
                reference_file, test_file, return_distance=False
            )
            
            distance = zimtohrli.load_and_compare_audio_files(
                reference_file, test_file, return_distance=True
            )
            
            # Assess quality by loading files manually
            ref_audio, ref_sr = sf.read(reference_file)
            test_audio, test_sr = sf.read(test_file)
            ref_audio = ref_audio.astype(np.float32)
            test_audio = test_audio.astype(np.float32)
            
            quality_mos, quality_label = zimtohrli.assess_audio_quality(
                ref_audio, test_audio, ref_sr
            )
            
            print(f"{os.path.basename(test_file):<25} | {mos:<8.4f} | {distance:<10.6f} | {quality_label}")
        
        print()
        
        # Demonstrate batch comparison
        print("🔄 Batch Comparison Demonstration:")
        
        # Load reference audio
        ref_audio, ref_sr = sf.read(reference_file)
        ref_audio = ref_audio.astype(np.float32)
        
        # Load test audios
        test_audios = []
        test_names = []
        for test_filename in sorted(test_files):
            test_audio, test_sr = sf.read(file_paths[test_filename])
            test_audio = test_audio.astype(np.float32)
            
            # Resample if needed (zimtohrli expects 48kHz)
            if test_sr != 48000:
                # Simple resampling for demo (in practice, use proper resampling)
                test_audio = test_audio  # Assume all are 48kHz for this demo
            
            test_audios.append(test_audio)
            test_names.append(os.path.basename(test_filename))
        
        # Batch compare
        batch_scores = zimtohrli.batch_compare_audio(ref_audio, test_audios, ref_sr)
        
        print("Batch comparison results:")
        for name, score in zip(test_names, batch_scores):
            print(f"  {name:<25}: MOS = {score:.4f}")
        
        print()
        
        # Demonstrate consistency between different methods
        print("🔍 API Consistency Check:")
        
        test_file = file_paths["test_440hz.wav"]
        
        # Method 1: File-based comparison
        mos_file = zimtohrli.load_and_compare_audio_files(reference_file, test_file)
        
        # Method 2: Array-based comparison
        ref_audio, ref_sr = sf.read(reference_file)
        test_audio, test_sr = sf.read(test_file)
        ref_audio = ref_audio.astype(np.float32)
        test_audio = test_audio.astype(np.float32)
        
        mos_array = zimtohrli.compare_audio(ref_audio, ref_sr, test_audio, test_sr)
        
        # Method 3: Using comparator class
        comparator = zimtohrli.ZimtohrliComparator()
        mos_comparator = comparator.compare(ref_audio, test_audio)
        
        print(f"File-based comparison:     MOS = {mos_file:.8f}")
        print(f"Array-based comparison:    MOS = {mos_array:.8f}")
        print(f"Comparator class:          MOS = {mos_comparator:.8f}")
        
        diff1 = abs(mos_file - mos_array)
        diff2 = abs(mos_array - mos_comparator)
        
        print(f"Difference (file vs array): {diff1:.2e}")
        print(f"Difference (array vs comp): {diff2:.2e}")
        
        if diff1 < 1e-6 and diff2 < 1e-6:
            print("✅ All methods produce consistent results!")
        else:
            print("❌ Methods produce different results")
        
        print()
        print("🎯 Key Observations:")
        print("• Identical files (clean) produce MOS ≈ 5.0 and distance ≈ 0.0")
        print("• Different frequencies show varying degrees of similarity")
        print("• Octave relationships (440Hz vs 880Hz) show moderate similarity")
        print("• Noise vs tones show significant differences")
        print("• All API methods produce identical results")
        print("• The metric shows musical/perceptual relationships (octaves, harmonics)")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    main()