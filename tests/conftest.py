"""
Test configuration and fixtures for MusicFlow Organizer
=======================================================

Global pytest configuration and shared test fixtures.

Developed by BlueSystemIO
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory(prefix="musicflow_test_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_audio_files(temp_directory):
    """Create sample audio files for testing."""
    files = []
    audio_formats = ['.mp3', '.flac', '.wav', '.m4a']
    
    for i, ext in enumerate(audio_formats):
        file_path = temp_directory / f"test_track_{i}{ext}"
        file_path.write_text(f"Mock audio content {i}")
        files.append(file_path)
    
    return files


@pytest.fixture
def mock_mixinkey_data():
    """Mock MixInKey track data for testing."""
    return {
        'file_path': '/test/path/track.mp3',
        'filename': 'track.mp3',
        'artist': 'Test Artist',
        'title': 'Test Track',
        'bpm': 128.0,
        'key': '4A',
        'energy': 7,
        'duration': 240.0,
        'bitrate': 320,
        'year': 2023
    }


@pytest.fixture
def mock_audio_analysis_result():
    """Mock audio analysis result for testing."""
    from src.core.audio_analyzer import AudioAnalysisResult
    
    return AudioAnalysisResult(
        file_path='/test/path/track.mp3',
        duration=240.0,
        sample_rate=44100,
        bitrate=320,
        bpm=128.0,
        key='C major',
        energy_level=0.7,
        mood='energetic',
        spectral_centroid=2000.0,
        spectral_rolloff=8000.0,
        zero_crossing_rate=0.1,
        mfcc_features=[1.0, 2.0, 3.0],
        analysis_time=1.5,
        success=True
    )


@pytest.fixture
def mock_genre_classification():
    """Mock genre classification result for testing."""
    from src.core.genre_classifier import GenreClassificationResult
    
    return GenreClassificationResult(
        file_path='/test/path/track.mp3',
        primary_genre='House',
        confidence=0.85,
        secondary_genres=[('Deep House', 0.65), ('Tech House', 0.45)],
        audio_features={
            'tempo': 128.0,
            'energy': 0.7,
            'danceability': 0.8
        },
        processing_time=0.5,
        success=True
    )


@pytest.fixture
def mock_organization_plan(temp_directory):
    """Mock organization plan for testing."""
    from src.core.file_organizer import OrganizationPlan, OrganizationScheme
    
    return OrganizationPlan(
        source_directory=str(temp_directory / "source"),
        target_directory=str(temp_directory / "target"),
        scheme=OrganizationScheme.BY_GENRE,
        files_to_organize=[
            ('/test/source/track1.mp3', ['House', 'Deep House', 'track1.mp3']),
            ('/test/source/track2.mp3', ['Techno', 'Peak Time', 'track2.mp3'])
        ],
        total_files=2,
        estimated_size=1024000,
        preview_mode=True,
        create_backup=True
    )


@pytest.fixture
def mock_sqlite_database(temp_directory):
    """Create a mock SQLite database for testing."""
    import sqlite3
    
    db_path = temp_directory / "test_mixinkey.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE ZSONG (
                ZARTIST TEXT,
                ZNAME TEXT,
                ZALBUM TEXT,
                ZTEMPO REAL,
                ZKEY TEXT,
                ZENERGY INTEGER,
                ZFILESIZE INTEGER,
                ZBOOKMARKDATA BLOB
            )
        """)
        
        # Insert test data
        test_data = [
            ('Test Artist 1', 'Test Track 1', 'Test Album 1', 128.0, '4A', 7, 5000000, b'test_bookmark_1'),
            ('Test Artist 2', 'Test Track 2', 'Test Album 2', 135.0, '9B', 8, 6000000, b'test_bookmark_2')
        ]
        
        cursor.executemany("""
            INSERT INTO ZSONG (ZARTIST, ZNAME, ZALBUM, ZTEMPO, ZKEY, ZENERGY, ZFILESIZE, ZBOOKMARKDATA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, test_data)
        
        conn.commit()
    
    return db_path


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing."""
    test_env = {
        'TEST_DISCOGS_TOKEN': 'mock_discogs_token',
        'TEST_SPOTIFY_CLIENT_ID': 'mock_spotify_id',
        'TEST_SPOTIFY_SECRET': 'mock_spotify_secret',
        'TEST_LASTFM_API_KEY': 'mock_lastfm_key',
        'TEST_OPENAI_API_KEY': 'mock_openai_key'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_audio_analyzer():
    """Mock AudioAnalyzer for testing."""
    from src.core.audio_analyzer import AudioAnalyzer
    
    with patch.object(AudioAnalyzer, 'analyze_file') as mock_analyze:
        mock_analyze.return_value = Mock(
            success=True,
            bpm=128.0,
            key='C major',
            energy_level=0.7,
            error_message=None
        )
        yield mock_analyze


@pytest.fixture
def mock_file_system():
    """Mock file system operations for testing."""
    with patch('shutil.move') as mock_move, \
         patch('shutil.copy2') as mock_copy, \
         patch('shutil.copytree') as mock_copytree, \
         patch('os.makedirs') as mock_makedirs:
        
        yield {
            'move': mock_move,
            'copy': mock_copy,
            'copytree': mock_copytree,
            'makedirs': mock_makedirs
        }


# Security testing fixtures
@pytest.fixture
def malicious_paths():
    """Common malicious path patterns for security testing."""
    return [
        '../../../etc/passwd',
        '..\\..\\windows\\system32\\config\\sam',
        '/etc/shadow',
        '../../Library/Keychains/',
        '../.ssh/id_rsa',
        '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',  # URL encoded
        '....//....//....//etc//passwd',  # Double dot bypass
        'test\x00file.mp3',  # Null byte injection
        'file|rm -rf /',  # Command injection
        'file; DROP TABLE tracks; --'  # SQL injection
    ]


@pytest.fixture
def malicious_sql_inputs():
    """Common SQL injection patterns for testing."""
    return [
        "'; DROP TABLE ZSONG; --",
        "1' OR '1'='1",
        "'; DELETE FROM ZSONG WHERE 1=1; --",
        "1' UNION SELECT password FROM users --",
        "admin'/*",
        "1'; ATTACH DATABASE '/etc/passwd' AS pwn; --",
        "\"; DROP TABLE ZSONG; --"
    ]


# Performance testing fixtures
@pytest.fixture
def large_file_list(temp_directory):
    """Create a large list of file paths for performance testing."""
    files = []
    for i in range(1000):  # Simulate 1000 files
        file_path = temp_directory / f"track_{i:04d}.mp3"
        files.append(str(file_path))
    return files


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "security: mark test as security-related"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance-related"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )