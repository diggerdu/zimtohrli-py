"""
Zimtohrli: Psychoacoustic perceptual audio similarity metric.

This package provides Python bindings for Google's Zimtohrli audio 
perceptual similarity metric, which quantifies human-perceivable 
differences in audio signals.

Basic usage:
    import zimtohrli_py as zimtohrli
    import numpy as np
    
    # Create audio arrays
    audio_a = np.random.randn(48000).astype(np.float32)  # 1 sec at 48kHz
    audio_b = np.random.randn(48000).astype(np.float32)
    
    # Get MOS score (1-5, higher is better)
    mos = zimtohrli.compare_audio(audio_a, 48000, audio_b, 48000)
    
    # Get raw distance (0-1, lower is better)
    distance = zimtohrli.compare_audio(audio_a, 48000, audio_b, 48000, return_distance=True)
"""

from .core import (
    compare_audio,
    zimtohrli_distance_to_mos,
    get_expected_sample_rate,
    ZimtohrliComparator,
)

try:
    from .audio_utils import (
        load_and_compare_audio_files,
        assess_audio_quality,
        batch_compare_audio
    )
except ImportError:
    # soundfile/librosa not available
    pass

__version__ = "1.0.0"
__author__ = "Google Zimtohrli Team, Python binding contributors"
__license__ = "Apache-2.0"

__all__ = [
    "compare_audio",
    "zimtohrli_distance_to_mos", 
    "get_expected_sample_rate",
    "ZimtohrliComparator",
    "load_and_compare_audio_files",
    "assess_audio_quality",
    "batch_compare_audio",
]