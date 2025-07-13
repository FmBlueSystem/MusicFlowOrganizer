"""
MixIn Key Integration Module for MusicFlow Organizer
===================================================

Professional integration with MixIn Key analysis results for:
- Reading MixIn Key database files
- Extracting BPM, Key, and Energy data
- Genre organization based on professional DJ mixing rules
- Harmonic mixing compatibility using Camelot Wheel

This module handles all audio analysis data from MixIn Key,
focusing on organization and workflow optimization for DJs.
"""

import logging
import sqlite3
import json
import os
import re
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import xml.etree.ElementTree as ET

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logging.warning("Mutagen not available - limited metadata support")


@dataclass
class MixInKeyTrackData:
    """Container for MixIn Key analyzed track data."""
    
    # File information
    file_path: str
    filename: str
    artist: str = ""
    title: str = ""
    album: str = ""
    genre: str = ""
    
    # MixIn Key analysis results
    bpm: Optional[float] = None
    key: Optional[str] = None  # Camelot notation (e.g., "8A", "12B")
    energy: Optional[int] = None  # 1-10 scale
    
    # Additional metadata
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    year: Optional[int] = None
    label: Optional[str] = None
    
    # File properties
    file_size: Optional[int] = None
    date_added: Optional[str] = None
    last_played: Optional[str] = None
    play_count: int = 0
    
    # Analysis metadata
    analyzed_by_mixinkey: bool = False
    analysis_date: Optional[str] = None


