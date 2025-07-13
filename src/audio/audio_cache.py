"""
Audio Cache System for MusicFlow Organizer
===========================================

Intelligent caching system for audio metadata and preview data
to improve performance during music library organization.
"""

import os
import json
import logging
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
import time
from threading import Lock

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


@dataclass
class CachedTrackData:
    """Cached track metadata and analysis data."""
    
    file_path: str
    file_hash: str
    file_size: int
    last_modified: float
    
    # Basic metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    
    # Analysis data (if available)
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[int] = None
    
    # Cache metadata
    cached_at: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0


class AudioCache:
    """
    Intelligent audio metadata cache for improved performance.
    
    Caches file metadata, analysis results, and provides fast lookups
    for previously analyzed tracks.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize audio cache.
        
        Args:
            cache_dir: Custom cache directory (uses default if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default cache in user's home directory
            self.cache_dir = Path.home() / ".musicflow_cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache database
        self.db_path = self.cache_dir / "audio_cache.db"
        self.db_lock = Lock()
        
        # In-memory cache for fast access
        self.memory_cache: Dict[str, CachedTrackData] = {}
        self.max_memory_cache = 1000  # Maximum items in memory
        
        # Initialize database
        self._init_database()
        
        # Load recent items into memory
        self._load_recent_to_memory()
        
        self.logger.info(f"Audio cache initialized: {self.cache_dir}")
    
    def _init_database(self):
        """Initialize SQLite database for persistent cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS track_cache (
                        file_path TEXT PRIMARY KEY,
                        file_hash TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        last_modified REAL NOT NULL,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        genre TEXT,
                        duration REAL,
                        bitrate INTEGER,
                        bpm REAL,
                        key TEXT,
                        energy INTEGER,
                        cached_at REAL NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        last_accessed REAL DEFAULT 0
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON track_cache(file_hash)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON track_cache(last_accessed)")
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cache database: {e}")
    
    def _load_recent_to_memory(self):
        """Load recently accessed items into memory cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM track_cache 
                    ORDER BY last_accessed DESC 
                    LIMIT ?
                """, (self.max_memory_cache // 2,))
                
                for row in cursor.fetchall():
                    track_data = self._row_to_track_data(row)
                    self.memory_cache[track_data.file_path] = track_data
                    
        except Exception as e:
            self.logger.warning(f"Failed to load cache to memory: {e}")
    
    def get_track_data(self, file_path: str) -> Optional[CachedTrackData]:
        """
        Get cached track data.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            CachedTrackData if found and valid, None otherwise
        """
        # Check if file exists
        if not Path(file_path).exists():
            return None
        
        # Check memory cache first
        if file_path in self.memory_cache:
            track_data = self.memory_cache[file_path]
            if self._is_cache_valid(track_data):
                self._update_access_stats(track_data)
                return track_data
            else:
                # Remove invalid cache
                del self.memory_cache[file_path]
        
        # Check database cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM track_cache WHERE file_path = ?",
                    (file_path,)
                )
                row = cursor.fetchone()
                
                if row:
                    track_data = self._row_to_track_data(row)
                    if self._is_cache_valid(track_data):
                        # Add to memory cache
                        self._add_to_memory_cache(track_data)
                        self._update_access_stats(track_data)
                        return track_data
                    else:
                        # Remove invalid cache
                        self.remove_from_cache(file_path)
                        
        except Exception as e:
            self.logger.warning(f"Failed to get cached data for {file_path}: {e}")
        
        return None
    
    def cache_track_data(self, file_path: str, **metadata) -> bool:
        """
        Cache track metadata and analysis data.
        
        Args:
            file_path: Path to audio file
            **metadata: Track metadata and analysis data
            
        Returns:
            True if cached successfully
        """
        try:
            # Get file stats
            file_stat = Path(file_path).stat()
            file_hash = self._calculate_file_hash(file_path)
            
            # Extract metadata if not provided
            if not metadata and MUTAGEN_AVAILABLE:
                metadata = self._extract_metadata(file_path)
            
            # Create track data
            track_data = CachedTrackData(
                file_path=file_path,
                file_hash=file_hash,
                file_size=file_stat.st_size,
                last_modified=file_stat.st_mtime,
                cached_at=time.time(),
                access_count=0,
                last_accessed=time.time(),
                **metadata
            )
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO track_cache 
                    (file_path, file_hash, file_size, last_modified,
                     title, artist, album, genre, duration, bitrate,
                     bpm, key, energy, cached_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track_data.file_path, track_data.file_hash, track_data.file_size,
                    track_data.last_modified, track_data.title, track_data.artist,
                    track_data.album, track_data.genre, track_data.duration,
                    track_data.bitrate, track_data.bpm, track_data.key,
                    track_data.energy, track_data.cached_at, track_data.access_count,
                    track_data.last_accessed
                ))
                conn.commit()
            
            # Add to memory cache
            self._add_to_memory_cache(track_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cache track data for {file_path}: {e}")
            return False
    
    def remove_from_cache(self, file_path: str) -> bool:
        """
        Remove track from cache.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if removed successfully
        """
        try:
            # Remove from memory cache
            if file_path in self.memory_cache:
                del self.memory_cache[file_path]
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM track_cache WHERE file_path = ?", (file_path,))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove from cache: {file_path}: {e}")
            return False
    
    def clear_cache(self, older_than_days: int = 0) -> int:
        """
        Clear cache entries.
        
        Args:
            older_than_days: Remove entries older than this many days (0 = all)
            
        Returns:
            Number of entries removed
        """
        try:
            if older_than_days > 0:
                cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM track_cache WHERE cached_at < ?",
                        (cutoff_time,)
                    )
                    count = cursor.fetchone()[0]
                    
                    conn.execute("DELETE FROM track_cache WHERE cached_at < ?", (cutoff_time,))
                    conn.commit()
                
                # Clear matching items from memory cache
                to_remove = [
                    path for path, data in self.memory_cache.items()
                    if data.cached_at < cutoff_time
                ]
                for path in to_remove:
                    del self.memory_cache[path]
            else:
                # Clear all
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM track_cache")
                    count = cursor.fetchone()[0]
                    
                    conn.execute("DELETE FROM track_cache")
                    conn.commit()
                
                self.memory_cache.clear()
            
            self.logger.info(f"Cleared {count} cache entries")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM track_cache")
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT SUM(file_size) FROM track_cache")
                total_size = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("""
                    SELECT AVG(access_count), MAX(access_count) 
                    FROM track_cache WHERE access_count > 0
                """)
                avg_access, max_access = cursor.fetchone()
            
            return {
                'total_entries': total_entries,
                'memory_entries': len(self.memory_cache),
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': str(self.cache_dir),
                'avg_access_count': avg_access or 0,
                'max_access_count': max_access or 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def _is_cache_valid(self, track_data: CachedTrackData) -> bool:
        """Check if cached data is still valid."""
        try:
            file_path = Path(track_data.file_path)
            
            # Check if file still exists
            if not file_path.exists():
                return False
            
            # Check if file was modified
            current_mtime = file_path.stat().st_mtime
            if abs(current_mtime - track_data.last_modified) > 1:  # 1 second tolerance
                return False
            
            # Check if file size changed
            current_size = file_path.stat().st_size
            if current_size != track_data.file_size:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _update_access_stats(self, track_data: CachedTrackData):
        """Update access statistics."""
        track_data.access_count += 1
        track_data.last_accessed = time.time()
        
        # Update database asynchronously (don't block for this)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE track_cache 
                    SET access_count = ?, last_accessed = ?
                    WHERE file_path = ?
                """, (track_data.access_count, track_data.last_accessed, track_data.file_path))
                conn.commit()
        except Exception as e:
            self.logger.debug(f"Failed to update access stats: {e}")
    
    def _add_to_memory_cache(self, track_data: CachedTrackData):
        """Add track data to memory cache with LRU eviction."""
        # Add new item
        self.memory_cache[track_data.file_path] = track_data
        
        # Evict old items if cache is full
        if len(self.memory_cache) > self.max_memory_cache:
            # Remove least recently accessed items
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            # Remove oldest 10% of items
            to_remove = len(sorted_items) - int(self.max_memory_cache * 0.9)
            for i in range(to_remove):
                path_to_remove = sorted_items[i][0]
                del self.memory_cache[path_to_remove]
    
    def _row_to_track_data(self, row) -> CachedTrackData:
        """Convert database row to CachedTrackData."""
        return CachedTrackData(
            file_path=row[0],
            file_hash=row[1],
            file_size=row[2],
            last_modified=row[3],
            title=row[4],
            artist=row[5],
            album=row[6],
            genre=row[7],
            duration=row[8],
            bitrate=row[9],
            bpm=row[10],
            key=row[11],
            energy=row[12],
            cached_at=row[13],
            access_count=row[14],
            last_accessed=row[15]
        )
    
    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate file hash for cache validation."""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Only hash first and last chunks for speed
                chunk = f.read(chunk_size)
                hasher.update(chunk)
                
                # Seek to end and read last chunk
                f.seek(-min(chunk_size, f.tell()), 2)
                chunk = f.read(chunk_size)
                hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception:
            # Fallback to file size + mtime
            stat = Path(file_path).stat()
            return f"{stat.st_size}_{stat.st_mtime}"
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic metadata from audio file."""
        if not MUTAGEN_AVAILABLE:
            return {}
        
        try:
            audio_file = MutagenFile(file_path)
            if not audio_file:
                return {}
            
            metadata = {}
            
            # Basic tags
            if 'TIT2' in audio_file:  # Title
                metadata['title'] = str(audio_file['TIT2'][0])
            elif 'TITLE' in audio_file:
                metadata['title'] = str(audio_file['TITLE'][0])
            
            if 'TPE1' in audio_file:  # Artist
                metadata['artist'] = str(audio_file['TPE1'][0])
            elif 'ARTIST' in audio_file:
                metadata['artist'] = str(audio_file['ARTIST'][0])
            
            if 'TALB' in audio_file:  # Album
                metadata['album'] = str(audio_file['TALB'][0])
            elif 'ALBUM' in audio_file:
                metadata['album'] = str(audio_file['ALBUM'][0])
            
            if 'TCON' in audio_file:  # Genre
                metadata['genre'] = str(audio_file['TCON'][0])
            elif 'GENRE' in audio_file:
                metadata['genre'] = str(audio_file['GENRE'][0])
            
            # Technical info
            if hasattr(audio_file, 'info'):
                if hasattr(audio_file.info, 'length'):
                    metadata['duration'] = audio_file.info.length
                if hasattr(audio_file.info, 'bitrate'):
                    metadata['bitrate'] = audio_file.info.bitrate
            
            return metadata
            
        except Exception as e:
            self.logger.debug(f"Failed to extract metadata from {file_path}: {e}")
            return {}