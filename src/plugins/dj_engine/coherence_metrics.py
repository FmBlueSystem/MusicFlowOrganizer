"""
Coherence Metrics for DJ Playlist Generation
===========================================
Implementation of Schweiger 2025 coherence metrics for professional DJ mixing.

Provides multi-dimensional coherence scoring for seamless track transitions:
- BPM coherence (tempo matching)
- Key coherence (harmonic compatibility) 
- Valence coherence (emotional continuity)
- Energy coherence (intensity progression)

Author: Claude Code
Date: 2025-07-12
"""

import math
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

@dataclass
class TrackFeatures:
    """Track features for coherence analysis."""
    bpm: float
    camelot_key: str
    energy: float  # 0.0 to 1.0
    valence: float  # 0.0 to 1.0 (negative to positive emotion)
    danceability: Optional[float] = None
    loudness: Optional[float] = None
    instrumentalness: Optional[float] = None

class CoherenceMetrics:
    """
    Advanced coherence metrics for professional DJ playlist generation.
    
    Implements the Schweiger 2025 methodology for multi-dimensional 
    coherence scoring with configurable weights.
    
    Default weights:
    - w_bpm = 0.25 (tempo matching importance)
    - w_key = 0.30 (harmonic compatibility importance)  
    - w_valence = 0.25 (emotional continuity importance)
    - w_energy = 0.20 (energy progression importance)
    """
    
    def __init__(self, 
                 w_bpm: float = 0.25,
                 w_key: float = 0.30, 
                 w_valence: float = 0.25,
                 w_energy: float = 0.20,
                 camelot_wheel=None):
        """
        Initialize coherence metrics with configurable weights.
        
        Args:
            w_bpm: Weight for BPM coherence (0.0 to 1.0)
            w_key: Weight for key coherence (0.0 to 1.0)
            w_valence: Weight for valence coherence (0.0 to 1.0)
            w_energy: Weight for energy coherence (0.0 to 1.0)
            camelot_wheel: CamelotWheel instance for key compatibility
        """
        # Validate weights sum to 1.0
        total_weight = w_bpm + w_key + w_valence + w_energy
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        self.w_bpm = w_bpm
        self.w_key = w_key
        self.w_valence = w_valence
        self.w_energy = w_energy
        
        self.camelot_wheel = camelot_wheel
        self.logger = logging.getLogger("CoherenceMetrics")
        
        # Coherence calculation parameters
        self.bpm_tolerance = 10.0  # BPM difference tolerance
        self.energy_smoothing = 0.15  # Energy transition smoothing factor
        self.valence_smoothing = 0.20  # Valence transition smoothing factor
    
    def calculate_bpm_coherence(self, bpm1: float, bpm2: float) -> float:
        """
        Calculate BPM coherence between two tracks.
        
        Uses exponential decay based on BPM difference to favor closer tempos.
        Perfect match (0 BPM diff) = 1.0
        Within tolerance = 0.5+
        Beyond tolerance = exponential decay
        
        Args:
            bpm1: Source track BPM
            bpm2: Target track BPM
            
        Returns:
            float: BPM coherence score (0.0 to 1.0)
        """
        if not bpm1 or not bpm2 or bpm1 <= 0 or bpm2 <= 0:
            return 0.0
        
        bpm_diff = abs(bpm1 - bpm2)
        
        # Perfect match
        if bpm_diff == 0:
            return 1.0
        
        # Within tolerance - high coherence
        if bpm_diff <= self.bpm_tolerance:
            # Linear decay within tolerance
            return 1.0 - (bpm_diff / self.bpm_tolerance) * 0.3
        
        # Beyond tolerance - exponential decay
        decay_factor = 0.1  # How quickly coherence drops
        return max(0.0, 0.7 * math.exp(-decay_factor * (bpm_diff - self.bpm_tolerance)))
    
    def calculate_key_coherence(self, key1: str, key2: str) -> float:
        """
        Calculate harmonic key coherence using Camelot Wheel compatibility.
        
        Args:
            key1: Source track Camelot key
            key2: Target track Camelot key
            
        Returns:
            float: Key coherence score (0.0 to 1.0)
        """
        if not key1 or not key2:
            return 0.5  # Neutral score for missing keys
        
        if not self.camelot_wheel:
            self.logger.warning("No Camelot Wheel provided for key coherence")
            return 0.5
        
        # Get compatibility score from Camelot Wheel
        compatibility = self.camelot_wheel.get_compatibility_score(key1, key2)
        
        # Apply slight smoothing to favor strong relationships
        if compatibility >= 0.8:
            return min(1.0, compatibility + 0.1)  # Boost strong relationships
        elif compatibility >= 0.5:
            return compatibility  # Maintain moderate relationships
        else:
            return compatibility * 0.8  # Slightly penalize weak relationships
    
    def calculate_valence_coherence(self, valence1: float, valence2: float) -> float:
        """
        Calculate emotional valence coherence between tracks.
        
        Valence represents the emotional positivity/negativity:
        - 1.0 = Very positive (happy, euphoric)
        - 0.5 = Neutral
        - 0.0 = Very negative (sad, melancholic)
        
        Args:
            valence1: Source track valence (0.0 to 1.0)
            valence2: Target track valence (0.0 to 1.0)
            
        Returns:
            float: Valence coherence score (0.0 to 1.0)
        """
        if valence1 is None or valence2 is None:
            return 0.5  # Neutral score for missing valence
        
        # Ensure values are in valid range
        valence1 = max(0.0, min(1.0, valence1))
        valence2 = max(0.0, min(1.0, valence2))
        
        valence_diff = abs(valence1 - valence2)
        
        # Perfect emotional match
        if valence_diff <= 0.05:
            return 1.0
        
        # Smooth emotional transition favored
        if valence_diff <= self.valence_smoothing:
            return 1.0 - (valence_diff / self.valence_smoothing) * 0.2
        
        # Larger emotional jumps penalized
        penalty_factor = (valence_diff - self.valence_smoothing) / (1.0 - self.valence_smoothing)
        return max(0.2, 0.8 - penalty_factor * 0.6)
    
    def calculate_energy_coherence(self, energy1: float, energy2: float) -> float:
        """
        Calculate energy level coherence between tracks.
        
        Energy represents the intensity and danceability:
        - 1.0 = Very high energy (intense, driving)
        - 0.5 = Moderate energy
        - 0.0 = Very low energy (ambient, chill)
        
        Args:
            energy1: Source track energy (0.0 to 1.0)
            energy2: Target track energy (0.0 to 1.0)
            
        Returns:
            float: Energy coherence score (0.0 to 1.0)
        """
        if energy1 is None or energy2 is None:
            return 0.5  # Neutral score for missing energy
        
        # Ensure values are in valid range
        energy1 = max(0.0, min(1.0, energy1))
        energy2 = max(0.0, min(1.0, energy2))
        
        energy_diff = abs(energy1 - energy2)
        
        # Very similar energy levels
        if energy_diff <= 0.05:
            return 1.0
        
        # Gradual energy transitions favored
        if energy_diff <= self.energy_smoothing:
            return 1.0 - (energy_diff / self.energy_smoothing) * 0.25
        
        # Moderate energy changes acceptable
        if energy_diff <= 0.35:
            base_score = 0.75 - ((energy_diff - self.energy_smoothing) / 0.20) * 0.35
            return max(0.4, base_score)
        
        # Large energy jumps heavily penalized
        return max(0.1, 0.4 - (energy_diff - 0.35) * 0.6)
    
    def calculate_overall_coherence(self, track1_features: TrackFeatures, 
                                  track2_features: TrackFeatures) -> Dict[str, float]:
        """
        Calculate overall coherence score using weighted combination of all metrics.
        
        Args:
            track1_features: Source track features
            track2_features: Target track features
            
        Returns:
            Dict[str, float]: Detailed coherence breakdown and overall score
        """
        # Calculate individual coherence components
        bpm_coherence = self.calculate_bpm_coherence(
            track1_features.bpm, track2_features.bpm
        )
        
        key_coherence = self.calculate_key_coherence(
            track1_features.camelot_key, track2_features.camelot_key
        )
        
        valence_coherence = self.calculate_valence_coherence(
            track1_features.valence, track2_features.valence
        )
        
        energy_coherence = self.calculate_energy_coherence(
            track1_features.energy, track2_features.energy
        )
        
        # Calculate weighted overall coherence
        overall_coherence = (
            self.w_bpm * bpm_coherence +
            self.w_key * key_coherence +
            self.w_valence * valence_coherence +
            self.w_energy * energy_coherence
        )
        
        return {
            'bpm_coherence': bpm_coherence,
            'key_coherence': key_coherence, 
            'valence_coherence': valence_coherence,
            'energy_coherence': energy_coherence,
            'overall_coherence': overall_coherence,
            'weights': {
                'bpm': self.w_bpm,
                'key': self.w_key,
                'valence': self.w_valence,
                'energy': self.w_energy
            }
        }
    
    def calculate_sequence_coherence(self, track_sequence: List[TrackFeatures]) -> Dict[str, Any]:
        """
        Calculate coherence metrics for an entire track sequence (playlist).
        
        Args:
            track_sequence: List of track features in sequence order
            
        Returns:
            Dict[str, Any]: Sequence coherence analysis
        """
        if len(track_sequence) < 2:
            return {'error': 'Sequence must contain at least 2 tracks'}
        
        transition_scores = []
        bmp_progression = []
        energy_progression = []
        valence_progression = []
        
        # Analyze each transition
        for i in range(len(track_sequence) - 1):
            current_track = track_sequence[i]
            next_track = track_sequence[i + 1]
            
            transition = self.calculate_overall_coherence(current_track, next_track)
            transition_scores.append(transition['overall_coherence'])
            
            # Track progressions
            bpm_progression.append((current_track.bpm, next_track.bpm))
            energy_progression.append((current_track.energy, next_track.energy))
            valence_progression.append((current_track.valence, next_track.valence))
        
        # Calculate sequence-level metrics
        avg_coherence = sum(transition_scores) / len(transition_scores)
        min_coherence = min(transition_scores)
        coherence_variance = sum((score - avg_coherence) ** 2 for score in transition_scores) / len(transition_scores)
        
        # Energy arc analysis
        energy_values = [track.energy for track in track_sequence if track.energy is not None]
        energy_arc_quality = self._analyze_energy_arc(energy_values) if energy_values else 0.5
        
        return {
            'sequence_length': len(track_sequence),
            'average_coherence': avg_coherence,
            'minimum_coherence': min_coherence,
            'coherence_variance': coherence_variance,
            'transition_scores': transition_scores,
            'energy_arc_quality': energy_arc_quality,
            'bpm_progression': bpm_progression,
            'energy_progression': energy_progression,
            'valence_progression': valence_progression,
            'quality_rating': self._rate_sequence_quality(avg_coherence, min_coherence, coherence_variance)
        }
    
    def _analyze_energy_arc(self, energy_values: List[float]) -> float:
        """
        Analyze the energy progression arc for professional DJ sets.
        
        Good DJ sets often follow energy patterns:
        - Gradual build-up
        - Peak maintenance
        - Controlled wind-down
        
        Args:
            energy_values: List of energy values in sequence
            
        Returns:
            float: Energy arc quality score (0.0 to 1.0)
        """
        if len(energy_values) < 3:
            return 0.5
        
        # Find energy peak position
        max_energy = max(energy_values)
        peak_position = energy_values.index(max_energy) / (len(energy_values) - 1)
        
        # Ideal peak position is around 60-80% through the set
        optimal_peak = 0.7
        peak_score = 1.0 - abs(peak_position - optimal_peak) * 2
        peak_score = max(0.0, peak_score)
        
        # Analyze smoothness of transitions
        transition_smoothness = 0.0
        for i in range(len(energy_values) - 1):
            energy_diff = abs(energy_values[i + 1] - energy_values[i])
            # Penalize sudden energy drops/jumps
            if energy_diff > 0.3:
                transition_smoothness += 0.5
            else:
                transition_smoothness += 1.0
        
        transition_smoothness /= (len(energy_values) - 1)
        
        # Overall energy arc quality
        return (peak_score * 0.4 + transition_smoothness * 0.6)
    
    def _rate_sequence_quality(self, avg_coherence: float, min_coherence: float, variance: float) -> str:
        """
        Rate the overall quality of a track sequence.
        
        Args:
            avg_coherence: Average coherence score
            min_coherence: Minimum coherence score
            variance: Coherence variance
            
        Returns:
            str: Quality rating
        """
        # Professional DJ quality thresholds
        if avg_coherence >= 0.8 and min_coherence >= 0.6 and variance <= 0.05:
            return "PROFESSIONAL"
        elif avg_coherence >= 0.7 and min_coherence >= 0.5 and variance <= 0.1:
            return "EXCELLENT"
        elif avg_coherence >= 0.6 and min_coherence >= 0.4:
            return "GOOD"
        elif avg_coherence >= 0.5:
            return "FAIR"
        else:
            return "POOR"
    
    def suggest_transition_improvements(self, track1_features: TrackFeatures, 
                                      track2_features: TrackFeatures) -> List[str]:
        """
        Suggest specific improvements for a track transition.
        
        Args:
            track1_features: Source track features
            track2_features: Target track features
            
        Returns:
            List[str]: List of improvement suggestions
        """
        suggestions = []
        coherence = self.calculate_overall_coherence(track1_features, track2_features)
        
        # BPM suggestions
        if coherence['bpm_coherence'] < 0.6:
            bpm_diff = abs(track1_features.bpm - track2_features.bpm)
            if bpm_diff > 20:
                suggestions.append(f"Consider tempo adjustment: {bpm_diff:.1f} BPM difference is too large")
            else:
                suggestions.append("Use gradual tempo transition or find intermediate track")
        
        # Key suggestions
        if coherence['key_coherence'] < 0.5:
            suggestions.append(f"Key transition {track1_features.camelot_key} → {track2_features.camelot_key} is not harmonically compatible")
        
        # Energy suggestions
        if coherence['energy_coherence'] < 0.4:
            energy_diff = abs(track1_features.energy - track2_features.energy)
            if energy_diff > 0.4:
                suggestions.append(f"Energy jump too large ({energy_diff:.2f}), consider intermediate track")
        
        # Valence suggestions
        if coherence['valence_coherence'] < 0.4:
            valence_diff = abs(track1_features.valence - track2_features.valence)
            if valence_diff > 0.5:
                suggestions.append(f"Emotional transition too abrupt, consider mood bridge")
        
        return suggestions