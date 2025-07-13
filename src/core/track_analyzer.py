"""
Track Analysis Engine - SRP-compliant component
==============================================

Responsible for analyzing individual tracks and building track database.
Part of the SOLID refactoring of FileOrganizer.

Developed by BlueSystemIO
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .mixinkey_integration import MixInKeyIntegration, MixInKeyTrackData
from .genre_classifier import GenreClassifier, GenreClassificationResult
from .audio_analyzer import AudioAnalyzer, AudioAnalysisResult


@dataclass
class TrackData:
    """Complete track data combining all analysis results."""
    file_path: str
    mixinkey_data: Optional[MixInKeyTrackData] = None
    genre_classification: Optional[GenreClassificationResult] = None
    analysis_result: Optional[AudioAnalysisResult] = None
    processed_timestamp: Optional[float] = None


class TrackAnalyzer:
    """
    Responsible for analyzing individual tracks and managing track database.
    
    Single Responsibility: Track analysis and data management
    """
    
    def __init__(self):
        """Initialize the track analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize analysis components
        self.mixinkey_integration = MixInKeyIntegration()
        self.genre_classifier = GenreClassifier()
        self.audio_analyzer = AudioAnalyzer()
        
        # Track database
        self.tracks_database: Dict[str, TrackData] = {}
    
    def analyze_track(self, file_path: str, mixinkey_data: Optional[MixInKeyTrackData] = None) -> TrackData:
        """
        Perform comprehensive analysis of a single track.
        
        Args:
            file_path: Path to the audio file
            mixinkey_data: Pre-existing MixIn Key data (optional)
            
        Returns:
            TrackData with complete analysis results
        """
        self.logger.debug(f"Analyzing track: {file_path}")
        
        track_data = TrackData(
            file_path=file_path,
            processed_timestamp=time.time()
        )
        
        # Use provided MixIn Key data or analyze the file
        if mixinkey_data:
            track_data.mixinkey_data = mixinkey_data
        else:
            track_data.mixinkey_data = self._analyze_with_audio_analyzer(file_path)
        
        # Perform genre classification if we have audio data
        if track_data.mixinkey_data:
            track_data.analysis_result = self._create_analysis_result(track_data.mixinkey_data)
            track_data.genre_classification = self.genre_classifier.classify_genre(track_data.analysis_result)
        
        return track_data
    
    def build_tracks_database(self, audio_files: list, mixinkey_tracks: Dict[str, MixInKeyTrackData] = None) -> Dict[str, Any]:
        """
        Build comprehensive tracks database from audio files.
        
        Args:
            audio_files: List of audio file paths
            mixinkey_tracks: Pre-loaded MixIn Key data (optional)
            
        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Building tracks database for {len(audio_files)} files")
        start_time = time.time()
        
        if not mixinkey_tracks:
            mixinkey_tracks = {}
        
        processed_count = 0
        failed_count = 0
        
        for file_path in audio_files:
            try:
                # Get existing MixIn Key data if available
                mixinkey_data = mixinkey_tracks.get(file_path)
                
                # Analyze the track
                track_data = self.analyze_track(file_path, mixinkey_data)
                
                # Store in database
                self.tracks_database[file_path] = track_data
                processed_count += 1
                
                if processed_count % 100 == 0:
                    self.logger.info(f"Processed {processed_count}/{len(audio_files)} files")
                    
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
                failed_count += 1
        
        processing_time = time.time() - start_time
        
        stats = {
            'total_files': len(audio_files),
            'processed_files': processed_count,
            'failed_files': failed_count,
            'mixinkey_analyzed': len([t for t in self.tracks_database.values() 
                                   if t.mixinkey_data and t.mixinkey_data.analyzed_by_mixinkey]),
            'processing_time': processing_time,
            'tracks_database_size': len(self.tracks_database)
        }
        
        self.logger.info(f"Tracks database built: {processed_count} tracks in {processing_time:.2f}s")
        return stats
    
    def get_track_data(self, file_path: str) -> Optional[TrackData]:
        """
        Get track data for a specific file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            TrackData if available, None otherwise
        """
        return self.tracks_database.get(file_path)
    
    def get_tracks_by_genre(self, genre: str) -> Dict[str, TrackData]:
        """
        Get all tracks of a specific genre.
        
        Args:
            genre: Genre name to filter by
            
        Returns:
            Dictionary of tracks filtered by genre
        """
        filtered_tracks = {}
        
        for file_path, track_data in self.tracks_database.items():
            if (track_data.genre_classification and 
                track_data.genre_classification.primary_genre == genre):
                filtered_tracks[file_path] = track_data
        
        return filtered_tracks
    
    def get_tracks_by_bpm_range(self, min_bpm: float, max_bpm: float) -> Dict[str, TrackData]:
        """
        Get all tracks within a BPM range.
        
        Args:
            min_bpm: Minimum BPM
            max_bpm: Maximum BPM
            
        Returns:
            Dictionary of tracks filtered by BPM range
        """
        filtered_tracks = {}
        
        for file_path, track_data in self.tracks_database.items():
            if (track_data.mixinkey_data and track_data.mixinkey_data.bpm and
                min_bpm <= track_data.mixinkey_data.bpm <= max_bpm):
                filtered_tracks[file_path] = track_data
        
        return filtered_tracks
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the tracks database.
        
        Returns:
            Dictionary with database statistics
        """
        if not self.tracks_database:
            return {}
        
        total_tracks = len(self.tracks_database)
        mixinkey_analyzed = len([t for t in self.tracks_database.values() 
                               if t.mixinkey_data and t.mixinkey_data.analyzed_by_mixinkey])
        
        # Collect statistics
        genres = {}
        bpms = []
        keys = {}
        
        for track_data in self.tracks_database.values():
            # Genre distribution
            if track_data.genre_classification and track_data.genre_classification.primary_genre:
                genre = track_data.genre_classification.primary_genre
                genres[genre] = genres.get(genre, 0) + 1
            
            # BPM and key data
            if track_data.mixinkey_data:
                if track_data.mixinkey_data.bpm:
                    bpms.append(track_data.mixinkey_data.bpm)
                if track_data.mixinkey_data.key:
                    key = track_data.mixinkey_data.key
                    keys[key] = keys.get(key, 0) + 1
        
        return {
            'total_tracks': total_tracks,
            'mixinkey_analyzed': mixinkey_analyzed,
            'genre_distribution': genres,
            'average_bpm': sum(bpms) / len(bpms) if bpms else 0,
            'bpm_range': {'min': min(bpms), 'max': max(bpms)} if bpms else None,
            'key_distribution': keys,
            'most_common_genre': max(genres, key=genres.get) if genres else None,
            'most_common_key': max(keys, key=keys.get) if keys else None
        }
    
    def clear_database(self):
        """Clear the tracks database."""
        self.tracks_database.clear()
        self.logger.info("Tracks database cleared")
    
    def _analyze_with_audio_analyzer(self, file_path: str) -> Optional[MixInKeyTrackData]:
        """
        Analyze file with audio analyzer and convert to MixInKeyTrackData format.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            MixInKeyTrackData or None if analysis failed
        """
        try:
            analysis_result = self.audio_analyzer.analyze_file(file_path)
            if analysis_result.success:
                return MixInKeyTrackData(
                    file_path=file_path,
                    filename=Path(file_path).name,
                    bpm=analysis_result.bpm,
                    key=analysis_result.key,
                    energy=int(analysis_result.energy_level * 10) if analysis_result.energy_level else None,
                    duration=analysis_result.duration,
                    analyzed_by_mixinkey=False
                )
        except Exception as e:
            self.logger.warning(f"Audio analysis failed for {file_path}: {e}")
        
        return None
    
    def _create_analysis_result(self, mixinkey_data: MixInKeyTrackData) -> AudioAnalysisResult:
        """
        Create AudioAnalysisResult from MixInKeyTrackData.
        
        Args:
            mixinkey_data: MixIn Key track data
            
        Returns:
            AudioAnalysisResult instance
        """
        return AudioAnalysisResult(
            file_path=mixinkey_data.file_path,
            duration=mixinkey_data.duration or 0,
            sample_rate=44100,  # Default
            bpm=mixinkey_data.bpm,
            key=mixinkey_data.key,
            energy_level=mixinkey_data.energy / 10 if mixinkey_data.energy else None,
            success=True
        )
