"""
DJ Playlist Builder with Greedy Algorithm
========================================
Professional playlist generation using harmonic mixing and coherence optimization.

Implements:
- Greedy track selection with multi-criteria scoring
- Schweiger 2025 coherence metrics
- Lambda parameter for popularity/novelty balance
- Energy arc management for professional DJ sets
- BPM constraints and harmonic compatibility

Author: Claude Code
Date: 2025-07-12
"""

import logging
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path

from .camelot_wheel import CamelotWheel
from .coherence_metrics import CoherenceMetrics, TrackFeatures
from .enrichment import EnrichedTrackData

@dataclass
class PlaylistTrack:
    """Track in playlist with transition metadata."""
    track: EnrichedTrackData
    position: int
    transition_score: float
    coherence_breakdown: Dict[str, float]
    selected_reason: str

@dataclass
class PlaylistConfig:
    """Configuration for playlist generation."""
    target_bpm: Optional[float] = None
    target_length: int = 30
    lambda_popularity: float = 0.4  # Balance between popularity (λ) and novelty (1-λ)
    max_bpm_delta: float = 10.0
    min_coherence_threshold: float = 0.6
    energy_arc_type: str = "progressive"  # progressive, peak, valley, flat
    seed_track_id: Optional[str] = None
    genre_filter: Optional[List[str]] = None
    year_range: Optional[Tuple[int, int]] = None
    exclude_tracks: Optional[Set[str]] = None