class MixInKeyIntegration:
    """
    Professional MixIn Key integration for DJ workflow optimization.
    
    Reads and processes MixIn Key analysis results to provide intelligent
    music organization based on harmonic mixing principles and DJ best practices.
    """
    
    # Camelot Wheel for harmonic mixing
    CAMELOT_WHEEL = {
        '1A': {'compatible': ['1A', '1B', '2A', '12A'], 'note': 'Ab minor'},
        '2A': {'compatible': ['2A', '2B', '3A', '1A'], 'note': 'Eb minor'},
        '3A': {'compatible': ['3A', '3B', '4A', '2A'], 'note': 'Bb minor'},
        '4A': {'compatible': ['4A', '4B', '5A', '3A'], 'note': 'F minor'},
        '5A': {'compatible': ['5A', '5B', '6A', '4A'], 'note': 'C minor'},
        '6A': {'compatible': ['6A', '6B', '7A', '5A'], 'note': 'G minor'},
        '7A': {'compatible': ['7A', '7B', '8A', '6A'], 'note': 'D minor'},
        '8A': {'compatible': ['8A', '8B', '9A', '7A'], 'note': 'A minor'},
        '9A': {'compatible': ['9A', '9B', '10A', '8A'], 'note': 'E minor'},
        '10A': {'compatible': ['10A', '10B', '11A', '9A'], 'note': 'B minor'},
        '11A': {'compatible': ['11A', '11B', '12A', '10A'], 'note': 'F# minor'},
        '12A': {'compatible': ['12A', '12B', '1A', '11A'], 'note': 'Db minor'},
        '1B': {'compatible': ['1B', '1A', '2B', '12B'], 'note': 'B major'},
        '2B': {'compatible': ['2B', '2A', '3B', '1B'], 'note': 'F# major'},
        '3B': {'compatible': ['3B', '3A', '4B', '2B'], 'note': 'Db major'},
        '4B': {'compatible': ['4B', '4A', '5B', '3B'], 'note': 'Ab major'},
        '5B': {'compatible': ['5B', '5A', '6B', '4B'], 'note': 'Eb major'},
        '6B': {'compatible': ['6B', '6A', '7B', '5B'], 'note': 'Bb major'},
        '7B': {'compatible': ['7B', '7A', '8B', '6B'], 'note': 'F major'},
        '8B': {'compatible': ['8B', '8A', '9B', '7B'], 'note': 'C major'},
        '9B': {'compatible': ['9B', '9A', '10B', '8B'], 'note': 'G major'},
        '10B': {'compatible': ['10B', '10A', '11B', '9B'], 'note': 'D major'},
        '11B': {'compatible': ['11B', '11A', '12B', '10B'], 'note': 'A major'},
        '12B': {'compatible': ['12B', '12A', '1B', '11B'], 'note': 'E major'}
    }
    
    # Energy level categories for DJ organization
    ENERGY_CATEGORIES = {
        (1, 3): "Intro/Outro",
        (4, 5): "Low Energy",
        (6, 7): "Medium Energy", 
        (8, 9): "High Energy",
        (10, 10): "Peak Time"
    }
    
    # BPM categories for mixing
    BPM_CATEGORIES = {
        (60, 100): "Chill/Ambient",
        (100, 115): "Hip Hop/R&B",
        (115, 125): "Deep House/Disco",
        (125, 132): "House/Tech House",
        (132, 140): "Trance/Progressive",
        (140, 150): "Techno/Hard Dance",
        (150, 180): "Drum & Bass/Hardcore",
        (180, 220): "Speedcore/Gabber"
    }
    
    def __init__(self, database_path: Optional[str] = None):
        """Initialize MixIn Key integration."""
        self.logger = logging.getLogger(__name__)
        self.tracks_database = {}
        self.database_path = database_path
        
        self.logger.info("MixIn Key integration initialized")
    
    def _extract_path_from_bookmark_data(self, bookmark_data: bytes) -> Optional[str]:
        """
        Extract file path from macOS Security-Scoped Bookmark data.
        
        Args:
            bookmark_data: Raw bookmark data from ZBOOKMARKDATA field
            
        Returns:
            Extracted file path if successful, None otherwise
        """
        if not bookmark_data:
            return None
            
        try:
            # Convert bookmark data to string for pattern matching
            bookmark_str = bookmark_data.decode('utf-8', errors='ignore')
            
            # Look for file path patterns in the bookmark data
            # Patterns commonly found in bookmark data:
            
            # Pattern 1: Look for volume paths like "/Volumes/..."
            volume_pattern = r'/Volumes/[^/\x00]+(?:/[^/\x00]+)*\.(?:mp3|flac|wav|m4a|aiff|ogg|mp4|m4p)'
            volume_matches = re.findall(volume_pattern, bookmark_str, re.IGNORECASE)
            if volume_matches:
                # Return the longest match (most complete path)
                path = max(volume_matches, key=len)
                if Path(path).exists():
                    self.logger.debug(f"Found volume path: {path}")
                    return path
            
            # Pattern 2: Look for Users paths like "/Users/..."
            users_pattern = r'/Users/[^/\x00]+(?:/[^/\x00]+)*\.(?:mp3|flac|wav|m4a|aiff|ogg|mp4|m4p)'
            users_matches = re.findall(users_pattern, bookmark_str, re.IGNORECASE)
            if users_matches:
                path = max(users_matches, key=len)
                if Path(path).exists():
                    self.logger.debug(f"Found users path: {path}")
                    return path
                    
            # Pattern 3: Look for any absolute path pattern
            abs_pattern = r'/[^/\x00]+(?:/[^/\x00]+)*\.(?:mp3|flac|wav|m4a|aiff|ogg|mp4|m4p)'
            abs_matches = re.findall(abs_pattern, bookmark_str, re.IGNORECASE)
            if abs_matches:
                # Filter out obviously invalid paths and return the longest valid one
                valid_paths = []
                for path in abs_matches:
                    # Skip paths that look like they contain binary junk
                    if not re.search(r'[\x00-\x1f\x7f-\xff]', path) and len(path) > 10:
                        if Path(path).exists():
                            valid_paths.append(path)
                
                if valid_paths:
                    path = max(valid_paths, key=len)
                    self.logger.debug(f"Found absolute path: {path}")
                    return path
            
            # Try to extract paths using a different approach - look for filename patterns
            try:
                # Some bookmark data might be structured differently
                # Look for filename.extension patterns and try to reconstruct paths
                filename_pattern = r'([^/\x00]+\.(?:mp3|flac|wav|m4a|aiff|ogg|mp4|m4p))'
                filename_matches = re.findall(filename_pattern, bookmark_str, re.IGNORECASE)
                
                if filename_matches:
                    # Try to find the full path containing this filename
                    for filename in filename_matches:
                        # Look for this filename in the broader context
                        context_pattern = rf'[^/\x00]*{re.escape(filename)}'
                        context_matches = re.findall(context_pattern, bookmark_str, re.IGNORECASE)
                        for match in context_matches:
                            if '/' in match:
                                # Try to extract a reasonable path
                                potential_path = f"/{match.lstrip('/')}"
                                if Path(potential_path).exists():
                                    self.logger.debug(f"Found context path: {potential_path}")
                                    return potential_path
                                    
            except Exception as context_error:
                self.logger.debug(f"Context extraction failed: {context_error}")
            
            self.logger.debug("No valid path found in bookmark data")
            return None
            
        except Exception as e:
            self.logger.debug(f"Failed to extract path from bookmark data: {e}")
            return None
    
    def scan_mixinkey_database(self, library_path: str) -> Dict[str, MixInKeyTrackData]:
        """
        Scan for MixIn Key database files and extract track data.
        
        Args:
            library_path: Path to music library to scan
            
        Returns:
            Dictionary mapping file paths to track data
        """
        self.logger.info(f"Scanning for MixIn Key data in: {library_path}")
        
        tracks = {}
        
        # Use configured database path if available
        if self.database_path and Path(self.database_path).exists():
            self.logger.info(f"Using configured MixIn Key database: {self.database_path}")
            db_tracks = self._read_sqlite_database(Path(self.database_path))
            tracks.update(db_tracks)
        else:
            # Look for MixIn Key database files in library
            mixinkey_files = self._find_mixinkey_files(library_path)
            
            for db_file in mixinkey_files:
                self.logger.info(f"Processing MixIn Key database: {db_file}")
                
                if db_file.suffix.lower() in ['.db', '.mikdb']:
                    # SQLite database (including .mikdb format)
                    db_tracks = self._read_sqlite_database(db_file)
                    tracks.update(db_tracks)
                elif db_file.suffix.lower() == '.xml':
                    # XML export
                    xml_tracks = self._read_xml_database(db_file)
                    tracks.update(xml_tracks)
        
        # Fallback: scan individual audio files for MixIn Key tags
        if not tracks:
            self.logger.info("No MixIn Key database found, scanning individual files...")
            tracks = self._scan_audio_files_for_mixinkey_tags(library_path)
        
        self.tracks_database = tracks
        self.logger.info(f"Loaded {len(tracks)} tracks with MixIn Key data")
        
        return tracks
    
    def _find_mixinkey_files(self, library_path: str) -> List[Path]:
        """Find MixIn Key database files."""
        search_paths = [
            Path(library_path),
            Path.home() / "Music" / "MixIn Key",
            Path.home() / "Documents" / "MixIn Key",
            # Common MixIn Key database locations - CORRECT paths
            Path.home() / "Library" / "Application Support" / "Mixed In Key 11",  # Newest version location
            Path.home() / "Library" / "Application Support" / "Mixedinkey",  # Real location (one word)
            Path.home() / "Library" / "Application Support" / "Mixed In Key 10",  # Legacy fallback
            Path.home() / "Library" / "Application Support" / "MixIn Key",  # Legacy fallback
            Path("/Applications/MixIn Key.app/Contents/Resources")
        ]
        
        mixinkey_files = []
        
        for search_path in search_paths:
            if search_path.exists():
                # Look for database files including .mikdb format
                for pattern in ["*.mikdb", "*.db", "*.sqlite", "*.xml"]:
                    found_files = list(search_path.rglob(pattern))
                    mixinkey_files.extend(found_files)
        
        # Remove duplicates and prioritize Collection11.mikdb over Collection10.mikdb
        unique_files = list(set(mixinkey_files))
        
        # Sort to prioritize newer versions first (Collection20 gets priority 0!)
        def sort_priority(file_path):
            name = file_path.name.lower()
            if 'collection20' in name:
                return 0  # Highest priority - newest version
            elif 'collection19' in name:
                return 1  # Second priority
            elif 'collection18' in name:
                return 2  # Third priority
            elif 'collection17' in name:
                return 3  # Fourth priority
            elif 'collection16' in name:
                return 4  # Fifth priority
            elif 'collection15' in name:
                return 5  # Sixth priority
            elif 'collection14' in name:
                return 6  # Seventh priority
            elif 'collection13' in name:
                return 7  # Eighth priority
            elif 'collection12' in name:
                return 8  # Ninth priority
            elif 'collection11' in name:
                return 9  # Tenth priority
            elif 'collection10' in name:
                return 10  # Eleventh priority
            elif name.endswith('.mikdb'):
                return 11  # Other .mikdb files
            elif name.endswith('.db'):
                return 12  # SQLite files
            else:
                return 13  # XML and others
        
        unique_files.sort(key=sort_priority)
        return unique_files
    
    def _read_sqlite_database(self, db_path: Path) -> Dict[str, MixInKeyTrackData]:
        """Read MixIn Key SQLite database."""
        tracks = {}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # First, get all table names to understand the schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"🔍 DEBUG: Database tables found in {db_path.name}: {tables}")
            self.logger.info(f"Database tables found in {db_path.name}: {tables}")
            
            # Also get schema information for each table
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    print(f"🔍 DEBUG: Table '{table}' columns: {column_names}")
                    self.logger.info(f"Table '{table}' columns: {column_names}")
                except sqlite3.Error as e:
                    print(f"❌ DEBUG: Could not get schema for table {table}: {e}")
                    self.logger.debug(f"Could not get schema for table {table}: {e}")
            
            # Try different table structures based on Mixed In Key versions
            table_queries = [
                # Core Data format (Collection11.mikdb, Collection10.mikdb)
                "SELECT * FROM ZSONG",
                # Legacy formats
                "SELECT * FROM Music",
                "SELECT * FROM Tracks", 
                "SELECT * FROM tracks",
                "SELECT * FROM music",
                "SELECT * FROM library",
                "SELECT * FROM Files"
            ]
            
            successful_query = None
            for query in table_queries:
                try:
                    cursor.execute(query)
                    columns = [description[0] for description in cursor.description]
                    self.logger.info(f"Table schema - Columns: {columns}")
                    
                    rows = cursor.fetchall()
                    print(f"🔍 DEBUG: Query '{query}' returned {len(rows)} rows")
                    self.logger.info(f"Found {len(rows)} rows in database")
                    
                    if len(rows) > 0:
                        # Process the data
                        for row in rows:
                            track_data = dict(zip(columns, row))
                            track = self._parse_database_row(track_data)
                            if track and track.file_path:
                                tracks[track.file_path] = track
                        
                        successful_query = query
                        self.logger.info(f"Successfully read {len(tracks)} tracks from query: {query}")
                        break  # Success, stop trying other queries
                    
                except sqlite3.Error as e:
                    print(f"❌ DEBUG: Query failed: {query} - {e}")
                    self.logger.debug(f"Query failed: {query} - {e}")
                    continue
            
            if not tracks and successful_query is None:
                self.logger.warning(f"No valid data found in database {db_path}. Available tables: {tables}")
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to read SQLite database {db_path}: {e}")
        
        return tracks
    
    def _read_xml_database(self, xml_path: Path) -> Dict[str, MixInKeyTrackData]:
        """Read MixIn Key XML export."""
        tracks = {}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Parse XML structure (adapt based on MixIn Key XML format)
            for track_element in root.findall(".//track"):
                track = self._parse_xml_track(track_element)
                if track and track.file_path:
                    tracks[track.file_path] = track
                    
        except Exception as e:
            self.logger.error(f"Failed to read XML database {xml_path}: {e}")
        
        return tracks
    
    def _scan_audio_files_for_mixinkey_tags(self, library_path: str) -> Dict[str, MixInKeyTrackData]:
        """Scan individual audio files for MixIn Key metadata tags."""
        tracks = {}
        
        if not MUTAGEN_AVAILABLE:
            self.logger.warning("Mutagen not available - cannot scan audio file tags")
            return tracks
        
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aiff', '.ogg'}
        
        for root, dirs, files in os.walk(library_path):
            for file in files:
                if Path(file).suffix.lower() in audio_extensions:
                    file_path = os.path.join(root, file)
                    
                    track = self._extract_mixinkey_tags(file_path)
                    if track:
                        tracks[file_path] = track
        
        return tracks
    
    def _parse_database_row(self, row_data: Dict) -> Optional[MixInKeyTrackData]:
        """Parse a database row into MixInKeyTrackData."""
        try:
            # Map database field names for different Mixed In Key formats
            field_mapping = {
                # Core Data format (ZSONG table) - Collection11.mikdb, Collection10.mikdb
                'ZARTIST': 'artist',
                'ZNAME': 'title',  # ZNAME is the track title in Mixed In Key
                'ZALBUM': 'album',
                'ZGENRE': 'genre',
                'ZTEMPO': 'bpm',   # ZTEMPO contains the actual BPM
                'ZKEY': 'key',     # ZKEY contains Camelot notation
                'ZENERGY': 'energy', # ZENERGY is the energy level (1-10)
                'ZYEAR': 'year',
                'ZBITRATE': 'bitrate',
                'ZFILESIZE': 'file_size',
                'ZBOOKMARKDATA': 'bookmark_data',  # Security-Scoped Bookmark containing real file path
                # Note: ZVOLUME not mapped as it's not in MixInKeyTrackData dataclass
                
                # Legacy formats (for newer versions if they exist)
                'FilePath': 'file_path',
                'Directory': 'file_path',
                'path': 'file_path',
                'filepath': 'file_path',
                'location': 'file_path',
                'FileName': 'filename',
                'filename': 'filename',
                
                # Standard metadata fields
                'Artist': 'artist',
                'artist': 'artist',
                'Title': 'title', 
                'title': 'title',
                'Album': 'album',
                'album': 'album',
                'Genre': 'genre',
                'genre': 'genre',
                
                # Standard analysis fields
                'BPM': 'bpm',
                'bpm': 'bpm',
                'tempo': 'bpm',
                'Key': 'key',
                'key': 'key',
                'camelot': 'key',
                'Energy': 'energy',
                'energy': 'energy',
                'Duration': 'duration',
                'duration': 'duration',
                'Bitrate': 'bitrate',
                'bitrate': 'bitrate',
                'Year': 'year',
                'year': 'year',
                'Label': 'label',
                'label': 'label'
            }
            
            track_data = {}
            
            # Debug: Log available fields
            self.logger.debug(f"Row data keys: {list(row_data.keys())}")
            
            # Map fields
            for db_field, track_field in field_mapping.items():
                if db_field in row_data and row_data[db_field] is not None:
                    value = row_data[db_field]
                    # Handle string/path concatenation for Directory + FileName
                    if db_field == 'Directory' and 'FileName' in row_data:
                        if value and row_data['FileName']:
                            track_data[track_field] = str(Path(value) / row_data['FileName'])
                    else:
                        track_data[track_field] = value
                    self.logger.debug(f"Mapped {db_field} -> {track_field}: {value}")
            
            # Handle file path - Extract from bookmark data if available, otherwise use existing logic
            if 'file_path' not in track_data or not track_data['file_path']:
                # First try to extract real path from bookmark data
                extracted_path = None
                if 'bookmark_data' in track_data and track_data['bookmark_data']:
                    extracted_path = self._extract_path_from_bookmark_data(track_data['bookmark_data'])
                    if extracted_path:
                        track_data['file_path'] = extracted_path
                        self.logger.debug(f"Extracted real path from bookmark: {extracted_path}")
                
                # If no bookmark extraction succeeded, fall back to creating placeholder
                if not extracted_path:
                    if 'artist' in track_data and 'title' in track_data:
                        # Create a reasonable file path from available metadata
                        artist = track_data.get('artist', 'Unknown Artist').replace('/', '_')
                        title = track_data.get('title', 'Unknown Title').replace('/', '_')
                        album = track_data.get('album', '').replace('/', '_')
                        
                        # Generate a reasonable filename
                        if album:
                            filename = f"{artist} - {album} - {title}.mp3"
                        else:
                            filename = f"{artist} - {title}.mp3"
                        
                        # Create a placeholder path (this won't be a real path but will allow processing)
                        track_data['file_path'] = f"/MixInKey_Placeholder/{artist}/{filename}"
                        self.logger.debug(f"Generated placeholder path: {track_data['file_path']}")
                    else:
                        self.logger.debug("No valid file path found and insufficient metadata")
                        return None
            
            # Set filename if not already set
            if 'filename' not in track_data and 'file_path' in track_data:
                track_data['filename'] = Path(track_data['file_path']).name
            
            # Convert numeric fields
            for field in ['bpm', 'energy', 'duration', 'bitrate', 'year']:
                if field in track_data and track_data[field] is not None:
                    try:
                        if field == 'bpm':
                            track_data[field] = float(track_data[field])
                        else:
                            track_data[field] = int(track_data[field])
                    except (ValueError, TypeError):
                        self.logger.debug(f"Could not convert {field}: {track_data[field]}")
                        track_data[field] = None
            
            # Remove bookmark_data as it's not part of MixInKeyTrackData dataclass
            if 'bookmark_data' in track_data:
                del track_data['bookmark_data']
            
            result = MixInKeyTrackData(**track_data, analyzed_by_mixinkey=True)
            self.logger.debug(f"Created track: {result.filename} with BPM: {result.bpm}, Key: {result.key}")
            return result
            
        except Exception as e:
            self.logger.debug(f"Failed to parse database row: {e}")
            self.logger.debug(f"Row data: {row_data}")
            return None
    
    def _parse_xml_track(self, track_element) -> Optional[MixInKeyTrackData]:
        """Parse XML track element."""
        try:
            track_data = {}
            
            # Extract attributes and child elements
            for attr in ['path', 'artist', 'title', 'album', 'bpm', 'key', 'energy']:
                value = track_element.get(attr) or track_element.findtext(attr)
                if value:
                    track_data[attr] = value
            
            if 'path' in track_data:
                track_data['file_path'] = track_data.pop('path')
                return MixInKeyTrackData(**track_data, analyzed_by_mixinkey=True)
            
        except Exception as e:
            self.logger.debug(f"Failed to parse XML track: {e}")
        
        return None
    
    def _extract_mixinkey_tags(self, file_path: str) -> Optional[MixInKeyTrackData]:
        """Extract MixIn Key tags from audio file."""
        try:
            audio_file = MutagenFile(file_path)
            if not audio_file:
                return None
            
            # Look for MixIn Key specific tags
            mixinkey_tags = {}
            
            # Common MixIn Key tag names
            tag_mappings = {
                'TBPM': 'bpm',
                'BPM': 'bpm', 
                'TKEY': 'key',
                'KEY': 'key',
                'TXXX:ENERGY': 'energy',
                'ENERGY': 'energy',
                'TXXX:CAMELOT': 'key',
                'CAMELOT': 'key'
            }
            
            for tag_name, field_name in tag_mappings.items():
                if tag_name in audio_file:
                    value = audio_file[tag_name]
                    if isinstance(value, list) and value:
                        value = value[0]
                    mixinkey_tags[field_name] = str(value)
            
            # Only create track data if we found MixIn Key specific tags
            if mixinkey_tags:
                # Get basic metadata
                track_data = {
                    'file_path': file_path,
                    'filename': Path(file_path).name,
                    'analyzed_by_mixinkey': True
                }
                
                # Add basic tags
                if 'TIT2' in audio_file:  # Title
                    track_data['title'] = str(audio_file['TIT2'][0])
                if 'TPE1' in audio_file:  # Artist
                    track_data['artist'] = str(audio_file['TPE1'][0])
                if 'TALB' in audio_file:  # Album
                    track_data['album'] = str(audio_file['TALB'][0])
                if 'TCON' in audio_file:  # Genre
                    track_data['genre'] = str(audio_file['TCON'][0])
                
                # Add MixIn Key data
                track_data.update(mixinkey_tags)
                
                # Convert types
                if 'bpm' in track_data:
                    try:
                        track_data['bpm'] = float(track_data['bpm'])
                    except (ValueError, TypeError):
                        pass
                
                if 'energy' in track_data:
                    try:
                        track_data['energy'] = int(track_data['energy'])
                    except (ValueError, TypeError):
                        pass
                
                return MixInKeyTrackData(**track_data)
            
        except Exception as e:
            self.logger.debug(f"Failed to extract MixIn Key tags from {file_path}: {e}")
        
        return None
    
    def get_compatible_tracks(self, track: MixInKeyTrackData, 
                            max_results: int = 10) -> List[MixInKeyTrackData]:
        """
        Find tracks compatible for mixing with the given track.
        
        Args:
            track: Source track to find matches for
            max_results: Maximum number of results to return
            
        Returns:
            List of compatible tracks sorted by compatibility
        """
        compatible = []
        
        if not track.key or not track.bpm:
            return compatible
        
        for other_track in self.tracks_database.values():
            if (other_track.file_path == track.file_path or 
                not other_track.key or not other_track.bpm):
                continue
            
            compatibility_score = self._calculate_compatibility(track, other_track)
            if compatibility_score > 0:
                compatible.append((other_track, compatibility_score))
        
        # Sort by compatibility score
        compatible.sort(key=lambda x: x[1], reverse=True)
        
        return [track for track, score in compatible[:max_results]]
    
    def _calculate_compatibility(self, track1: MixInKeyTrackData, 
                               track2: MixInKeyTrackData) -> float:
        """Calculate mixing compatibility score between two tracks."""
        score = 0.0
        
        # Key compatibility (Camelot Wheel)
        if track1.key and track2.key:
            if track2.key in self.CAMELOT_WHEEL.get(track1.key, {}).get('compatible', []):
                score += 0.4  # High weight for harmonic compatibility
        
        # BPM compatibility
        if track1.bpm and track2.bpm:
            bpm_diff = abs(track1.bpm - track2.bpm)
            if bpm_diff <= 2:
                score += 0.3  # Perfect BPM match
            elif bpm_diff <= 6:
                score += 0.2  # Good BPM match
            elif bpm_diff <= 12:
                score += 0.1  # Acceptable BPM match
            
            # Check for double/half tempo compatibility
            if abs(track1.bpm - track2.bpm * 2) <= 6 or abs(track1.bpm * 2 - track2.bpm) <= 6:
                score += 0.15
        
        # Energy level compatibility
        if track1.energy and track2.energy:
            energy_diff = abs(track1.energy - track2.energy)
            if energy_diff <= 1:
                score += 0.2
            elif energy_diff <= 2:
                score += 0.1
        
        # Genre similarity
        if track1.genre and track2.genre:
            if track1.genre == track2.genre:
                score += 0.1
        
        return score
    
    def get_organization_suggestions(self, track: MixInKeyTrackData) -> List[Tuple[str, List[str]]]:
        """
        Get organization suggestions for a track.
        
        Returns:
            List of (organization_type, folder_path) tuples
        """
        suggestions = []
        
        # By Key organization
        if track.key:
            key_path = ["By Key", f"{track.key} - {self.CAMELOT_WHEEL.get(track.key, {}).get('note', 'Unknown')}"]
            suggestions.append(("Harmonic", key_path))
        
        # By BPM organization
        if track.bpm:
            bpm_category = self._get_bpm_category(track.bpm)
            bpm_path = ["By BPM", bpm_category, f"{int(track.bpm)} BPM"]
            suggestions.append(("Tempo", bpm_path))
        
        # By Energy organization
        if track.energy:
            energy_category = self._get_energy_category(track.energy)
            energy_path = ["By Energy", energy_category]
            suggestions.append(("Energy", energy_path))
        
        # By Genre organization
        if track.genre:
            genre_path = ["By Genre", track.genre]
            suggestions.append(("Genre", genre_path))
        
        return suggestions
    
    def _get_bpm_category(self, bpm: float) -> str:
        """Get BPM category name."""
        for (min_bpm, max_bpm), category in self.BPM_CATEGORIES.items():
            if min_bpm <= bpm <= max_bpm:
                return category
        return "Other"
    
    def _get_energy_category(self, energy: int) -> str:
        """Get energy category name."""
        for (min_energy, max_energy), category in self.ENERGY_CATEGORIES.items():
            if min_energy <= energy <= max_energy:
                return category
        return "Unknown"
    
    def export_dj_playlists(self, output_dir: str) -> bool:
        """
        Export DJ-ready playlists based on MixIn Key analysis.
        
        Args:
            output_dir: Directory to save playlist files
            
        Returns:
            True if successful
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Create playlists by key
            self._create_key_playlists(output_path)
            
            # Create playlists by energy
            self._create_energy_playlists(output_path)
            
            # Create BPM-based playlists
            self._create_bpm_playlists(output_path)
            
            self.logger.info(f"DJ playlists exported to {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export playlists: {e}")
            return False
    
    def _create_key_playlists(self, output_path: Path):
        """Create playlists organized by musical key."""
        key_groups = {}
        
        for track in self.tracks_database.values():
            if track.key:
                if track.key not in key_groups:
                    key_groups[track.key] = []
                key_groups[track.key].append(track)
        
        for key, tracks in key_groups.items():
            playlist_name = f"Key_{key}_{self.CAMELOT_WHEEL.get(key, {}).get('note', 'Unknown').replace(' ', '_')}.m3u"
            self._write_m3u_playlist(output_path / playlist_name, tracks)
    
    def _create_energy_playlists(self, output_path: Path):
        """Create playlists organized by energy level."""
        energy_groups = {}
        
        for track in self.tracks_database.values():
            if track.energy:
                category = self._get_energy_category(track.energy)
                if category not in energy_groups:
                    energy_groups[category] = []
                energy_groups[category].append(track)
        
        for category, tracks in energy_groups.items():
            playlist_name = f"Energy_{category.replace(' ', '_').replace('/', '_')}.m3u"
            self._write_m3u_playlist(output_path / playlist_name, tracks)
    
    def _create_bpm_playlists(self, output_path: Path):
        """Create playlists organized by BPM range."""
        bpm_groups = {}
        
        for track in self.tracks_database.values():
            if track.bpm:
                # Group by 10 BPM ranges
                bpm_range = f"{int(track.bpm // 10) * 10}-{int(track.bpm // 10) * 10 + 9}"
                if bpm_range not in bpm_groups:
                    bpm_groups[bpm_range] = []
                bpm_groups[bpm_range].append(track)
        
        for bpm_range, tracks in bpm_groups.items():
            playlist_name = f"BPM_{bpm_range}.m3u"
            self._write_m3u_playlist(output_path / playlist_name, tracks)
    
    def _write_m3u_playlist(self, playlist_path: Path, tracks: List[MixInKeyTrackData]):
        """Write M3U playlist file."""
        try:
            with open(playlist_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                
                for track in tracks:
                    # Write extended info
                    duration = int(track.duration) if track.duration else -1
                    artist_title = f"{track.artist} - {track.title}" if track.artist and track.title else track.filename
                    f.write(f"#EXTINF:{duration},{artist_title}\n")
                    
                    # Write file path
                    f.write(f"{track.file_path}\n")
                    
        except Exception as e:
            self.logger.error(f"Failed to write playlist {playlist_path}: {e}")
    
    def get_track_data(self, file_path: str) -> Optional[MixInKeyTrackData]:
        """Get track data for a specific file."""
        return self.tracks_database.get(file_path)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the analyzed library."""
        total_tracks = len(self.tracks_database)
        
        if total_tracks == 0:
            return {}
        
        # Count tracks by various categories
        keys_count = len([t for t in self.tracks_database.values() if t.key])
        bpm_count = len([t for t in self.tracks_database.values() if t.bpm])
        energy_count = len([t for t in self.tracks_database.values() if t.energy])
        
        # Average BPM
        bpms = [t.bpm for t in self.tracks_database.values() if t.bpm]
        avg_bpm = sum(bpms) / len(bpms) if bpms else 0
        
        # Most common key
        keys = [t.key for t in self.tracks_database.values() if t.key]
        most_common_key = max(set(keys), key=keys.count) if keys else None
        
        return {
            'total_tracks': total_tracks,
            'analyzed_tracks': total_tracks,  # All from MixIn Key
            'tracks_with_key': keys_count,
            'tracks_with_bpm': bpm_count,
            'tracks_with_energy': energy_count,
            'average_bpm': round(avg_bpm, 1),
            'most_common_key': most_common_key,
            'completion_percentage': 100.0  # All tracks from MixIn Key are complete
        }