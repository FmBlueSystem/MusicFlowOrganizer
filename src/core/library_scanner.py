"""
Music Library Scanner - SRP-compliant component
===============================================

Responsible solely for scanning and discovering audio files in directories.
Part of the SOLID refactoring of FileOrganizer.

Developed by BlueSystemIO
"""

import os
import logging
from pathlib import Path
from typing import List, Set


class LibraryScanner:
    """
    Responsible for discovering and cataloging audio files in directories.
    
    Single Responsibility: File discovery and basic cataloging
    """
    
    # Supported audio file extensions
    AUDIO_EXTENSIONS = {
        '.mp3', '.flac', '.wav', '.aiff', '.m4a', '.ogg', 
        '.wma', '.aac', '.opus', '.alac'
    }
    
    # DJ software playlist extensions to preserve
    PLAYLIST_EXTENSIONS = {
        '.m3u', '.m3u8', '.pls', '.cue', '.nml', '.xml'
    }
    
    def __init__(self):
        """Initialize the library scanner."""
        self.logger = logging.getLogger(__name__)
    
    def find_audio_files(self, library_path: str) -> List[str]:
        """
        Find all audio files in the given directory recursively.
        
        Args:
            library_path: Path to search for audio files
            
        Returns:
            List of audio file paths
        """
        self.logger.info(f"Scanning for audio files in: {library_path}")
        audio_files = []
        
        try:
            for root, dirs, files in os.walk(library_path):
                for file in files:
                    if Path(file).suffix.lower() in self.AUDIO_EXTENSIONS:
                        audio_files.append(os.path.join(root, file))
            
            self.logger.info(f"Found {len(audio_files)} audio files")
            return audio_files
            
        except Exception as e:
            self.logger.error(f"Error scanning directory {library_path}: {e}")
            return []
    
    def find_playlist_files(self, library_path: str) -> List[str]:
        """
        Find all playlist files in the given directory.
        
        Args:
            library_path: Path to search for playlist files
            
        Returns:
            List of playlist file paths
        """
        playlist_files = []
        
        try:
            for root, dirs, files in os.walk(library_path):
                for file in files:
                    if Path(file).suffix.lower() in self.PLAYLIST_EXTENSIONS:
                        playlist_files.append(os.path.join(root, file))
            
            return playlist_files
            
        except Exception as e:
            self.logger.error(f"Error scanning for playlists in {library_path}: {e}")
            return []
    
    def get_directory_stats(self, library_path: str) -> dict:
        """
        Get basic statistics about a directory.
        
        Args:
            library_path: Path to analyze
            
        Returns:
            Dictionary with directory statistics
        """
        try:
            audio_files = self.find_audio_files(library_path)
            playlist_files = self.find_playlist_files(library_path)
            
            total_size = 0
            for file_path in audio_files:
                try:
                    total_size += Path(file_path).stat().st_size
                except OSError:
                    pass
            
            return {
                'total_audio_files': len(audio_files),
                'total_playlist_files': len(playlist_files),
                'total_size_bytes': total_size,
                'total_size_mb': total_size // (1024 * 1024),
                'directory_path': library_path
            }
            
        except Exception as e:
            self.logger.error(f"Error getting directory stats for {library_path}: {e}")
            return {}
    
    def is_audio_file(self, file_path: str) -> bool:
        """
        Check if a file is a supported audio format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a supported audio format
        """
        return Path(file_path).suffix.lower() in self.AUDIO_EXTENSIONS
    
    def is_playlist_file(self, file_path: str) -> bool:
        """
        Check if a file is a supported playlist format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a supported playlist format
        """
        return Path(file_path).suffix.lower() in self.PLAYLIST_EXTENSIONS
