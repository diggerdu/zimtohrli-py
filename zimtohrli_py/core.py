"""
Core functionality for Zimtohrli Python binding.

This module provides the main interface to the Zimtohrli C++ library.
"""

import numpy as np
from typing import Union

try:
    from ._zimtohrli import (
        Pyohrli as _ZimtohrliCore,
        compare_audio_arrays as _compare_audio_arrays,
        compare_audio_arrays_distance as _compare_audio_arrays_distance,
        MOSFromZimtohrli as _mos_from_zimtohrli,
    )
except ImportError as e:
    raise ImportError(
        f"Failed to import Zimtohrli C++ extension: {e}. "
        "Make sure the package was installed correctly with all dependencies."
    ) from e


def compare_audio(
    audio_a: np.ndarray, 
    sample_rate_a: float, 
    audio_b: np.ndarray, 
    sample_rate_b: float,
    return_distance: bool = False
) -> float:
    """
    Compare two audio arrays using the Zimtohrli perceptual similarity metric.
    
    Args:
        audio_a: First audio array (1D numpy array of float32)
        sample_rate_a: Sample rate of first audio in Hz
        audio_b: Second audio array (1D numpy array of float32)  
        sample_rate_b: Sample rate of second audio in Hz
        return_distance: If True, return raw Zimtohrli distance (0-1).
                        If False, return MOS score (1-5).
    
    Returns:
        float: Either MOS score (1-5, higher is better) or Zimtohrli distance (0-1, lower is better)
        
    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If comparison fails
        
    Example:
        >>> import numpy as np
        >>> import zimtohrli_py as zimtohrli
        >>> audio_a = np.sin(2 * np.pi * 1000 * np.linspace(0, 1, 48000)).astype(np.float32)
        >>> audio_b = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 48000)).astype(np.float32)
        >>> mos = zimtohrli.compare_audio(audio_a, 48000, audio_b, 48000)
        >>> print(f"MOS: {mos:.3f}")
    """
    # Validate inputs
    if not isinstance(audio_a, np.ndarray) or not isinstance(audio_b, np.ndarray):
        raise ValueError("Audio inputs must be numpy arrays")
    
    if audio_a.ndim != 1 or audio_b.ndim != 1:
        raise ValueError("Audio arrays must be 1-dimensional")
        
    if len(audio_a) == 0 or len(audio_b) == 0:
        raise ValueError("Audio arrays cannot be empty")
    
    # Convert to float32 if needed
    if audio_a.dtype != np.float32:
        audio_a = audio_a.astype(np.float32)
    if audio_b.dtype != np.float32:
        audio_b = audio_b.astype(np.float32)
    
    # Ensure arrays are contiguous
    if not audio_a.flags['C_CONTIGUOUS']:
        audio_a = np.ascontiguousarray(audio_a)
    if not audio_b.flags['C_CONTIGUOUS']:
        audio_b = np.ascontiguousarray(audio_b)
    
    # Validate sample rates
    if sample_rate_a <= 0 or sample_rate_b <= 0:
        raise ValueError("Sample rates must be positive")
    
    # Call the appropriate C++ function
    if return_distance:
        return _compare_audio_arrays_distance(audio_a, float(sample_rate_a), 
                                             audio_b, float(sample_rate_b))
    else:
        return _compare_audio_arrays(audio_a, float(sample_rate_a), 
                                    audio_b, float(sample_rate_b))


def zimtohrli_distance_to_mos(distance: float) -> float:
    """
    Convert a raw Zimtohrli distance to Mean Opinion Score (MOS).
    
    Args:
        distance: Zimtohrli distance (0-1, where 0 is identical)
        
    Returns:
        float: MOS score (1-5, where 5 is excellent quality)
        
    Example:
        >>> distance = 0.1
        >>> mos = zimtohrli_distance_to_mos(distance)
        >>> print(f"Distance {distance} -> MOS {mos:.3f}")
    """
    return _mos_from_zimtohrli(float(distance))


