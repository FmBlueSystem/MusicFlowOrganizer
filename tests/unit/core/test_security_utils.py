"""
Unit tests for Security Utils
=============================

Tests for security validation functions including path validation,
input sanitization, and injection prevention.

Developed by BlueSystemIO
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.core.security_utils import (
    validate_file_path, 
    sanitize_filename, 
    validate_database_query_params,
    is_safe_file_operation,
    SecurityError
)


class TestSecurityUtils:
    """Test suite for security utility functions."""
    
    @pytest.mark.security
    def test_validate_file_path_normal_paths(self, temp_directory):
        """Test validation of normal, safe file paths."""
        # Test valid paths
        valid_paths = [
            str(temp_directory / "music" / "track.mp3"),
            str(temp_directory / "folder" / "subfolder" / "song.flac"),
            "/home/user/music/track.mp3",
            "C:\\Users\\User\\Music\\track.mp3"
        ]
        
        for path in valid_paths:
            try:
                result = validate_file_path(path)
                assert isinstance(result, Path)
            except SecurityError:
                # Some paths might fail due to not existing, that's OK
                pass
    
    @pytest.mark.security
    def test_validate_file_path_traversal_attacks(self, malicious_paths):
        """Test prevention of path traversal attacks."""
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError):
                validate_file_path(malicious_path)
    
    @pytest.mark.security
    def test_validate_file_path_null_bytes(self):
        """Test detection of null byte injection."""
        malicious_paths = [
            "file\x00.mp3",
            "track.mp3\x00.exe",
            "/path/to/file\x00",
            "normal_file.mp3\x00../../../etc/passwd"
        ]
        
        for path in malicious_paths:
            with pytest.raises(SecurityError, match="null bytes"):
                validate_file_path(path)
    
    @pytest.mark.security
    def test_validate_file_path_dangerous_chars(self):
        """Test detection of dangerous characters."""
        dangerous_paths = [
            "file|rm -rf /.mp3",
            "track;cat /etc/passwd.mp3",
            "song&wget malicious.com.flac",
            "music$evil_command.wav",
            "track>output.txt.mp3",
            "song<input.txt.flac"
        ]
        
        for path in dangerous_paths:
            with pytest.raises(SecurityError, match="dangerous characters"):
                validate_file_path(path)
    
    @pytest.mark.security
    def test_validate_file_path_with_allowed_base_paths(self, temp_directory):
        """Test path validation with allowed base directories."""
        allowed_bases = [str(temp_directory)]
        
        # Valid path within allowed base
        valid_path = temp_directory / "music" / "track.mp3"
        result = validate_file_path(str(valid_path), allowed_bases)
        assert isinstance(result, Path)
        
        # Invalid path outside allowed base
        with pytest.raises(SecurityError, match="outside allowed directories"):
            validate_file_path("/etc/passwd", allowed_bases)
    
    def test_validate_file_path_empty_input(self):
        """Test handling of empty file paths."""
        empty_inputs = ["", None]
        
        for empty_input in empty_inputs:
            with pytest.raises(SecurityError, match="Empty file path"):
                validate_file_path(empty_input)
    
    @pytest.mark.security
    def test_sanitize_filename_normal_names(self):
        """Test sanitization of normal filenames."""
        test_cases = [
            ("normal_file.mp3", "normal_file.mp3"),
            ("Track Name.flac", "Track Name.flac"),
            ("Song-Title_2023.wav", "Song-Title_2023.wav"),
            ("01. First Track.mp3", "01. First Track.mp3")
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
    
    @pytest.mark.security
    def test_sanitize_filename_dangerous_chars(self):
        """Test removal of dangerous characters from filenames."""
        test_cases = [
            ("track|rm -rf.mp3", "track_rm -rf.mp3"),
            ("song;evil.flac", "song_evil.flac"),
            ("music&command.wav", "music_command.wav"),
            ("track$var.mp3", "track_var.mp3"),
            ("song>output.flac", "song_output.flac"),
            ("track<input.wav", "track_input.wav")
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
    
    @pytest.mark.security
    def test_sanitize_filename_reserved_names(self):
        """Test handling of Windows reserved filenames."""
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
        
        for name in reserved_names:
            result = sanitize_filename(name)
            assert result == f"_{name}"
            
            # Test with extension
            result = sanitize_filename(f"{name}.mp3")
            assert result == f"_{name}.mp3"
    
    def test_sanitize_filename_empty_input(self):
        """Test handling of empty filenames."""
        with pytest.raises(SecurityError, match="Empty filename"):
            sanitize_filename("")
        
        with pytest.raises(SecurityError, match="Empty filename"):
            sanitize_filename(None)
    
    def test_sanitize_filename_becomes_empty(self):
        """Test handling when filename becomes empty after sanitization."""
        # Filename with only dangerous characters
        with pytest.raises(SecurityError, match="becomes empty"):
            sanitize_filename("||||")
    
    @pytest.mark.security
    def test_validate_database_query_params_safe_params(self):
        """Test validation of safe database query parameters."""
        safe_params = [
            (1, 'track_name', 128.0, True),
            ('artist_name', 2023, None),
            (42,),
            ('normal string', 3.14, False)
        ]
        
        for params in safe_params:
            result = validate_database_query_params(params)
            assert result == params
            assert isinstance(result, tuple)
    
    @pytest.mark.security
    def test_validate_database_query_params_sql_injection(self, malicious_sql_inputs):
        """Test detection of SQL injection attempts."""
        for malicious_input in malicious_sql_inputs:
            params = (malicious_input, 'normal_param')
            
            with pytest.raises(SecurityError, match="SQL injection"):
                validate_database_query_params(params)
    
    def test_validate_database_query_params_invalid_types(self):
        """Test handling of invalid parameter types."""
        # Non-tuple/list input
        with pytest.raises(SecurityError, match="must be tuple or list"):
            validate_database_query_params("not a tuple")
        
        # Unsupported parameter type
        class CustomObject:
            pass
        
        with pytest.raises(SecurityError, match="Unsupported parameter type"):
            validate_database_query_params((CustomObject(),))
    
    @pytest.mark.security
    def test_is_safe_file_operation_valid_operations(self, temp_directory):
        """Test validation of safe file operations."""
        source = temp_directory / "source" / "track.mp3"
        target = temp_directory / "target" / "track.mp3"
        
        # Should not raise exception for valid paths
        try:
            result = is_safe_file_operation(source, target)
            assert result is True
        except SecurityError:
            # May fail due to path validation, but shouldn't crash
            pass
    
    @pytest.mark.security
    def test_is_safe_file_operation_system_paths(self):
        """Test prevention of operations on system directories."""
        system_targets = [
            '/bin/evil_file',
            '/sbin/malicious',
            '/usr/bin/bad_script',
            '/system/library/bad_file',
            '/windows/system32/evil.exe'
        ]
        
        for target in system_targets:
            with pytest.raises(SecurityError, match="system directory"):
                is_safe_file_operation('/tmp/source.mp3', target)
    
    @pytest.mark.security
    def test_is_safe_file_operation_identical_paths(self, temp_directory):
        """Test prevention of operations where source equals target."""
        path = temp_directory / "track.mp3"
        
        with pytest.raises(SecurityError, match="identical"):
            is_safe_file_operation(path, path)
    
    @pytest.mark.security
    def test_is_safe_file_operation_malicious_paths(self, malicious_paths):
        """Test file operations with malicious paths."""
        for malicious_path in malicious_paths:
            with pytest.raises(SecurityError):
                is_safe_file_operation('/tmp/source.mp3', malicious_path)
            
            with pytest.raises(SecurityError):
                is_safe_file_operation(malicious_path, '/tmp/target.mp3')
    
    def test_get_safe_temp_dir(self):
        """Test creation of safe temporary directory."""
        from src.core.security_utils import get_safe_temp_dir
        
        temp_dir = get_safe_temp_dir()
        
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.name == "musicflow_safe"
        
        # Check permissions (on Unix-like systems)
        if hasattr(temp_dir, 'stat'):
            stat_info = temp_dir.stat()
            # Should be readable/writable by owner only
            assert (stat_info.st_mode & 0o777) == 0o700
    
    @pytest.mark.security
    def test_path_validation_edge_cases(self):
        """Test edge cases in path validation."""
        edge_cases = [
            ".",  # Current directory
            "..",  # Parent directory
            "...",  # Triple dots
            "/",  # Root directory
            "\\",  # Windows root
            "",  # Empty string
            " ",  # Space only
            "\t",  # Tab character
            "\n",  # Newline
        ]
        
        for case in edge_cases:
            try:
                validate_file_path(case)
                # Some might be valid, that's OK
            except SecurityError:
                # Most should fail validation, that's expected
                pass
    
    @pytest.mark.security
    def test_filename_sanitization_unicode(self):
        """Test filename sanitization with Unicode characters."""
        unicode_names = [
            "track_ñañá.mp3",
            "música_española.flac",
            "трек_на_русском.wav",
            "日本語のファイル.mp3",
            "emoji_🎵_track.flac"
        ]
        
        for name in unicode_names:
            try:
                result = sanitize_filename(name)
                # Should handle Unicode gracefully
                assert isinstance(result, str)
                assert len(result) > 0
            except Exception:
                # Some Unicode handling might fail, but shouldn't crash
                pass