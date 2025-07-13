"""
Unit tests for TrackAnalyzer
============================

Tests for the SOLID-compliant TrackAnalyzer component.
Part of the FileOrganizer refactoring.

Developed by BlueSystemIO
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.core.track_analyzer import TrackAnalyzer, TrackData
from src.core.mixinkey_integration import MixInKeyTrackData
from src.core.genre_classifier import GenreClassificationResult
from src.core.audio_analyzer import AudioAnalysisResult


class TestTrackAnalyzer:
    """Test suite for TrackAnalyzer class."""
    
    def test_init(self):
        """Test TrackAnalyzer initialization."""
        analyzer = TrackAnalyzer()
        
        assert analyzer.logger is not None
        assert analyzer.mixinkey_integration is not None
        assert analyzer.genre_classifier is not None
        assert analyzer.audio_analyzer is not None
        assert analyzer.tracks_database == {}
    
    def test_track_data_dataclass(self):
        """Test TrackData dataclass functionality."""
        track_data = TrackData(
            file_path='/test/track.mp3',
            processed_timestamp=1234567890.0
        )
        
        assert track_data.file_path == '/test/track.mp3'
        assert track_data.processed_timestamp == 1234567890.0
        assert track_data.mixinkey_data is None
        assert track_data.genre_classification is None
        assert track_data.analysis_result is None
    
    @patch('src.core.track_analyzer.time.time')
    def test_analyze_track_with_mixinkey_data(self, mock_time):
        """Test track analysis with provided MixInKey data."""
        mock_time.return_value = 1234567890.0
        
        analyzer = TrackAnalyzer()
        
        # Mock components
        analyzer.genre_classifier.classify_genre = Mock()
        mock_genre_result = Mock()
        analyzer.genre_classifier.classify_genre.return_value = mock_genre_result
        
        # Create test MixInKey data
        mixinkey_data = MixInKeyTrackData(
            file_path='/test/track.mp3',
            filename='track.mp3',
            bpm=128.0,
            key='4A',
            energy=7,
            duration=240.0
        )
        
        result = analyzer.analyze_track('/test/track.mp3', mixinkey_data)
        
        # Verify result
        assert isinstance(result, TrackData)
        assert result.file_path == '/test/track.mp3'
        assert result.mixinkey_data == mixinkey_data
        assert result.genre_classification == mock_genre_result
        assert result.analysis_result is not None
        assert result.processed_timestamp == 1234567890.0
        
        # Verify genre classifier was called
        analyzer.genre_classifier.classify_genre.assert_called_once()
    
    def test_analyze_track_without_mixinkey_data(self):
        """Test track analysis without MixInKey data (fallback to audio analyzer)."""
        analyzer = TrackAnalyzer()
        
        # Mock audio analyzer
        mock_analysis_result = AudioAnalysisResult(
            file_path='/test/track.mp3',
            duration=240.0,
            bpm=130.0,
            key='C major',
            energy_level=0.8,
            success=True
        )
        analyzer.audio_analyzer.analyze_file = Mock(return_value=mock_analysis_result)
        
        # Mock genre classifier
        mock_genre_result = Mock()
        analyzer.genre_classifier.classify_genre = Mock(return_value=mock_genre_result)
        
        result = analyzer.analyze_track('/test/track.mp3')
        
        # Verify audio analyzer was called
        analyzer.audio_analyzer.analyze_file.assert_called_once_with('/test/track.mp3')
        
        # Verify MixInKey data was created from analysis
        assert result.mixinkey_data is not None
        assert result.mixinkey_data.bpm == 130.0
        assert result.mixinkey_data.key == 'C major'
        assert result.mixinkey_data.energy == 8  # 0.8 * 10
        assert result.mixinkey_data.analyzed_by_mixinkey is False
    
    def test_analyze_track_audio_analysis_failure(self):
        """Test track analysis when audio analysis fails."""
        analyzer = TrackAnalyzer()
        
        # Mock failed audio analysis
        failed_result = AudioAnalysisResult(
            file_path='/test/track.mp3',
            success=False,
            error_message='Analysis failed'
        )
        analyzer.audio_analyzer.analyze_file = Mock(return_value=failed_result)
        
        result = analyzer.analyze_track('/test/track.mp3')
        
        # Should still return TrackData but with minimal data
        assert isinstance(result, TrackData)
        assert result.mixinkey_data is None
        assert result.genre_classification is None
        assert result.analysis_result is None
    
    def test_build_tracks_database(self):
        """Test building tracks database from audio files."""
        analyzer = TrackAnalyzer()
        
        # Mock analyze_track method
        mock_track_data = TrackData(file_path='/test/track1.mp3')
        analyzer.analyze_track = Mock(return_value=mock_track_data)
        
        audio_files = ['/test/track1.mp3', '/test/track2.mp3']
        mixinkey_tracks = {'/test/track1.mp3': Mock()}
        
        result = analyzer.build_tracks_database(audio_files, mixinkey_tracks)
        
        # Verify database was built
        assert len(analyzer.tracks_database) == 2
        assert '/test/track1.mp3' in analyzer.tracks_database
        assert '/test/track2.mp3' in analyzer.tracks_database
        
        # Verify statistics
        assert result['total_files'] == 2
        assert result['processed_files'] == 2
        assert result['failed_files'] == 0
        assert 'processing_time' in result
    
    def test_build_tracks_database_with_failures(self):
        """Test building tracks database with some failures."""
        analyzer = TrackAnalyzer()
        
        # Mock analyze_track to fail for second file
        def mock_analyze_side_effect(file_path, mixinkey_data=None):
            if 'track2' in file_path:
                raise Exception("Analysis failed")
            return TrackData(file_path=file_path)
        
        analyzer.analyze_track = Mock(side_effect=mock_analyze_side_effect)
        
        audio_files = ['/test/track1.mp3', '/test/track2.mp3']
        
        result = analyzer.build_tracks_database(audio_files)
        
        # Verify partial success
        assert len(analyzer.tracks_database) == 1
        assert result['processed_files'] == 1
        assert result['failed_files'] == 1
    
    def test_get_track_data(self):
        """Test retrieving track data."""
        analyzer = TrackAnalyzer()
        
        # Add test data
        track_data = TrackData(file_path='/test/track.mp3')
        analyzer.tracks_database['/test/track.mp3'] = track_data
        
        # Test existing track
        result = analyzer.get_track_data('/test/track.mp3')
        assert result == track_data
        
        # Test non-existent track
        result = analyzer.get_track_data('/test/nonexistent.mp3')
        assert result is None
    
    def test_get_tracks_by_genre(self):
        """Test filtering tracks by genre."""
        analyzer = TrackAnalyzer()
        
        # Create test tracks with different genres
        track1 = TrackData(
            file_path='/test/house_track.mp3',
            genre_classification=Mock(primary_genre='House')
        )
        track2 = TrackData(
            file_path='/test/techno_track.mp3',
            genre_classification=Mock(primary_genre='Techno')
        )
        track3 = TrackData(
            file_path='/test/house_track2.mp3',
            genre_classification=Mock(primary_genre='House')
        )
        
        analyzer.tracks_database = {
            '/test/house_track.mp3': track1,
            '/test/techno_track.mp3': track2,
            '/test/house_track2.mp3': track3
        }
        
        house_tracks = analyzer.get_tracks_by_genre('House')
        
        assert len(house_tracks) == 2
        assert '/test/house_track.mp3' in house_tracks
        assert '/test/house_track2.mp3' in house_tracks
        assert '/test/techno_track.mp3' not in house_tracks
    
    def test_get_tracks_by_bpm_range(self):
        """Test filtering tracks by BPM range."""
        analyzer = TrackAnalyzer()
        
        # Create test tracks with different BPMs
        track1 = TrackData(
            file_path='/test/track_120.mp3',
            mixinkey_data=Mock(bpm=120.0)
        )
        track2 = TrackData(
            file_path='/test/track_130.mp3',
            mixinkey_data=Mock(bpm=130.0)
        )
        track3 = TrackData(
            file_path='/test/track_140.mp3',
            mixinkey_data=Mock(bpm=140.0)
        )
        
        analyzer.tracks_database = {
            '/test/track_120.mp3': track1,
            '/test/track_130.mp3': track2,
            '/test/track_140.mp3': track3
        }
        
        # Test BPM range 125-135
        filtered_tracks = analyzer.get_tracks_by_bpm_range(125.0, 135.0)
        
        assert len(filtered_tracks) == 1
        assert '/test/track_130.mp3' in filtered_tracks
    
    def test_get_database_statistics(self):
        """Test database statistics generation."""
        analyzer = TrackAnalyzer()
        
        # Create test database
        track1 = TrackData(
            file_path='/test/track1.mp3',
            mixinkey_data=Mock(bpm=128.0, key='4A', analyzed_by_mixinkey=True),
            genre_classification=Mock(primary_genre='House')
        )
        track2 = TrackData(
            file_path='/test/track2.mp3',
            mixinkey_data=Mock(bpm=135.0, key='9B', analyzed_by_mixinkey=False),
            genre_classification=Mock(primary_genre='Techno')
        )
        
        analyzer.tracks_database = {
            '/test/track1.mp3': track1,
            '/test/track2.mp3': track2
        }
        
        stats = analyzer.get_database_statistics()
        
        assert stats['total_tracks'] == 2
        assert stats['mixinkey_analyzed'] == 1
        assert stats['average_bpm'] == 131.5  # (128 + 135) / 2
        assert stats['genre_distribution'] == {'House': 1, 'Techno': 1}
        assert stats['key_distribution'] == {'4A': 1, '9B': 1}
    
    def test_get_database_statistics_empty(self):
        """Test database statistics with empty database."""
        analyzer = TrackAnalyzer()
        
        stats = analyzer.get_database_statistics()
        assert stats == {}
    
    def test_clear_database(self):
        """Test clearing the tracks database."""
        analyzer = TrackAnalyzer()
        
        # Add test data
        analyzer.tracks_database['/test/track.mp3'] = TrackData(file_path='/test/track.mp3')
        assert len(analyzer.tracks_database) == 1
        
        # Clear database
        analyzer.clear_database()
        assert len(analyzer.tracks_database) == 0
    
    @pytest.mark.performance
    def test_large_database_performance(self):
        """Test performance with large track database."""
        analyzer = TrackAnalyzer()
        
        # Create large database
        for i in range(1000):
            track_data = TrackData(
                file_path=f'/test/track_{i:04d}.mp3',
                mixinkey_data=Mock(bpm=120.0 + i % 40, key='4A'),
                genre_classification=Mock(primary_genre='House')
            )
            analyzer.tracks_database[f'/test/track_{i:04d}.mp3'] = track_data
        
        import time
        start_time = time.time()
        stats = analyzer.get_database_statistics()
        end_time = time.time()
        
        # Should complete quickly even with large database
        assert (end_time - start_time) < 1.0
        assert stats['total_tracks'] == 1000
    
    def test_create_analysis_result_from_mixinkey(self):
        """Test creation of AudioAnalysisResult from MixInKey data."""
        analyzer = TrackAnalyzer()
        
        mixinkey_data = MixInKeyTrackData(
            file_path='/test/track.mp3',
            filename='track.mp3',
            bpm=128.0,
            key='4A',
            energy=7,
            duration=240.0
        )
        
        result = analyzer._create_analysis_result(mixinkey_data)
        
        assert isinstance(result, AudioAnalysisResult)
        assert result.file_path == '/test/track.mp3'
        assert result.bpm == 128.0
        assert result.key == '4A'
        assert result.energy_level == 0.7  # 7 / 10
        assert result.duration == 240.0
        assert result.success is True