def get_expected_sample_rate() -> int:
    """
    Get the expected sample rate for Zimtohrli analysis.
    
    Returns:
        int: Expected sample rate in Hz (48000)
        
    Example:
        >>> sr = zimtohrli.get_expected_sample_rate()
        >>> print(f"Expected sample rate: {sr} Hz")
    """
    return 48000


class ZimtohrliComparator:
    """
    A class for performing multiple audio comparisons with the same configuration.
    Reuses the underlying Zimtohrli instance for efficiency.
    
    This is the most efficient way to perform multiple comparisons, as it avoids
    the overhead of creating new Zimtohrli instances for each comparison.
    
    Example:
        >>> comparator = ZimtohrliComparator()
        >>> print(f"Expected sample rate: {comparator.sample_rate} Hz")
        >>> print(f"Spectrogram dimensions: {comparator.num_rotators}")
        >>> 
        >>> # Compare multiple audio pairs (must be at 48kHz)
        >>> for audio_a, audio_b in audio_pairs:
        ...     mos = comparator.compare(audio_a, audio_b)
        ...     print(f"MOS: {mos:.3f}")
    """
    
    def __init__(self):
        """Initialize the Zimtohrli comparator."""
        self._zimtohrli = _ZimtohrliCore()
    
    def compare(self, audio_a: np.ndarray, audio_b: np.ndarray, 
                return_distance: bool = False) -> float:
        """
        Compare two audio arrays at 48kHz sample rate.
        
        Note: Both arrays must already be at 48kHz sample rate.
        Use compare_audio() for automatic resampling.
        
        Args:
            audio_a: First audio array (1D numpy array of float32)
            audio_b: Second audio array (1D numpy array of float32)
            return_distance: If True, return raw distance. If False, return MOS.
            
        Returns:
            float: Either MOS score or raw distance
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate and prepare arrays
        if not isinstance(audio_a, np.ndarray) or not isinstance(audio_b, np.ndarray):
            raise ValueError("Audio inputs must be numpy arrays")
        
        if audio_a.ndim != 1 or audio_b.ndim != 1:
            raise ValueError("Audio arrays must be 1-dimensional")
            
        if audio_a.dtype != np.float32:
            audio_a = audio_a.astype(np.float32)
        if audio_b.dtype != np.float32:
            audio_b = audio_b.astype(np.float32)
        
        if not audio_a.flags['C_CONTIGUOUS']:
            audio_a = np.ascontiguousarray(audio_a)
        if not audio_b.flags['C_CONTIGUOUS']:
            audio_b = np.ascontiguousarray(audio_b)
        
        # Get raw distance
        distance = self._zimtohrli.distance(audio_a, audio_b)
        
        if return_distance:
            return distance
        else:
            return zimtohrli_distance_to_mos(distance)
    
    def analyze(self, audio: np.ndarray) -> bytes:
        """
        Analyze audio and return spectrogram data.
        
        Args:
            audio: Audio array (1D numpy array of float32) at 48kHz
            
        Returns:
            bytes: Spectrogram data
        """
        if not isinstance(audio, np.ndarray):
            raise ValueError("Audio input must be numpy array")
        
        if audio.ndim != 1:
            raise ValueError("Audio array must be 1-dimensional")
            
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        if not audio.flags['C_CONTIGUOUS']:
            audio = np.ascontiguousarray(audio)
            
        return self._zimtohrli.analyze(audio)
    
    @property
    def sample_rate(self) -> int:
        """Get the expected sample rate."""
        return self._zimtohrli.sample_rate()
    
    @property
    def num_rotators(self) -> int:
        """Get the number of rotators (spectrogram dimensions)."""
        return self._zimtohrli.num_rotators()


# Module-level convenience instance
_default_comparator = None

def get_default_comparator() -> ZimtohrliComparator:
    """Get a shared default comparator instance."""
    global _default_comparator
    if _default_comparator is None:
        _default_comparator = ZimtohrliComparator()
    return _default_comparator