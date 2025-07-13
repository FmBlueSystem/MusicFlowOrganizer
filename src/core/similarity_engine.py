"""
Advanced Similarity Detection Engine for MusicFlow Organizer
============================================================

Intelligent music similarity detection using:
- MixIn Key harmonic analysis and compatibility
- BPM and tempo matching algorithms
- Genre classification and mixing rules
- Energy level and mood analysis
- Machine learning-based feature comparison
- DJ mixing best practices

Built for professional DJ workflow optimization and music discovery.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import json
from pathlib import Path

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - using rule-based similarity only")

from .mixinkey_integration import MixInKeyTrackData, MixInKeyIntegration
from .genre_classifier import GenreClassificationResult, GenreClassifier
from .audio_analyzer import AudioAnalysisResult


@dataclass
class SimilarityResult:
    """Result of similarity analysis between tracks."""
    
    target_track: str  # File path
    similar_track: str  # File path
    similarity_score: float  # 0.0 to 1.0
    similarity_factors: Dict[str, float]  # Individual factor scores
    compatibility_type: str  # "harmonic", "tempo", "genre", "energy", "mood"
    mix_suggestion: Optional[str] = None  # DJ mixing suggestion
    confidence: float = 0.0  # Confidence in similarity
    

@dataclass
class PlaylistRecommendation:
    """Recommendation for creating playlists based on similarity."""
    
    seed_track: str
    recommended_tracks: List[Tuple[str, float]]  # (file_path, score)
    playlist_type: str  # "harmonic_mix", "energy_progression", "genre_journey"
    total_duration: float
    bpm_range: Tuple[float, float]
    key_progression: List[str]
    energy_curve: List[float]


class SimilarityEngine:
    """
    Advanced music similarity detection engine.
    
    Combines multiple analysis techniques to provide intelligent
    music recommendations and playlist generation for DJs.
    """
    
    # Similarity weights for different factors
    SIMILARITY_WEIGHTS = {
        'harmonic': 0.30,    # Key compatibility (Camelot Wheel)
        'tempo': 0.25,       # BPM matching
        'genre': 0.20,       # Genre compatibility
        'energy': 0.15,      # Energy level matching
        'mood': 0.10         # Mood and style similarity
    }
    
    # BPM tolerance for mixing
    BPM_TOLERANCE = {
        'perfect': 2.0,      # Perfect match
        'excellent': 6.0,    # Excellent for mixing
        'good': 12.0,        # Good with pitch adjustment
        'acceptable': 20.0   # Acceptable for transition
    }
    
    # Energy level transitions that work well
    ENERGY_TRANSITIONS = {
        'smooth': 1,         # ±1 energy level
        'moderate': 2,       # ±2 energy levels
        'dramatic': 3        # ±3 energy levels
    }
    
    def __init__(self):
        """Initialize the similarity engine."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.mixinkey_integration = MixInKeyIntegration()
        self.genre_classifier = GenreClassifier()
        
        # Analysis data
        self.tracks_database = {}
        self.similarity_matrix = {}
        self.genre_similarity_cache = {}
        
        # ML models
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.feature_matrix = None
        
        self.logger.info("SimilarityEngine initialized")
    
    def load_tracks_database(self, tracks_database: Dict) -> bool:
        """
        Load tracks database from file organizer.
        
        Args:
            tracks_database: Database from FileOrganizer
            
        Returns:
            True if loaded successfully
        """
        try:
            self.tracks_database = tracks_database
            self.logger.info(f"Loaded {len(tracks_database)} tracks for similarity analysis")
            
            # Build feature matrix for ML-based similarity
            if SKLEARN_AVAILABLE:
                self._build_feature_matrix()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load tracks database: {e}")
            return False
    
    def find_similar_tracks(self, target_file: str, 
                          max_results: int = 10,
                          min_similarity: float = 0.3) -> List[SimilarityResult]:
        """
        Find tracks similar to the target track.
        
        Args:
            target_file: Path to target track
            max_results: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of SimilarityResult objects sorted by similarity
        """
        if target_file not in self.tracks_database:
            self.logger.warning(f"Target track not found: {target_file}")
            return []
        
        target_data = self.tracks_database[target_file]
        similarities = []
        
        # Compare with all other tracks
        for candidate_file, candidate_data in self.tracks_database.items():
            if candidate_file == target_file:
                continue
            
            # Calculate similarity
            similarity = self._calculate_track_similarity(target_data, candidate_data)
            
            if similarity.similarity_score >= min_similarity:
                similarity.target_track = target_file
                similarity.similar_track = candidate_file
                similarities.append(similarity)
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Add mix suggestions
        for similarity in similarities[:max_results]:
            similarity.mix_suggestion = self._generate_mix_suggestion(
                target_data, self.tracks_database[similarity.similar_track]
            )
        
        self.logger.debug(f"Found {len(similarities)} similar tracks for {Path(target_file).name}")
        
        return similarities[:max_results]
    
    def generate_harmonic_playlist(self, seed_track: str, 
                                 target_duration: float = 3600) -> PlaylistRecommendation:
        """
        Generate playlist based on harmonic mixing principles.
        
        Args:
            seed_track: Starting track
            target_duration: Target playlist duration in seconds
            
        Returns:
            PlaylistRecommendation with harmonic progression
        """
        if seed_track not in self.tracks_database:
            return None
        
        playlist_tracks = [(seed_track, 1.0)]
        current_track = seed_track
        total_duration = self.tracks_database[seed_track]['mixinkey_data'].duration or 300
        
        key_progression = []
        energy_curve = []
        bpm_range = [float('inf'), -float('inf')]
        
        while total_duration < target_duration:
            # Find harmonically compatible next track
            similar_tracks = self.find_similar_tracks(
                current_track, max_results=20, min_similarity=0.4
            )
            
            # Filter for harmonic compatibility
            harmonic_tracks = [
                s for s in similar_tracks 
                if 'harmonic' in s.similarity_factors and s.similarity_factors['harmonic'] > 0.7
            ]
            
            if not harmonic_tracks:
                break
            
            # Select best track that hasn't been used
            next_track = None
            for track in harmonic_tracks:
                if track.similar_track not in [t[0] for t in playlist_tracks]:
                    next_track = track.similar_track
                    break
            
            if not next_track:
                break
            
            # Add to playlist
            playlist_tracks.append((next_track, harmonic_tracks[0].similarity_score))
            
            # Update statistics
            track_data = self.tracks_database[next_track]
            mixinkey_data = track_data['mixinkey_data']
            
            if mixinkey_data.duration:
                total_duration += mixinkey_data.duration
            
            if mixinkey_data.key:
                key_progression.append(mixinkey_data.key)
            
            if mixinkey_data.energy:
                energy_curve.append(mixinkey_data.energy / 10.0)
            
            if mixinkey_data.bpm:
                bpm_range[0] = min(bpm_range[0], mixinkey_data.bpm)
                bpm_range[1] = max(bpm_range[1], mixinkey_data.bpm)
            
            current_track = next_track
        
        return PlaylistRecommendation(
            seed_track=seed_track,
            recommended_tracks=playlist_tracks[1:],  # Exclude seed track
            playlist_type="harmonic_mix",
            total_duration=total_duration,
            bpm_range=tuple(bpm_range) if bpm_range[0] != float('inf') else (0, 0),
            key_progression=key_progression,
            energy_curve=energy_curve
        )
    
    def generate_energy_progression_playlist(self, seed_track: str,
                                           progression_type: str = "buildup") -> PlaylistRecommendation:
        """
        Generate playlist with energy progression (buildup/breakdown).
        
        Args:
            seed_track: Starting track
            progression_type: "buildup", "breakdown", or "wave"
            
        Returns:
            PlaylistRecommendation with energy progression
        """
        if seed_track not in self.tracks_database:
            return None
        
        seed_data = self.tracks_database[seed_track]
        seed_energy = seed_data['mixinkey_data'].energy or 5
        
        playlist_tracks = [(seed_track, 1.0)]
        energy_curve = [seed_energy / 10.0]
        key_progression = []
        bpm_range = [float('inf'), -float('inf')]
        total_duration = seed_data['mixinkey_data'].duration or 300
        
        # Define energy progression
        target_energy_levels = self._get_energy_progression(seed_energy, progression_type)
        
        current_track = seed_track
        for target_energy in target_energy_levels:
            # Find tracks with target energy level
            candidates = []
            
            for file_path, track_data in self.tracks_database.items():
                if file_path in [t[0] for t in playlist_tracks]:
                    continue
                
                track_energy = track_data['mixinkey_data'].energy or 5
                energy_diff = abs(track_energy - target_energy)
                
                if energy_diff <= 2:  # Within 2 energy levels
                    similarity = self._calculate_track_similarity(
                        self.tracks_database[current_track], track_data
                    )
                    candidates.append((file_path, similarity.similarity_score, track_energy))
            
            if not candidates:
                continue
            
            # Select best candidate
            candidates.sort(key=lambda x: x[1], reverse=True)
            next_track, score, energy = candidates[0]
            
            playlist_tracks.append((next_track, score))
            energy_curve.append(energy / 10.0)
            
            # Update statistics
            track_data = self.tracks_database[next_track]
            mixinkey_data = track_data['mixinkey_data']
            
            if mixinkey_data.duration:
                total_duration += mixinkey_data.duration
            
            if mixinkey_data.key:
                key_progression.append(mixinkey_data.key)
            
            if mixinkey_data.bpm:
                bpm_range[0] = min(bpm_range[0], mixinkey_data.bpm)
                bpm_range[1] = max(bpm_range[1], mixinkey_data.bpm)
            
            current_track = next_track
        
        return PlaylistRecommendation(
            seed_track=seed_track,
            recommended_tracks=playlist_tracks[1:],
            playlist_type=f"energy_{progression_type}",
            total_duration=total_duration,
            bpm_range=tuple(bpm_range) if bpm_range[0] != float('inf') else (0, 0),
            key_progression=key_progression,
            energy_curve=energy_curve
        )
    
    def find_transition_tracks(self, from_track: str, to_track: str,
                             max_transitions: int = 3) -> List[List[str]]:
        """
        Find transition tracks to smoothly mix between two tracks.
        
        Args:
            from_track: Starting track
            to_track: Ending track
            max_transitions: Maximum number of transition tracks
            
        Returns:
            List of possible transition paths
        """
        if (from_track not in self.tracks_database or 
            to_track not in self.tracks_database):
            return []
        
        from_data = self.tracks_database[from_track]
        to_data = self.tracks_database[to_track]
        
        # Check if direct transition is possible
        direct_similarity = self._calculate_track_similarity(from_data, to_data)
        if direct_similarity.similarity_score > 0.6:
            return [[from_track, to_track]]
        
        # Find intermediate tracks
        transition_paths = []
        
        # Get tracks similar to starting track
        similar_to_start = self.find_similar_tracks(from_track, max_results=20)
        
        for similar in similar_to_start:
            intermediate = similar.similar_track
            
            # Check if intermediate can transition to target
            intermediate_to_target = self._calculate_track_similarity(
                self.tracks_database[intermediate], to_data
            )
            
            if intermediate_to_target.similarity_score > 0.5:
                path = [from_track, intermediate, to_track]
                transition_paths.append(path)
        
        # Sort by total transition quality
        def path_quality(path):
            total_score = 0
            for i in range(len(path) - 1):
                sim = self._calculate_track_similarity(
                    self.tracks_database[path[i]], 
                    self.tracks_database[path[i + 1]]
                )
                total_score += sim.similarity_score
            return total_score / (len(path) - 1)
        
        transition_paths.sort(key=path_quality, reverse=True)
        
        return transition_paths[:max_transitions]
    
    def _calculate_track_similarity(self, track1_data: Dict, track2_data: Dict) -> SimilarityResult:
        """Calculate similarity between two tracks."""
        mixinkey1 = track1_data['mixinkey_data']
        mixinkey2 = track2_data['mixinkey_data']
        genre1 = track1_data['genre_classification']
        genre2 = track2_data['genre_classification']
        
        similarity_factors = {}
        
        # Harmonic similarity (Camelot Wheel)
        harmonic_score = self._calculate_harmonic_similarity(mixinkey1, mixinkey2)
        similarity_factors['harmonic'] = harmonic_score
        
        # Tempo similarity
        tempo_score = self._calculate_tempo_similarity(mixinkey1, mixinkey2)
        similarity_factors['tempo'] = tempo_score
        
        # Genre similarity
        genre_score = self._calculate_genre_similarity(genre1, genre2)
        similarity_factors['genre'] = genre_score
        
        # Energy similarity
        energy_score = self._calculate_energy_similarity(mixinkey1, mixinkey2)
        similarity_factors['energy'] = energy_score
        
        # Mood similarity
        mood_score = self._calculate_mood_similarity(genre1, genre2)
        similarity_factors['mood'] = mood_score
        
        # Calculate weighted overall similarity
        overall_similarity = sum(
            score * self.SIMILARITY_WEIGHTS[factor]
            for factor, score in similarity_factors.items()
            if score is not None
        )
        
        # Determine primary compatibility type
        max_factor = max(similarity_factors.items(), key=lambda x: x[1] or 0)
        compatibility_type = max_factor[0]
        
        # Calculate confidence based on available data
        available_factors = len([s for s in similarity_factors.values() if s is not None])
        confidence = available_factors / len(similarity_factors)
        
        return SimilarityResult(
            target_track="",  # Will be set by caller
            similar_track="",  # Will be set by caller
            similarity_score=overall_similarity,
            similarity_factors=similarity_factors,
            compatibility_type=compatibility_type,
            confidence=confidence
        )
    
    def _calculate_harmonic_similarity(self, track1: MixInKeyTrackData, 
                                     track2: MixInKeyTrackData) -> Optional[float]:
        """Calculate harmonic compatibility using Camelot Wheel."""
        if not track1.key or not track2.key:
            return None
        
        # Get compatible keys from Camelot Wheel
        compatible_keys = self.mixinkey_integration.CAMELOT_WHEEL.get(track1.key, {}).get('compatible', [])
        
        if track2.key == track1.key:
            return 1.0  # Perfect match
        elif track2.key in compatible_keys:
            return 0.8  # Harmonically compatible
        else:
            # Check for relative minor/major
            if (track1.key.endswith('A') and track2.key.endswith('B') and 
                track1.key[:-1] == track2.key[:-1]):
                return 0.6  # Relative minor/major
            else:
                return 0.2  # Not compatible
    
    def _calculate_tempo_similarity(self, track1: MixInKeyTrackData, 
                                  track2: MixInKeyTrackData) -> Optional[float]:
        """Calculate tempo compatibility for mixing."""
        if not track1.bpm or not track2.bpm:
            return None
        
        bpm_diff = abs(track1.bpm - track2.bpm)
        
        if bpm_diff <= self.BPM_TOLERANCE['perfect']:
            return 1.0
        elif bpm_diff <= self.BPM_TOLERANCE['excellent']:
            return 0.8
        elif bpm_diff <= self.BPM_TOLERANCE['good']:
            return 0.6
        elif bpm_diff <= self.BPM_TOLERANCE['acceptable']:
            return 0.4
        
        # Check for double/half tempo compatibility
        double_half_diff = min(
            abs(track1.bpm - track2.bpm * 2),
            abs(track1.bpm * 2 - track2.bpm)
        )
        
        if double_half_diff <= self.BPM_TOLERANCE['excellent']:
            return 0.7
        elif double_half_diff <= self.BPM_TOLERANCE['good']:
            return 0.5
        
        return 0.2
    
    def _calculate_genre_similarity(self, genre1: GenreClassificationResult,
                                  genre2: GenreClassificationResult) -> Optional[float]:
        """Calculate genre compatibility."""
        if not genre1 or not genre2:
            return None
        
        # Exact match
        if genre1.primary_genre == genre2.primary_genre:
            return 1.0
        
        # Check mixable genres
        if genre2.primary_genre in genre1.mixable_genres:
            return 0.8
        
        # Check similar genres
        if genre2.primary_genre in genre1.similar_genres:
            return 0.6
        
        # Use genre classifier similarity matrix
        similarity_matrix = self.genre_classifier._build_similarity_matrix()
        similar_genres = similarity_matrix.get(genre1.primary_genre, [])
        
        if genre2.primary_genre in similar_genres:
            # Position in similarity list indicates strength
            position = similar_genres.index(genre2.primary_genre)
            return max(0.4 - position * 0.1, 0.1)
        
        return 0.1
    
    def _calculate_energy_similarity(self, track1: MixInKeyTrackData,
                                   track2: MixInKeyTrackData) -> Optional[float]:
        """Calculate energy level compatibility."""
        if track1.energy is None or track2.energy is None:
            return None
        
        energy_diff = abs(track1.energy - track2.energy)
        
        if energy_diff == 0:
            return 1.0
        elif energy_diff <= self.ENERGY_TRANSITIONS['smooth']:
            return 0.8
        elif energy_diff <= self.ENERGY_TRANSITIONS['moderate']:
            return 0.6
        elif energy_diff <= self.ENERGY_TRANSITIONS['dramatic']:
            return 0.4
        else:
            return 0.2
    
    def _calculate_mood_similarity(self, genre1: GenreClassificationResult,
                                 genre2: GenreClassificationResult) -> Optional[float]:
        """Calculate mood and style similarity."""
        if not genre1 or not genre2:
            return None
        
        # Compare mood tags
        if hasattr(genre1, 'mood_tags') and hasattr(genre2, 'mood_tags'):
            common_tags = set(genre1.mood_tags) & set(genre2.mood_tags)
            total_tags = set(genre1.mood_tags) | set(genre2.mood_tags)
            
            if total_tags:
                return len(common_tags) / len(total_tags)
        
        # Fallback to energy category comparison
        if genre1.energy_category == genre2.energy_category:
            return 0.6
        else:
            return 0.3
    
    def _generate_mix_suggestion(self, track1_data: Dict, track2_data: Dict) -> str:
        """Generate mixing suggestion for two tracks."""
        mixinkey1 = track1_data['mixinkey_data']
        mixinkey2 = track2_data['mixinkey_data']
        
        suggestions = []
        
        # BPM suggestion
        if mixinkey1.bpm and mixinkey2.bpm:
            bpm_diff = abs(mixinkey1.bpm - mixinkey2.bpm)
            if bpm_diff <= 2:
                suggestions.append("Perfect BPM match - mix at any point")
            elif bpm_diff <= 6:
                suggestions.append(f"Adjust tempo by {bpm_diff:.1f} BPM")
            else:
                suggestions.append("Use pitch adjustment or find transition track")
        
        # Key suggestion
        if mixinkey1.key and mixinkey2.key:
            if mixinkey1.key == mixinkey2.key:
                suggestions.append("Same key - harmonic mixing ready")
            else:
                compatible = self.mixinkey_integration.CAMELOT_WHEEL.get(mixinkey1.key, {}).get('compatible', [])
                if mixinkey2.key in compatible:
                    suggestions.append(f"Harmonic mix: {mixinkey1.key} → {mixinkey2.key}")
        
        # Energy suggestion
        if mixinkey1.energy and mixinkey2.energy:
            energy_diff = mixinkey2.energy - mixinkey1.energy
            if energy_diff > 0:
                suggestions.append(f"Energy buildup (+{energy_diff})")
            elif energy_diff < 0:
                suggestions.append(f"Energy breakdown ({energy_diff})")
            else:
                suggestions.append("Same energy level")
        
        return " | ".join(suggestions) if suggestions else "Basic compatibility"
    
    def _get_energy_progression(self, start_energy: int, progression_type: str) -> List[int]:
        """Generate energy progression for playlist."""
        if progression_type == "buildup":
            # Gradual increase in energy
            return [start_energy + i for i in range(1, 6) if start_energy + i <= 10]
        
        elif progression_type == "breakdown":
            # Gradual decrease in energy
            return [start_energy - i for i in range(1, 6) if start_energy - i >= 1]
        
        elif progression_type == "wave":
            # Wave pattern (up then down)
            progression = []
            # Build up
            for i in range(1, 4):
                if start_energy + i <= 10:
                    progression.append(start_energy + i)
            # Break down
            peak = progression[-1] if progression else start_energy
            for i in range(1, 4):
                if peak - i >= 1:
                    progression.append(peak - i)
            return progression
        
        return []
    
    def _build_feature_matrix(self):
        """Build feature matrix for ML-based similarity (if sklearn available)."""
        if not SKLEARN_AVAILABLE:
            return
        
        features = []
        file_paths = []
        
        for file_path, track_data in self.tracks_database.items():
            mixinkey_data = track_data['mixinkey_data']
            genre_result = track_data['genre_classification']
            
            # Extract numerical features
            feature_vector = []
            
            # BPM
            feature_vector.append(mixinkey_data.bpm or 120)
            
            # Key (convert to numerical)
            key_num = self._key_to_number(mixinkey_data.key) if mixinkey_data.key else 0
            feature_vector.append(key_num)
            
            # Energy
            feature_vector.append(mixinkey_data.energy or 5)
            
            # Genre (one-hot encoding would be better, but this is simpler)
            genre_num = hash(genre_result.primary_genre) % 100 if genre_result else 0
            feature_vector.append(genre_num)
            
            features.append(feature_vector)
            file_paths.append(file_path)
        
        if features:
            self.feature_matrix = np.array(features)
            self.scaler.fit(self.feature_matrix)
            self.logger.info(f"Built feature matrix: {self.feature_matrix.shape}")
    
    def _key_to_number(self, key: str) -> int:
        """Convert Camelot key to numerical value."""
        if not key:
            return 0
        
        # Extract number and letter
        try:
            number = int(key[:-1])
            letter = key[-1]
            # A = minor (0), B = major (12)
            offset = 0 if letter == 'A' else 12
            return number + offset
        except (ValueError, IndexError):
            return 0
    
    def export_similarity_matrix(self, output_file: str) -> bool:
        """Export similarity matrix to JSON file."""
        try:
            similarity_data = {}
            
            for file_path in self.tracks_database.keys():
                similar_tracks = self.find_similar_tracks(file_path, max_results=10)
                similarity_data[file_path] = [
                    {
                        'file': s.similar_track,
                        'score': s.similarity_score,
                        'factors': s.similarity_factors,
                        'type': s.compatibility_type
                    }
                    for s in similar_tracks
                ]
            
            with open(output_file, 'w') as f:
                json.dump(similarity_data, f, indent=2)
            
            self.logger.info(f"Similarity matrix exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export similarity matrix: {e}")
            return False