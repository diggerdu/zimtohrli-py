"""
Test suite for Zimtohrli Python package core functionality.
"""

import numpy as np
import pytest
import zimtohrli_py as zimtohrli


class TestCoreAPI:
    """Test core API functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_rate = 48000
        self.duration = 0.5  # 0.5 seconds
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), dtype=np.float32)
        
        # Generate test signals
        self.sine_1khz = np.sin(2 * np.pi * 1000 * self.t).astype(np.float32) * 0.5
        self.sine_440hz = np.sin(2 * np.pi * 440 * self.t).astype(np.float32) * 0.5
        self.silence = np.zeros_like(self.t).astype(np.float32)
    
    def test_identical_signals(self):
        """Test that identical signals have high MOS and low distance."""
        mos = zimtohrli.compare_audio(self.sine_1khz, self.sample_rate, 
                                     self.sine_1khz, self.sample_rate)
        distance = zimtohrli.compare_audio(self.sine_1khz, self.sample_rate, 
                                          self.sine_1khz, self.sample_rate, 
                                          return_distance=True)
        
        assert mos > 4.5, f"MOS for identical signals should be high, got {mos}"
        assert distance < 0.1, f"Distance for identical signals should be low, got {distance}"
    
    def test_different_signals(self):
        """Test that different signals have different scores."""
        mos = zimtohrli.compare_audio(self.sine_1khz, self.sample_rate, 
                                     self.sine_440hz, self.sample_rate)
        distance = zimtohrli.compare_audio(self.sine_1khz, self.sample_rate, 
                                          self.sine_440hz, self.sample_rate, 
                                          return_distance=True)
        
        assert 1 <= mos <= 5, f"MOS should be in range [1,5], got {mos}"
        assert 0 <= distance <= 1, f"Distance should be in range [0,1], got {distance}"
        assert mos < 5.0, f"MOS for different signals should be < 5, got {mos}"
        assert distance > 0.0, f"Distance for different signals should be > 0, got {distance}"
    
    def test_sample_rate_conversion(self):
        """Test automatic sample rate conversion."""
        # Create signal at 16kHz
        sr_16k = 16000
        t_16k = np.linspace(0, self.duration, int(sr_16k * self.duration), dtype=np.float32)
        signal_16k = np.sin(2 * np.pi * 1000 * t_16k).astype(np.float32) * 0.5
        
        # Compare with same frequency at 48kHz
        mos = zimtohrli.compare_audio(signal_16k, sr_16k, self.sine_1khz, self.sample_rate)
        
        # Should be high similarity since same frequency content
        assert mos > 3.0, f"MOS for same frequency at different sample rates should be high, got {mos}"
    
    def test_input_validation(self):
        """Test input validation and error handling."""
        # Test non-numpy input
        with pytest.raises((ValueError, TypeError)):
            zimtohrli.compare_audio([1, 2, 3], 48000, [1, 2, 3], 48000)
        
        # Test negative sample rate
        with pytest.raises(ValueError):
            zimtohrli.compare_audio(self.sine_1khz, -1, self.sine_440hz, 48000)
        
        # Test empty array
        with pytest.raises(ValueError):
            empty_signal = np.array([], dtype=np.float32)
            zimtohrli.compare_audio(empty_signal, 48000, self.sine_1khz, 48000)
        
        # Test multi-dimensional array
        with pytest.raises(ValueError):
            multi_dim = np.random.randn(2, 1000).astype(np.float32)
            zimtohrli.compare_audio(multi_dim, 48000, self.sine_1khz, 48000)


class TestZimtohrliComparator:
    """Test ZimtohrliComparator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_rate = 48000
        self.duration = 0.5
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), dtype=np.float32)
        
        self.sine_1khz = np.sin(2 * np.pi * 1000 * self.t).astype(np.float32) * 0.5
        self.sine_440hz = np.sin(2 * np.pi * 440 * self.t).astype(np.float32) * 0.5
        
        self.comparator = zimtohrli.ZimtohrliComparator()
    
    def test_comparator_properties(self):
        """Test comparator properties."""
        assert self.comparator.sample_rate == 48000
        assert self.comparator.num_rotators > 0
    
    def test_comparator_compare(self):
        """Test comparator compare method."""
        # Test MOS
        mos = self.comparator.compare(self.sine_1khz, self.sine_440hz, return_distance=False)
        assert 1 <= mos <= 5, f"MOS should be in range [1,5], got {mos}"
        
        # Test distance
        distance = self.comparator.compare(self.sine_1khz, self.sine_440hz, return_distance=True)
        assert 0 <= distance <= 1, f"Distance should be in range [0,1], got {distance}"
        
        # Test consistency
        mos_from_distance = zimtohrli.zimtohrli_distance_to_mos(distance)
        np.testing.assert_allclose(mos, mos_from_distance, rtol=1e-6)
    
    def test_comparator_analyze(self):
        """Test spectrogram analysis."""
        spec_data = self.comparator.analyze(self.sine_1khz)
        assert isinstance(spec_data, bytes)
        assert len(spec_data) > 0


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_zimtohrli_distance_to_mos(self):
        """Test distance to MOS conversion."""
        test_distances = [0.0, 0.1, 0.5, 1.0]
        
        for distance in test_distances:
            mos = zimtohrli.zimtohrli_distance_to_mos(distance)
            assert 1 <= mos <= 5, f"MOS should be in range [1,5] for distance {distance}, got {mos}"
        
        # Test that distance 0 gives high MOS
        mos_zero = zimtohrli.zimtohrli_distance_to_mos(0.0)
        assert mos_zero > 4.5, f"Distance 0 should give high MOS, got {mos_zero}"
        
        # Test that higher distance gives lower MOS
        mos_low = zimtohrli.zimtohrli_distance_to_mos(0.1)
        mos_high = zimtohrli.zimtohrli_distance_to_mos(0.9)
        assert mos_low > mos_high, f"Lower distance should give higher MOS: {mos_low} vs {mos_high}"
    
    def test_get_expected_sample_rate(self):
        """Test expected sample rate function."""
        sr = zimtohrli.get_expected_sample_rate()
        assert sr == 48000


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_short_audio(self):
        """Test with very short audio signals."""
        short_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        # This might work or raise an error depending on implementation
        try:
            mos = zimtohrli.compare_audio(short_audio, 48000, short_audio, 48000)
            # If it works, should return high MOS for identical signals
            assert mos > 4.0
        except (ValueError, RuntimeError):
            # It's acceptable for very short signals to fail
            pass
    
    def test_different_dtypes(self):
        """Test with different numpy dtypes."""
        sample_rate = 48000
        t = np.linspace(0, 0.1, int(sample_rate * 0.1))
        
        # Test float64 (should be converted to float32)
        audio_f64 = np.sin(2 * np.pi * 1000 * t).astype(np.float64)
        audio_f32 = audio_f64.astype(np.float32)
        
        mos = zimtohrli.compare_audio(audio_f64, sample_rate, audio_f32, sample_rate)
        assert mos > 4.5, "Same signal with different dtypes should have high MOS"
    
    def test_non_contiguous_arrays(self):
        """Test with non-contiguous arrays."""
        sample_rate = 48000
        audio_orig = np.sin(2 * np.pi * 1000 * np.linspace(0, 0.1, int(sample_rate * 0.1))).astype(np.float32)
        
        # Create non-contiguous array
        audio_big = np.zeros((2, len(audio_orig)), dtype=np.float32)
        audio_big[0] = audio_orig
        audio_non_contig = audio_big[0]  # This should be non-contiguous
        
        # Should still work (will be made contiguous internally)
        mos = zimtohrli.compare_audio(audio_orig, sample_rate, audio_non_contig, sample_rate)
        assert mos > 4.5, "Same signal should have high MOS regardless of contiguity"


if __name__ == "__main__":
    pytest.main([__file__])