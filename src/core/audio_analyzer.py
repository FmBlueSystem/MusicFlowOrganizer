"""
Advanced Audio Analysis Engine for MusicFlow Organizer
======================================================

Professional audio analysis using librosa and essentia for:
- BPM detection and tempo analysis
- Key detection and harmonic analysis
- Energy level and mood classification
- Audio quality assessment
- Spectral analysis for genre hints

Based on professional DJ requirements and music analysis best practices.
"""

import os
import logging
import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import time

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import librosa
    import numpy as np
    import soundfile as sf
    from mutagen import File as MutagenFile
    AUDIO_ANALYSIS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Audio analysis libraries not available: {e}")
    AUDIO_ANALYSIS_AVAILABLE = False
    # Create minimal stubs for type hints
    try:
        import numpy as np
    except ImportError:
        # If numpy is also missing, create minimal type stubs
        class np:
            ndarray = object

# Try to import essentia for advanced analysis
try:
    import essentia
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    logging.info("Essentia not available - using librosa only")
    ESSENTIA_AVAILABLE = False


@dataclass
class AudioAnalysisResult:
    """Container for comprehensive audio analysis results."""
    
    # Basic properties
    file_path: str
    duration: float
    sample_rate: int
    bitrate: Optional[int] = None
    
    # Musical properties
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy_level: Optional[float] = None  # 0.0 to 1.0
    mood: Optional[str] = None
    
    # Advanced analysis
    spectral_centroid: Optional[float] = None
    spectral_rolloff: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    mfcc_features: Optional[List[float]] = None
    
    # Quality metrics
    dynamic_range: Optional[float] = None
    loudness: Optional[float] = None
    
    # Processing metadata
    analysis_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class AudioAnalyzer:
    """
    Professional audio analysis engine for DJ applications.
    
    Provides comprehensive audio analysis including BPM, key detection,
    energy levels, and spectral features for intelligent music organization.
    """
    
    # Key signatures in Camelot notation
    CAMELOT_KEYS = {
        'C': '8B', 'G': '9B', 'D': '10B', 'A': '11B', 'E': '12B', 'B': '1B',
        'F#': '2B', 'Db': '3B', 'Ab': '4B', 'Eb': '5B', 'Bb': '6B', 'F': '7B',
        'Am': '8A', 'Em': '9A', 'Bm': '10A', 'F#m': '11A', 'C#m': '12A', 'G#m': '1A',
        'D#m': '2A', 'Bbm': '3A', 'Fm': '4A', 'Cm': '5A', 'Gm': '6A', 'Dm': '7A'
    }
    
    # Energy level thresholds (based on DJ best practices)
    ENERGY_THRESHOLDS = {
        'low': 0.3,      # Chill, ambient, intro tracks
        'medium': 0.6,   # Regular dance tracks
        'high': 0.8,     # Peak time, high energy
        'extreme': 1.0   # Festival, hard dance
    }
    
    def __init__(self):
        """Initialize the audio analyzer."""
        self.logger = logging.getLogger(__name__)
        
        if not AUDIO_ANALYSIS_AVAILABLE:
            self.logger.warning("Audio analysis libraries not available - limited functionality")
            # Don't raise error, just warn
        
        # Configure librosa for better performance
        self.sr = 22050  # Sample rate for analysis
        self.hop_length = 512
        
        self.logger.info("AudioAnalyzer initialized")
    
    def analyze_file(self, file_path: str) -> AudioAnalysisResult:
        """
        Perform comprehensive audio analysis on a single file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            AudioAnalysisResult with all analysis data
        """
        start_time = time.time()
        
        # Check if analysis is available
        if not AUDIO_ANALYSIS_AVAILABLE:
            return AudioAnalysisResult(
                file_path=file_path,
                duration=0,
                sample_rate=0,
                success=False,
                error_message="Audio analysis libraries not available",
                analysis_time=time.time() - start_time
            )
        
        try:
            # Validate file
            if not Path(file_path).exists():
                return AudioAnalysisResult(
                    file_path=file_path,
                    duration=0,
                    sample_rate=0,
                    success=False,
                    error_message="File not found"
                )
            
            # Load basic metadata first
            metadata = self._extract_metadata(file_path)
            
            # Load audio for analysis
            try:
                y, sr = librosa.load(file_path, sr=self.sr, duration=120)  # Analyze first 2 minutes
            except Exception as e:
                return AudioAnalysisResult(
                    file_path=file_path,
                    duration=0,
                    sample_rate=0,
                    success=False,
                    error_message=f"Failed to load audio: {str(e)}"
                )
            
            # Perform analysis
            result = AudioAnalysisResult(
                file_path=file_path,
                duration=metadata.get('duration', len(y) / sr),
                sample_rate=sr,
                bitrate=metadata.get('bitrate')
            )
            
            # BPM detection
            result.bpm = self._detect_bpm(y, sr)
            
            # Key detection
            result.key = self._detect_key(y, sr)
            
            # Energy and mood analysis
            result.energy_level = self._analyze_energy(y, sr)
            result.mood = self._classify_mood(y, sr, result.energy_level)
            
            # Spectral features
            result.spectral_centroid = self._calculate_spectral_centroid(y, sr)
            result.spectral_rolloff = self._calculate_spectral_rolloff(y, sr)
            result.zero_crossing_rate = self._calculate_zcr(y)
            
            # MFCC features for ML
            result.mfcc_features = self._extract_mfcc_features(y, sr)
            
            # Audio quality metrics
            result.dynamic_range = self._calculate_dynamic_range(y)
            result.loudness = self._calculate_loudness(y)
            
            result.analysis_time = time.time() - start_time
            result.success = True
            
            self.logger.debug(f"Analysis completed for {Path(file_path).name} in {result.analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {file_path}: {str(e)}")
            return AudioAnalysisResult(
                file_path=file_path,
                duration=0,
                sample_rate=0,
                success=False,
                error_message=str(e),
                analysis_time=time.time() - start_time
            )
    
    def _extract_metadata(self, file_path: str) -> Dict:
        """Extract basic metadata using mutagen."""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return {}
            
            metadata = {}
            
            # Duration
            if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                metadata['duration'] = audio_file.info.length
            
            # Bitrate
            if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'bitrate'):
                metadata['bitrate'] = audio_file.info.bitrate
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata from {file_path}: {e}")
            return {}
    
    def _detect_bpm(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Detect BPM using librosa's beat tracking."""
        try:
            # Use multiple methods for better accuracy
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            
            # Validate BPM range (typical for music)
            if 60 <= tempo <= 200:
                return round(float(tempo), 1)
            
            # Try onset detection method if beat tracking fails
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length)
            if len(onset_frames) > 1:
                onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
                intervals = np.diff(onset_times)
                avg_interval = np.median(intervals)
                tempo = 60.0 / avg_interval
                
                if 60 <= tempo <= 200:
                    return round(tempo, 1)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"BPM detection failed: {e}")
            return None
    
    def _detect_key(self, y: np.ndarray, sr: int) -> Optional[str]:
        """Detect musical key using chroma features."""
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Simple key detection based on chroma distribution
            key_profiles = self._get_key_profiles()
            
            best_correlation = -1
            detected_key = None
            
            for key, profile in key_profiles.items():
                correlation = np.corrcoef(chroma_mean, profile)[0, 1]
                if correlation > best_correlation:
                    best_correlation = correlation
                    detected_key = key
            
            # Convert to Camelot notation if detected
            if detected_key and detected_key in self.CAMELOT_KEYS:
                return self.CAMELOT_KEYS[detected_key]
            
            return detected_key
            
        except Exception as e:
            self.logger.warning(f"Key detection failed: {e}")
            return None
    
    def _get_key_profiles(self) -> Dict[str, np.ndarray]:
        """Get key profiles for key detection."""
        # Simplified key profiles (Krumhansl-Schmuckler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        keys = {}
        key_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
        
        for i, key in enumerate(key_names):
            # Major keys
            keys[key] = np.roll(major_profile, i)
            # Minor keys
            keys[key + 'm'] = np.roll(minor_profile, i)
        
        return keys
    
    def _analyze_energy(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Analyze energy level of the track."""
        try:
            # RMS energy
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
            rms_mean = np.mean(rms)
            
            # Spectral centroid (brightness)
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
            centroid_mean = np.mean(centroid)
            
            # Zero crossing rate (noisiness)
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            zcr_mean = np.mean(zcr)
            
            # Combine features for energy estimate
            # Normalize and weight the features
            rms_norm = np.clip(rms_mean * 10, 0, 1)  # Scale RMS
            centroid_norm = np.clip(centroid_mean / 4000, 0, 1)  # Normalize centroid
            zcr_norm = np.clip(zcr_mean * 20, 0, 1)  # Scale ZCR
            
            # Weighted combination
            energy = (rms_norm * 0.5) + (centroid_norm * 0.3) + (zcr_norm * 0.2)
            
            return float(np.clip(energy, 0, 1))
            
        except Exception as e:
            self.logger.warning(f"Energy analysis failed: {e}")
            return None
    
    def _classify_mood(self, y: np.ndarray, sr: int, energy_level: Optional[float]) -> Optional[str]:
        """Classify mood based on audio features."""
        try:
            if energy_level is None:
                return None
            
            # Use energy level as primary mood indicator
            if energy_level >= self.ENERGY_THRESHOLDS['extreme']:
                return 'aggressive'
            elif energy_level >= self.ENERGY_THRESHOLDS['high']:
                return 'energetic'
            elif energy_level >= self.ENERGY_THRESHOLDS['medium']:
                return 'upbeat'
            elif energy_level >= self.ENERGY_THRESHOLDS['low']:
                return 'mellow'
            else:
                return 'chill'
                
        except Exception as e:
            self.logger.warning(f"Mood classification failed: {e}")
            return None
    
    def _calculate_spectral_centroid(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Calculate spectral centroid (brightness)."""
        try:
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
            return float(np.mean(centroid))
        except Exception:
            return None
    
    def _calculate_spectral_rolloff(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Calculate spectral rolloff."""
        try:
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
            return float(np.mean(rolloff))
        except Exception:
            return None
    
    def _calculate_zcr(self, y: np.ndarray) -> Optional[float]:
        """Calculate zero crossing rate."""
        try:
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            return float(np.mean(zcr))
        except Exception:
            return None
    
    def _extract_mfcc_features(self, y: np.ndarray, sr: int) -> Optional[List[float]]:
        """Extract MFCC features for machine learning."""
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            mfcc_means = np.mean(mfccs, axis=1)
            return mfcc_means.tolist()
        except Exception:
            return None
    
    def _calculate_dynamic_range(self, y: np.ndarray) -> Optional[float]:
        """Calculate dynamic range (difference between loud and quiet parts)."""
        try:
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            rms_db = librosa.amplitude_to_db(rms)
            return float(np.max(rms_db) - np.min(rms_db))
        except Exception:
            return None
    
    def _calculate_loudness(self, y: np.ndarray) -> Optional[float]:
        """Calculate overall loudness (RMS in dB)."""
        try:
            rms = np.sqrt(np.mean(y**2))
            return float(librosa.amplitude_to_db([rms])[0])
        except Exception:
            return None
    
    def get_energy_category(self, energy_level: float) -> str:
        """Get energy category label."""
        if energy_level >= self.ENERGY_THRESHOLDS['extreme']:
            return 'Extreme Energy'
        elif energy_level >= self.ENERGY_THRESHOLDS['high']:
            return 'High Energy'
        elif energy_level >= self.ENERGY_THRESHOLDS['medium']:
            return 'Medium Energy'
        else:
            return 'Low Energy'
    
    def is_mixable_bpm(self, bpm1: float, bpm2: float, tolerance: float = 6.0) -> bool:
        """Check if two BPMs are mixable within tolerance."""
        return abs(bpm1 - bpm2) <= tolerance or abs(bpm1 - bpm2*2) <= tolerance or abs(bpm1*2 - bpm2) <= tolerance
    
    def get_compatible_keys(self, key: str) -> List[str]:
        """Get list of harmonically compatible keys for mixing."""
        # Camelot Wheel harmonic mixing rules
        camelot_compatibility = {
            '1A': ['1A', '1B', '2A', '12A'],
            '2A': ['2A', '2B', '3A', '1A'],
            '3A': ['3A', '3B', '4A', '2A'],
            '4A': ['4A', '4B', '5A', '3A'],
            '5A': ['5A', '5B', '6A', '4A'],
            '6A': ['6A', '6B', '7A', '5A'],
            '7A': ['7A', '7B', '8A', '6A'],
            '8A': ['8A', '8B', '9A', '7A'],
            '9A': ['9A', '9B', '10A', '8A'],
            '10A': ['10A', '10B', '11A', '9A'],
            '11A': ['11A', '11B', '12A', '10A'],
            '12A': ['12A', '12B', '1A', '11A'],
            '1B': ['1B', '1A', '2B', '12B'],
            '2B': ['2B', '2A', '3B', '1B'],
            '3B': ['3B', '3A', '4B', '2B'],
            '4B': ['4B', '4A', '5B', '3B'],
            '5B': ['5B', '5A', '6B', '4B'],
            '6B': ['6B', '6A', '7B', '5B'],
            '7B': ['7B', '7A', '8B', '6B'],
            '8B': ['8B', '8A', '9B', '7B'],
            '9B': ['9B', '9A', '10B', '8B'],
            '10B': ['10B', '10A', '11B', '9B'],
            '11B': ['11B', '11A', '12B', '10B'],
            '12B': ['12B', '12A', '1B', '11B']
        }
        
        return camelot_compatibility.get(key, [key])