class PlaylistBuilder:
    """
    Professional DJ playlist builder with greedy algorithm.
    
    Generates playlists optimized for:
    - Harmonic compatibility (Camelot Wheel)
    - Coherent transitions (BPM, energy, mood)
    - Popularity/novelty balance
    - Professional energy arc management
    """
    
    def __init__(self, enriched_db_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize playlist builder.
        
        Args:
            enriched_db_path: Path to enriched tracks database
            config: Optional configuration overrides
        """
        self.db_path = enriched_db_path
        self.config = config or {}
        self.logger = logging.getLogger("PlaylistBuilder")
        
        # Initialize components
        self.camelot_wheel = CamelotWheel()
        self.coherence_metrics = CoherenceMetrics(
            w_bpm=self.config.get('w_bpm', 0.25),
            w_key=self.config.get('w_key', 0.30),
            w_valence=self.config.get('w_valence', 0.25),
            w_energy=self.config.get('w_energy', 0.20),
            camelot_wheel=self.camelot_wheel
        )
        
        # Track scoring weights for greedy algorithm
        self.scoring_weights = {
            'key_compatibility': 0.6,   # Harmonic mixing is crucial
            'tempo_similarity': 0.2,    # BPM matching
            'coherence_mood': 0.2       # Mood/energy continuity
        }
        
        # Energy arc templates for professional DJ sets
        self.energy_arc_templates = {
            'progressive': self._generate_progressive_arc,
            'peak': self._generate_peak_arc,
            'valley': self._generate_valley_arc,
            'flat': self._generate_flat_arc
        }
    
    def _get_enriched_tracks(self, filters: Optional[Dict[str, Any]] = None) -> List[EnrichedTrackData]:
        """
        Retrieve enriched tracks from database with optional filters.
        
        Args:
            filters: Optional filtering criteria
            
        Returns:
            List[EnrichedTrackData]: Filtered enriched tracks
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM enriched_tracks WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('genre_filter'):
                    placeholders = ','.join(['?' for _ in filters['genre_filter']])
                    query += f" AND genre IN ({placeholders})"
                    params.extend(filters['genre_filter'])
                
                if filters.get('year_range'):
                    query += " AND year >= ? AND year <= ?"
                    params.extend(filters['year_range'])
                
                if filters.get('min_bpm'):
                    query += " AND bpm >= ?"
                    params.append(filters['min_bpm'])
                
                if filters.get('max_bpm'):
                    query += " AND bpm <= ?"
                    params.append(filters['max_bpm'])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to EnrichedTrackData objects
            tracks = []
            for row in rows:
                data = dict(row)
                
                # Parse JSON fields
                for field in ['subgenres', 'discogs_styles', 'lastfm_tags']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            data[field] = []
                
                for field in ['spotify_features', 'gpt_inference']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            data[field] = {}
                
                tracks.append(EnrichedTrackData(**data))
            
            return tracks
            
        except Exception as e:
            self.logger.error(f"Error retrieving enriched tracks: {e}")
            return []
    
    def _calculate_track_score(self, current_track: EnrichedTrackData, 
                              candidate: EnrichedTrackData,
                              config: PlaylistConfig) -> Tuple[float, Dict[str, float]]:
        """
        Calculate comprehensive score for track transition.
        
        Score = 0.6 × key_score + 0.2 × tempo_similarity + 0.2 × coherence_mood
        
        Args:
            current_track: Current track in playlist
            candidate: Candidate track to evaluate
            config: Playlist configuration
            
        Returns:
            Tuple[float, Dict[str, float]]: (total_score, score_breakdown)
        """
        # Key compatibility score (0.0 to 1.0)
        key_score = self.camelot_wheel.get_compatibility_score(
            current_track.camelot_key, 
            candidate.camelot_key
        )
        
        # Tempo similarity score (0.0 to 1.0)
        bpm_diff = abs(current_track.bpm - candidate.bpm)
        if bpm_diff > config.max_bpm_delta:
            tempo_score = 0.0  # Hard constraint
        else:
            # Linear decay within tolerance
            tempo_score = 1.0 - (bpm_diff / config.max_bpm_delta)
        
        # Coherence mood score using Schweiger metrics
        current_features = TrackFeatures(
            bpm=current_track.bpm,
            camelot_key=current_track.camelot_key,
            energy=current_track.energy,
            valence=current_track.spotify_features.get('valence', 0.5) if current_track.spotify_features else 0.5,
            danceability=current_track.spotify_features.get('danceability') if current_track.spotify_features else None
        )
        
        candidate_features = TrackFeatures(
            bpm=candidate.bpm,
            camelot_key=candidate.camelot_key,
            energy=candidate.energy,
            valence=candidate.spotify_features.get('valence', 0.5) if candidate.spotify_features else 0.5,
            danceability=candidate.spotify_features.get('danceability') if candidate.spotify_features else None
        )
        
        coherence_result = self.coherence_metrics.calculate_overall_coherence(
            current_features, candidate_features
        )
        coherence_score = coherence_result['overall_coherence']
        
        # Calculate weighted total score
        total_score = (
            self.scoring_weights['key_compatibility'] * key_score +
            self.scoring_weights['tempo_similarity'] * tempo_score +
            self.scoring_weights['coherence_mood'] * coherence_score
        )
        
        breakdown = {
            'key_score': key_score,
            'tempo_score': tempo_score,
            'coherence_score': coherence_score,
            'total_score': total_score,
            'bpm_diff': bpm_diff,
            'coherence_details': coherence_result
        }
        
        return total_score, breakdown
    
    def _apply_lambda_adjustment(self, track: EnrichedTrackData, 
                                lambda_popularity: float) -> float:
        """
        Apply lambda parameter adjustment for popularity/novelty balance.
        
        total_score = λ·popularity + (1-λ)·novelty
        
        Args:
            track: Track to evaluate
            lambda_popularity: Lambda parameter (0.0 to 1.0)
            
        Returns:
            float: Adjusted score factor
        """
        # Normalize popularity (0 to 100 -> 0.0 to 1.0)
        popularity = (track.spotify_popularity or 50) / 100.0
        
        # Calculate novelty as inverse of popularity with time decay
        current_year = time.localtime().tm_year
        track_age = current_year - (track.year or current_year)
        age_factor = min(1.0, track_age / 20.0)  # Normalize over 20 years
        
        novelty = (1.0 - popularity) * 0.7 + age_factor * 0.3
        
        # Apply lambda weighting
        adjustment = lambda_popularity * popularity + (1 - lambda_popularity) * novelty
        
        return adjustment
    
    def _generate_progressive_arc(self, length: int) -> List[float]:
        """Generate progressive energy arc (gradual build)."""
        arc = []
        for i in range(length):
            # Start at 0.3, build to 0.9
            energy = 0.3 + (0.6 * (i / (length - 1)))
            arc.append(energy)
        return arc
    
    def _generate_peak_arc(self, length: int) -> List[float]:
        """Generate peak energy arc (build, peak at 70%, wind down)."""
        arc = []
        peak_position = int(length * 0.7)
        
        for i in range(length):
            if i <= peak_position:
                # Build phase
                energy = 0.3 + (0.7 * (i / peak_position))
            else:
                # Wind down phase
                remaining = length - peak_position - 1
                position_after_peak = i - peak_position
                energy = 1.0 - (0.5 * (position_after_peak / remaining))
            arc.append(energy)
        return arc
    
    def _generate_valley_arc(self, length: int) -> List[float]:
        """Generate valley energy arc (start high, dip, recover)."""
        arc = []
        valley_position = int(length * 0.5)
        
        for i in range(length):
            if i <= valley_position:
                # Descent phase
                energy = 0.8 - (0.4 * (i / valley_position))
            else:
                # Recovery phase
                remaining = length - valley_position - 1
                position_after_valley = i - valley_position
                energy = 0.4 + (0.5 * (position_after_valley / remaining))
            arc.append(energy)
        return arc
    
    def _generate_flat_arc(self, length: int) -> List[float]:
        """Generate flat energy arc (consistent energy)."""
        return [0.6] * length
    
    def _select_seed_track(self, tracks: List[EnrichedTrackData], 
                          config: PlaylistConfig) -> Optional[EnrichedTrackData]:
        """
        Select optimal seed track for playlist.
        
        Args:
            tracks: Available tracks
            config: Playlist configuration
            
        Returns:
            Optional[EnrichedTrackData]: Selected seed track
        """
        if config.seed_track_id:
            # Use specified seed track
            for track in tracks:
                if track.track_id == config.seed_track_id:
                    return track
        
        # Select seed based on target BPM and popularity
        candidates = tracks.copy()
        
        if config.target_bpm:
            # Filter by BPM proximity
            candidates = [
                t for t in candidates 
                if abs(t.bpm - config.target_bpm) <= config.max_bpm_delta
            ]
        
        if not candidates:
            candidates = tracks
        
        # Score candidates by popularity and confidence
        scored_candidates = []
        for track in candidates:
            score = (
                self._apply_lambda_adjustment(track, config.lambda_popularity) * 0.5 +
                (track.genre_confidence or 0.5) * 0.5
            )
            scored_candidates.append((track, score))
        
        # Select top candidate with some randomness
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_candidates[:5]
        
        if top_candidates:
            return random.choice(top_candidates)[0]
        
        return None
    
    def build_playlist(self, config: PlaylistConfig) -> List[PlaylistTrack]:
        """
        Build a professional DJ playlist using greedy algorithm.
        
        Args:
            config: Playlist configuration
            
        Returns:
            List[PlaylistTrack]: Generated playlist with metadata
        """
        self.logger.info(f"Building playlist with config: {config}")
        
        # Get available tracks
        filters = {}
        if config.genre_filter:
            filters['genre_filter'] = config.genre_filter
        if config.year_range:
            filters['year_range'] = config.year_range
        if config.target_bpm:
            filters['min_bpm'] = config.target_bpm - config.max_bpm_delta * 2
            filters['max_bpm'] = config.target_bpm + config.max_bpm_delta * 2
        
        available_tracks = self._get_enriched_tracks(filters)
        
        if not available_tracks:
            self.logger.error("No tracks available for playlist generation")
            return []
        
        # Filter out excluded tracks
        if config.exclude_tracks:
            available_tracks = [
                t for t in available_tracks 
                if t.track_id not in config.exclude_tracks
            ]
        
        # Generate target energy arc
        energy_arc_generator = self.energy_arc_templates.get(
            config.energy_arc_type, 
            self._generate_progressive_arc
        )
        target_energy_arc = energy_arc_generator(config.target_length)
        
        # Initialize playlist with seed track
        seed_track = self._select_seed_track(available_tracks, config)
        if not seed_track:
            self.logger.error("Could not select seed track")
            return []
        
        playlist = [
            PlaylistTrack(
                track=seed_track,
                position=0,
                transition_score=1.0,
                coherence_breakdown={},
                selected_reason="Seed track"
            )
        ]
        
        used_tracks = {seed_track.track_id}
        
        # Greedy selection for remaining tracks
        for position in range(1, config.target_length):
            current_track = playlist[-1].track
            target_energy = target_energy_arc[position]
            
            # Find best candidate
            best_candidate = None
            best_score = -1
            best_breakdown = {}
            
            for candidate in available_tracks:
                # Skip already used tracks
                if candidate.track_id in used_tracks:
                    continue
                
                # Calculate transition score
                score, breakdown = self._calculate_track_score(
                    current_track, candidate, config
                )
                
                # Check minimum coherence threshold
                if breakdown['coherence_details']['overall_coherence'] < config.min_coherence_threshold:
                    continue
                
                # Apply energy arc guidance
                energy_diff = abs(candidate.energy - target_energy)
                energy_penalty = energy_diff * 0.2  # 20% penalty per unit difference
                adjusted_score = score * (1.0 - energy_penalty)
                
                # Apply popularity/novelty adjustment
                lambda_adjustment = self._apply_lambda_adjustment(
                    candidate, config.lambda_popularity
                )
                final_score = adjusted_score * (0.8 + 0.2 * lambda_adjustment)
                
                # Track best candidate
                if final_score > best_score:
                    best_score = final_score
                    best_candidate = candidate
                    best_breakdown = breakdown
                    best_breakdown['energy_diff'] = energy_diff
                    best_breakdown['lambda_adjustment'] = lambda_adjustment
                    best_breakdown['final_score'] = final_score
            
            # Add best candidate to playlist
            if best_candidate:
                reason = self._generate_selection_reason(best_breakdown)
                playlist.append(
                    PlaylistTrack(
                        track=best_candidate,
                        position=position,
                        transition_score=best_score,
                        coherence_breakdown=best_breakdown,
                        selected_reason=reason
                    )
                )
                used_tracks.add(best_candidate.track_id)
            else:
                self.logger.warning(f"Could not find suitable track for position {position}")
                break
        
        self.logger.info(f"Generated playlist with {len(playlist)} tracks")
        return playlist
    
    def _generate_selection_reason(self, breakdown: Dict[str, float]) -> str:
        """Generate human-readable reason for track selection."""
        reasons = []
        
        if breakdown['key_score'] >= 0.8:
            reasons.append("Excellent harmonic match")
        elif breakdown['key_score'] >= 0.6:
            reasons.append("Good key compatibility")
        
        if breakdown['tempo_score'] >= 0.9:
            reasons.append("Perfect tempo match")
        elif breakdown['tempo_score'] >= 0.7:
            reasons.append("Smooth BPM transition")
        
        if breakdown['coherence_score'] >= 0.8:
            reasons.append("High coherence")
        
        if breakdown.get('energy_diff', 1.0) <= 0.1:
            reasons.append("Matches energy arc")
        
        return " + ".join(reasons) if reasons else "Selected by algorithm"
    
    def export_playlist(self, playlist: List[PlaylistTrack], 
                       format: str = "json") -> str:
        """
        Export playlist in various formats.
        
        Args:
            playlist: Generated playlist
            format: Export format (json, m3u, csv)
            
        Returns:
            str: Exported playlist data
        """
        if format == "json":
            export_data = {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'track_count': len(playlist),
                'total_duration': sum(t.track.spotify_features.get('duration_ms', 0) 
                                    for t in playlist if t.track.spotify_features) / 1000 / 60,
                'tracks': []
            }
            
            for item in playlist:
                track_data = {
                    'position': item.position + 1,
                    'track_id': item.track.track_id,
                    'title': item.track.title,
                    'artist': item.track.artist,
                    'bpm': item.track.bpm,
                    'key': item.track.camelot_key,
                    'energy': item.track.energy,
                    'genre': item.track.genre,
                    'year': item.track.year,
                    'transition_score': item.transition_score,
                    'selection_reason': item.selected_reason
                }
                export_data['tracks'].append(track_data)
            
            return json.dumps(export_data, indent=2)
        
        elif format == "m3u":
            lines = ["#EXTM3U", "#PLAYLIST:MusicFlow DJ Set"]
            
            for item in playlist:
                duration = -1
                if item.track.spotify_features and 'duration_ms' in item.track.spotify_features:
                    duration = int(item.track.spotify_features['duration_ms'] / 1000)
                
                lines.append(f"#EXTINF:{duration},{item.track.artist} - {item.track.title}")
                lines.append(f"# BPM: {item.track.bpm}, Key: {item.track.camelot_key}")
                lines.append("")  # Placeholder for file path
            
            return "\n".join(lines)
        
        elif format == "csv":
            lines = ["Position,Artist,Title,BPM,Key,Energy,Genre,Year,Score,Reason"]
            
            for item in playlist:
                line = f"{item.position + 1},"
                line += f'"{item.track.artist}","{item.track.title}",'
                line += f"{item.track.bpm},{item.track.camelot_key},{item.track.energy:.2f},"
                line += f'"{item.track.genre or ""}",{item.track.year or ""},'
                line += f"{item.transition_score:.3f},"
                line += f'"{item.selected_reason}"'
                lines.append(line)
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def analyze_playlist_quality(self, playlist: List[PlaylistTrack]) -> Dict[str, Any]:
        """
        Analyze the quality of a generated playlist.
        
        Args:
            playlist: Playlist to analyze
            
        Returns:
            Dict[str, Any]: Quality analysis report
        """
        if len(playlist) < 2:
            return {'error': 'Playlist too short for analysis'}
        
        # Extract track features for sequence analysis
        track_features = []
        for item in playlist:
            features = TrackFeatures(
                bpm=item.track.bpm,
                camelot_key=item.track.camelot_key,
                energy=item.track.energy,
                valence=item.track.spotify_features.get('valence', 0.5) 
                    if item.track.spotify_features else 0.5
            )
            track_features.append(features)
        
        # Get sequence coherence analysis
        sequence_analysis = self.coherence_metrics.calculate_sequence_coherence(track_features)
        
        # Additional playlist metrics
        bpm_range = max(t.track.bpm for t in playlist) - min(t.track.bpm for t in playlist)
        
        # Genre diversity
        genres = set(t.track.genre for t in playlist if t.track.genre)
        genre_diversity = len(genres) / len(playlist) if playlist else 0
        
        # Key distribution
        key_distribution = {}
        for item in playlist:
            key = item.track.camelot_key
            key_distribution[key] = key_distribution.get(key, 0) + 1
        
        # Transition quality distribution
        transition_scores = [item.transition_score for item in playlist[1:]]
        avg_transition_score = sum(transition_scores) / len(transition_scores) if transition_scores else 0
        
        return {
            'playlist_length': len(playlist),
            'sequence_analysis': sequence_analysis,
            'bpm_range': bpm_range,
            'genre_diversity': genre_diversity,
            'unique_genres': list(genres),
            'key_distribution': key_distribution,
            'average_transition_score': avg_transition_score,
            'quality_summary': self._generate_quality_summary(
                sequence_analysis, avg_transition_score, genre_diversity
            )
        }
    
    def _generate_quality_summary(self, sequence_analysis: Dict[str, Any],
                                 avg_transition_score: float,
                                 genre_diversity: float) -> str:
        """Generate human-readable quality summary."""
        quality_rating = sequence_analysis.get('quality_rating', 'UNKNOWN')
        
        if quality_rating == "PROFESSIONAL":
            summary = "Professional-grade playlist with excellent flow"
        elif quality_rating == "EXCELLENT":
            summary = "High-quality playlist suitable for DJ performance"
        elif quality_rating == "GOOD":
            summary = "Good playlist with smooth transitions"
        elif quality_rating == "FAIR":
            summary = "Acceptable playlist with room for improvement"
        else:
            summary = "Playlist needs refinement for professional use"
        
        # Add specific insights
        if avg_transition_score >= 0.8:
            summary += ". Outstanding harmonic compatibility."
        elif avg_transition_score >= 0.6:
            summary += ". Good harmonic mixing throughout."
        
        if genre_diversity < 0.2:
            summary += " Very cohesive genre selection."
        elif genre_diversity > 0.5:
            summary += " Diverse genre exploration."
        
        return summary