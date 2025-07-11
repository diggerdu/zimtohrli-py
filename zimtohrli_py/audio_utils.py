"""
Audio utility functions for Zimtohrli.

This module provides convenience functions for loading and processing audio files.
Requires optional dependencies: soundfile, librosa
"""

from typing import Union, Tuple
from .core import compare_audio


def load_and_compare_audio_files(file_a: str, file_b: str, return_distance: bool = False) -> float:
    """
    Load two audio files and compare them using Zimtohrli.
    
    Note: Requires librosa or soundfile for loading audio files.
    
    Args:
        file_a: Path to first audio file
        file_b: Path to second audio file  
        return_distance: If True, return raw distance. If False, return MOS.
        
    Returns:
        float: Either MOS score or raw distance
        
    Raises:
        ImportError: If librosa is not available
        
    Example:
        >>> mos = load_and_compare_audio_files("reference.wav", "compressed.wav")
        >>> print(f"Audio quality MOS: {mos:.3f}")
    """
    try:
        import librosa
        
        # Load audio files
        audio_a, sr_a = librosa.load(file_a, sr=None)
        audio_b, sr_b = librosa.load(file_b, sr=None)
        
        return compare_audio(audio_a, float(sr_a), audio_b, float(sr_b), return_distance)
        
    except ImportError:
        try:
            import soundfile as sf
            
            # Load audio files with soundfile
            audio_a, sr_a = sf.read(file_a)
            audio_b, sr_b = sf.read(file_b)
            
            return compare_audio(audio_a, float(sr_a), audio_b, float(sr_b), return_distance)
            
        except ImportError:
            raise ImportError(
                "Audio file loading requires either librosa or soundfile. "
                "Install with: pip install librosa  or  pip install soundfile"
            )


def assess_audio_quality(reference: "np.ndarray", test_audio: "np.ndarray", 
                        sample_rate: float) -> Tuple[float, str]:
    """
    Assess audio quality using Zimtohrli MOS with qualitative description.
    
    Args:
        reference: Reference audio array
        test_audio: Test audio array to evaluate
        sample_rate: Sample rate of both audio arrays
        
    Returns:
        tuple: (MOS score, quality description)
        
    Example:
        >>> import numpy as np
        >>> reference = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 48000)).astype(np.float32)
        >>> compressed = reference + np.random.normal(0, 0.01, len(reference)).astype(np.float32)
        >>> mos, quality = assess_audio_quality(reference, compressed, 48000)
        >>> print(f"Audio Quality: {quality} (MOS: {mos:.3f})")
    """
    mos = compare_audio(reference, sample_rate, test_audio, sample_rate)
    
    if mos >= 4.5:
        quality = "Excellent"
    elif mos >= 4.0:
        quality = "Good"
    elif mos >= 3.0:
        quality = "Fair"
    elif mos >= 2.0:
        quality = "Poor"
    else:
        quality = "Bad"
    
    return mos, quality


def batch_compare_audio(reference_audio: "np.ndarray", test_audios: list, 
                       sample_rate: float) -> list:
    """
    Compare a reference audio against multiple test audios efficiently.
    
    Args:
        reference_audio: Reference audio array
        test_audios: List of test audio arrays
        sample_rate: Sample rate of all audio arrays
        
    Returns:
        list: List of MOS scores for each comparison
        
    Example:
        >>> reference = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 48000)).astype(np.float32)
        >>> test_audios = [generate_test_audio() for _ in range(10)]
        >>> scores = batch_compare_audio(reference, test_audios, 48000)
        >>> print(f"Average MOS: {np.mean(scores):.3f}")
    """
    from .core import ZimtohrliComparator
    
    # Use comparator for efficiency if all at 48kHz
    if sample_rate == 48000:
        comparator = ZimtohrliComparator()
        return [comparator.compare(reference_audio, test_audio) for test_audio in test_audios]
    else:
        # Use high-level function with resampling
        return [compare_audio(reference_audio, sample_rate, test_audio, sample_rate) 
                for test_audio in test_audios]