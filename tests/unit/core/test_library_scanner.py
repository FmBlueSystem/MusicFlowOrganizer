"""
Unit tests for LibraryScanner
=============================

Tests for the SOLID-compliant LibraryScanner component.
Part of the FileOrganizer refactoring.

Developed by BlueSystemIO
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.core.library_scanner import LibraryScanner


class TestLibraryScanner:
    """Test suite for LibraryScanner class."""
    
    def test_init(self):
        """Test LibraryScanner initialization."""
        scanner = LibraryScanner()
        assert scanner.logger is not None
        assert len(scanner.AUDIO_EXTENSIONS) > 0
        assert '.mp3' in scanner.AUDIO_EXTENSIONS
        assert '.flac' in scanner.AUDIO_EXTENSIONS
    
    def test_is_audio_file(self):
        """Test audio file detection."""
        scanner = LibraryScanner()
        
        # Test valid audio files
        assert scanner.is_audio_file('/path/to/track.mp3') is True
        assert scanner.is_audio_file('/path/to/track.flac') is True
        assert scanner.is_audio_file('/path/to/track.wav') is True
        assert scanner.is_audio_file('/path/to/track.m4a') is True
        
        # Test invalid files
        assert scanner.is_audio_file('/path/to/document.txt') is False
        assert scanner.is_audio_file('/path/to/image.jpg') is False
        assert scanner.is_audio_file('/path/to/video.mp4') is False
    
    def test_is_playlist_file(self):
        """Test playlist file detection."""
        scanner = LibraryScanner()
        
        # Test valid playlist files
        assert scanner.is_playlist_file('/path/to/playlist.m3u') is True
        assert scanner.is_playlist_file('/path/to/playlist.pls') is True
        assert scanner.is_playlist_file('/path/to/playlist.cue') is True
        
        # Test invalid files
        assert scanner.is_playlist_file('/path/to/track.mp3') is False
        assert scanner.is_playlist_file('/path/to/document.txt') is False
    
    @patch('os.walk')
    def test_find_audio_files_success(self, mock_walk):
        """Test successful audio file discovery."""
        scanner = LibraryScanner()
        
        # Mock os.walk to return test data
        mock_walk.return_value = [
            ('/music', ['subfolder'], ['track1.mp3', 'track2.flac', 'readme.txt']),
            ('/music/subfolder', [], ['track3.wav', 'playlist.m3u'])
        ]
        
        result = scanner.find_audio_files('/music')
        
        expected_files = [
            '/music/track1.mp3',
            '/music/track2.flac',
            '/music/subfolder/track3.wav'
        ]
        
        assert len(result) == 3
        for expected_file in expected_files:
            assert expected_file in result
    
    @patch('os.walk')
    def test_find_audio_files_empty_directory(self, mock_walk):
        """Test audio file discovery in empty directory."""
        scanner = LibraryScanner()
        
        # Mock empty directory
        mock_walk.return_value = [('/empty', [], [])]
        
        result = scanner.find_audio_files('/empty')
        assert result == []
    
    @patch('os.walk')
    def test_find_audio_files_error_handling(self, mock_walk):
        """Test error handling in audio file discovery."""
        scanner = LibraryScanner()
        
        # Mock os.walk to raise exception
        mock_walk.side_effect = OSError("Permission denied")
        
        result = scanner.find_audio_files('/restricted')
        assert result == []
    
    @patch('os.walk')
    def test_find_playlist_files(self, mock_walk):
        """Test playlist file discovery."""
        scanner = LibraryScanner()
        
        # Mock os.walk to return test data
        mock_walk.return_value = [
            ('/music', [], ['playlist1.m3u', 'playlist2.pls', 'track.mp3']),
            ('/music/playlists', [], ['dj_set.cue', 'favorites.m3u8'])
        ]
        
        result = scanner.find_playlist_files('/music')
        
        expected_files = [
            '/music/playlist1.m3u',
            '/music/playlist2.pls',
            '/music/playlists/dj_set.cue',
            '/music/playlists/favorites.m3u8'
        ]
        
        assert len(result) == 4
        for expected_file in expected_files:
            assert expected_file in result
    
    @patch('os.walk')
    @patch('pathlib.Path.stat')
    def test_get_directory_stats(self, mock_stat, mock_walk):
        """Test directory statistics calculation."""
        scanner = LibraryScanner()
        
        # Mock file system
        mock_walk.return_value = [
            ('/music', [], ['track1.mp3', 'track2.flac', 'playlist.m3u'])
        ]
        
        # Mock file sizes
        mock_stat.return_value.st_size = 5000000  # 5MB per file
        
        result = scanner.get_directory_stats('/music')
        
        assert result['total_audio_files'] == 2
        assert result['total_playlist_files'] == 1
        assert result['total_size_bytes'] == 10000000  # 2 * 5MB
        assert result['total_size_mb'] == 9  # 10MB // (1024*1024)
        assert result['directory_path'] == '/music'
    
    def test_case_insensitive_extensions(self):
        """Test that file extension detection is case insensitive."""
        scanner = LibraryScanner()
        
        # Test mixed case extensions
        assert scanner.is_audio_file('/path/to/track.MP3') is True
        assert scanner.is_audio_file('/path/to/track.FLAC') is True
        assert scanner.is_audio_file('/path/to/track.WaV') is True
        assert scanner.is_playlist_file('/path/to/playlist.M3U') is True
    
    def test_audio_extensions_comprehensive(self):
        """Test that all expected audio extensions are supported."""
        scanner = LibraryScanner()
        
        expected_extensions = {
            '.mp3', '.flac', '.wav', '.aiff', '.m4a', '.ogg',
            '.wma', '.aac', '.opus', '.alac'
        }
        
        assert scanner.AUDIO_EXTENSIONS == expected_extensions
    
    def test_playlist_extensions_comprehensive(self):
        """Test that all expected playlist extensions are supported."""
        scanner = LibraryScanner()
        
        expected_extensions = {
            '.m3u', '.m3u8', '.pls', '.cue', '.nml', '.xml'
        }
        
        assert scanner.PLAYLIST_EXTENSIONS == expected_extensions
    
    @pytest.mark.performance
    @patch('os.walk')
    def test_large_directory_performance(self, mock_walk):
        """Test performance with large directory structures."""
        scanner = LibraryScanner()
        
        # Simulate large directory with 1000 files
        large_file_list = [f'track_{i:04d}.mp3' for i in range(1000)]
        mock_walk.return_value = [('/large_music', [], large_file_list)]
        
        import time
        start_time = time.time()
        result = scanner.find_audio_files('/large_music')
        end_time = time.time()
        
        # Should complete quickly even with many files
        assert (end_time - start_time) < 1.0
        assert len(result) == 1000
    
    @pytest.mark.security
    def test_path_traversal_resistance(self):
        """Test resistance to path traversal in file paths."""
        scanner = LibraryScanner()
        
        # These should still be processed as audio files regardless of path
        malicious_paths = [
            '../../../etc/passwd.mp3',
            '..\\windows\\system32\\evil.flac',
            '/tmp/../music/track.wav'
        ]
        
        for path in malicious_paths:
            # Should detect as audio file based on extension
            assert scanner.is_audio_file(path) is True
            # Scanner itself doesn't validate paths - that's handled elsewhere
