"""
Asynchronous Filter Engine - Performance Optimization Component
==============================================================

Provides high-performance asynchronous filtering capabilities for large
music libraries with caching and progressive results.

Optimizations:
- Worker thread-based filtering
- Progressive result delivery
- LRU cache for frequent queries
- Batch processing for large datasets
- Memory-efficient streaming

Developed by BlueSystemIO
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from functools import lru_cache
import threading
from queue import Queue, Empty

try:
    from PySide6.QtCore import QThread, Signal, QObject
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Fallback classes for non-Qt environments
    class QThread:
        def __init__(self): pass
        def start(self): pass
        def wait(self): pass
    class Signal:
        def __init__(self, *args): pass
        def emit(self, *args): pass
        def connect(self, func): pass
    class QObject:
        def __init__(self): pass

from .track_analyzer import TrackData


class FilterType(Enum):
    """Available filter types."""
    GENRE = "genre"
    BPM_RANGE = "bpm_range"
    KEY = "key"
    ENERGY = "energy"
    ARTIST = "artist"
    ALBUM = "album"
    YEAR = "year"
    DURATION = "duration"
    TEXT_SEARCH = "text_search"
    CAMELOT_COMPATIBLE = "camelot_compatible"


@dataclass
class FilterCriteria:
    """Filter criteria specification."""
    filter_type: FilterType
    value: Any
    operator: str = "equals"  # equals, contains, range, greater_than, less_than
    case_sensitive: bool = False


@dataclass
class FilterResult:
    """Result of filtering operation."""
    matched_tracks: Dict[str, TrackData]
    total_matches: int
    processing_time: float
    cache_hit: bool = False
    filter_hash: str = ""


class AsyncFilterWorker(QThread):
    """Worker thread for asynchronous filtering operations."""
    
    # Signals for Qt-based applications
    progress_updated = Signal(int, str)  # progress_percent, status_message
    partial_results = Signal(dict)       # partial results for progressive display
    filtering_complete = Signal(object)  # FilterResult
    error_occurred = Signal(str)         # error message
    
    def __init__(self, tracks_database: Dict[str, TrackData], 
                 filter_criteria: List[FilterCriteria],
                 batch_size: int = 100):
        super().__init__()
        self.tracks_database = tracks_database
        self.filter_criteria = filter_criteria
        self.batch_size = batch_size
        self.cancelled = False
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Execute filtering in background thread."""
        try:
            start_time = time.time()
            self.progress_updated.emit(0, "Starting filter operation...")
            
            matched_tracks = {}
            total_tracks = len(self.tracks_database)
            processed = 0
            
            # Process tracks in batches for better responsiveness
            track_items = list(self.tracks_database.items())
            
            for i in range(0, len(track_items), self.batch_size):
                if self.cancelled:
                    return
                
                batch = track_items[i:i + self.batch_size]
                batch_matches = {}
                
                for file_path, track_data in batch:
                    if self.cancelled:
                        return
                    
                    if self._matches_criteria(track_data, self.filter_criteria):
                        batch_matches[file_path] = track_data
                    
                    processed += 1
                
                # Update progress and emit partial results
                progress = int((processed / total_tracks) * 100)
                self.progress_updated.emit(progress, f"Processed {processed}/{total_tracks} tracks")
                
                if batch_matches:
                    matched_tracks.update(batch_matches)
                    self.partial_results.emit(dict(batch_matches))
                
                # Small delay to prevent UI freezing
                if i % (self.batch_size * 5) == 0:
                    time.sleep(0.001)
            
            processing_time = time.time() - start_time
            
            result = FilterResult(
                matched_tracks=matched_tracks,
                total_matches=len(matched_tracks),
                processing_time=processing_time
            )
            
            self.filtering_complete.emit(result)
            
        except Exception as e:
            self.logger.error(f"Filter worker error: {e}")
            self.error_occurred.emit(str(e))
    
    def cancel(self):
        """Cancel the filtering operation."""
        self.cancelled = True
    
    def _matches_criteria(self, track_data: TrackData, criteria: List[FilterCriteria]) -> bool:
        """Check if track matches all filter criteria."""
        for criterion in criteria:
            if not self._matches_single_criterion(track_data, criterion):
                return False
        return True
    
    def _matches_single_criterion(self, track_data: TrackData, criterion: FilterCriteria) -> bool:
        """Check if track matches a single filter criterion."""
        try:
            if criterion.filter_type == FilterType.GENRE:
                if not track_data.genre_classification:
                    return False
                genre = track_data.genre_classification.primary_genre or ""
                return self._string_matches(genre, criterion.value, criterion.operator, criterion.case_sensitive)
            
            elif criterion.filter_type == FilterType.BPM_RANGE:
                if not track_data.mixinkey_data or not track_data.mixinkey_data.bpm:
                    return False
                bpm = track_data.mixinkey_data.bpm
                return self._numeric_matches(bpm, criterion.value, criterion.operator)
            
            elif criterion.filter_type == FilterType.KEY:
                if not track_data.mixinkey_data or not track_data.mixinkey_data.key:
                    return False
                key = track_data.mixinkey_data.key
                return self._string_matches(key, criterion.value, criterion.operator, criterion.case_sensitive)
            
            elif criterion.filter_type == FilterType.ARTIST:
                if not track_data.mixinkey_data or not track_data.mixinkey_data.artist:
                    return False
                artist = track_data.mixinkey_data.artist
                return self._string_matches(artist, criterion.value, criterion.operator, criterion.case_sensitive)
            
            elif criterion.filter_type == FilterType.TEXT_SEARCH:
                # Search in multiple fields
                search_fields = []
                if track_data.mixinkey_data:
                    search_fields.extend([
                        track_data.mixinkey_data.filename or "",
                        track_data.mixinkey_data.artist or "",
                        track_data.mixinkey_data.title or "",
                        track_data.mixinkey_data.album or ""
                    ])
                if track_data.genre_classification:
                    search_fields.append(track_data.genre_classification.primary_genre or "")
                
                search_text = " ".join(search_fields).lower() if not criterion.case_sensitive else " ".join(search_fields)
                search_value = criterion.value.lower() if not criterion.case_sensitive else criterion.value
                
                return search_value in search_text
            
            elif criterion.filter_type == FilterType.CAMELOT_COMPATIBLE:
                # Find tracks with compatible Camelot keys
                if not track_data.mixinkey_data or not track_data.mixinkey_data.key:
                    return False
                
                current_key = track_data.mixinkey_data.key
                target_key = criterion.value
                
                return self._are_camelot_compatible(current_key, target_key)
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking criterion {criterion.filter_type}: {e}")
            return False
    
    def _string_matches(self, value: str, target: str, operator: str, case_sensitive: bool) -> bool:
        """Check if string value matches target based on operator."""
        if not case_sensitive:
            value = value.lower()
            target = target.lower()
        
        if operator == "equals":
            return value == target
        elif operator == "contains":
            return target in value
        elif operator == "starts_with":
            return value.startswith(target)
        elif operator == "ends_with":
            return value.endswith(target)
        else:
            return value == target
    
    def _numeric_matches(self, value: float, target: Any, operator: str) -> bool:
        """Check if numeric value matches target based on operator."""
        if operator == "equals":
            return abs(value - float(target)) < 0.1
        elif operator == "greater_than":
            return value > float(target)
        elif operator == "less_than":
            return value < float(target)
        elif operator == "range":
            # Target should be tuple (min, max)
            min_val, max_val = target
            return min_val <= value <= max_val
        else:
            return value == float(target)
    
    def _are_camelot_compatible(self, key1: str, key2: str) -> bool:
        """Check if two Camelot keys are compatible for mixing."""
        # Simplified compatibility check - adjacent keys on Camelot wheel
        try:
            # Extract number and letter from Camelot notation (e.g., "4A", "9B")
            if len(key1) < 2 or len(key2) < 2:
                return False
            
            num1, letter1 = int(key1[:-1]), key1[-1]
            num2, letter2 = int(key2[:-1]), key2[-1]
            
            # Same key
            if key1 == key2:
                return True
            
            # Adjacent numbers (same letter)
            if letter1 == letter2:
                return abs(num1 - num2) == 1 or abs(num1 - num2) == 11  # Wrap around 12
            
            # Same number (different letter - relative major/minor)
            if num1 == num2:
                return letter1 != letter2
            
            return False
            
        except (ValueError, IndexError):
            return False


class FilterCache:
    """LRU cache for filter results to improve performance."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, FilterResult] = {}
        self.access_order: List[str] = []
        self.lock = threading.Lock()
    
    def get(self, filter_hash: str) -> Optional[FilterResult]:
        """Get cached filter result."""
        with self.lock:
            if filter_hash in self.cache:
                # Update access order
                self.access_order.remove(filter_hash)
                self.access_order.append(filter_hash)
                
                result = self.cache[filter_hash]
                result.cache_hit = True
                return result
        return None
    
    def put(self, filter_hash: str, result: FilterResult):
        """Store filter result in cache."""
        with self.lock:
            # Remove oldest entries if cache is full
            while len(self.cache) >= self.max_size and self.access_order:
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[filter_hash] = result
            self.access_order.append(filter_hash)
            result.filter_hash = filter_hash
    
    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'utilization': len(self.cache) / self.max_size if self.max_size > 0 else 0
            }


class AsyncFilterEngine(QObject if QT_AVAILABLE else object):
    """High-performance asynchronous filtering engine for music libraries."""
    
    # Signals for Qt-based applications
    if QT_AVAILABLE:
        filter_started = Signal()
        filter_progress = Signal(int, str)
        partial_results_ready = Signal(dict)
        filter_completed = Signal(object)
        filter_error = Signal(str)
    
    def __init__(self, cache_size: int = 100, batch_size: int = 100):
        if QT_AVAILABLE:
            super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.cache = FilterCache(cache_size)
        self.batch_size = batch_size
        self.current_worker: Optional[AsyncFilterWorker] = None
        self.tracks_database: Dict[str, TrackData] = {}
        
        # Performance metrics
        self.filter_count = 0
        self.cache_hits = 0
        self.total_filter_time = 0.0
    
    def set_tracks_database(self, tracks_database: Dict[str, TrackData]):
        """Set the tracks database for filtering."""
        self.tracks_database = tracks_database
        self.cache.clear()  # Clear cache when database changes
        self.logger.info(f"Tracks database updated: {len(tracks_database)} tracks")
    
    def filter_async(self, filter_criteria: List[FilterCriteria]) -> bool:
        """Start asynchronous filtering operation."""
        if not self.tracks_database:
            self.logger.warning("No tracks database available for filtering")
            return False
        
        # Generate cache key
        filter_hash = self._generate_filter_hash(filter_criteria)
        
        # Check cache first
        cached_result = self.cache.get(filter_hash)
        if cached_result:
            self.logger.info(f"Filter cache hit: {filter_hash[:8]}...")
            self.cache_hits += 1
            if QT_AVAILABLE:
                self.filter_completed.emit(cached_result)
            return True
        
        # Cancel any running filter operation
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait(1000)  # Wait up to 1 second
        
        # Start new filter operation
        self.current_worker = AsyncFilterWorker(
            self.tracks_database,
            filter_criteria,
            self.batch_size
        )
        
        # Connect signals if Qt is available
        if QT_AVAILABLE:
            self.current_worker.progress_updated.connect(self.filter_progress.emit)
            self.current_worker.partial_results.connect(self.partial_results_ready.emit)
            self.current_worker.filtering_complete.connect(self._on_filter_complete)
            self.current_worker.error_occurred.connect(self.filter_error.emit)
        
        self.current_worker.start()
        
        self.filter_count += 1
        if QT_AVAILABLE:
            self.filter_started.emit()
        
        self.logger.info(f"Started async filter operation: {filter_hash[:8]}...")
        return True
    
    def filter_sync(self, filter_criteria: List[FilterCriteria]) -> FilterResult:
        """Synchronous filtering operation for immediate results."""
        start_time = time.time()
        
        # Check cache first
        filter_hash = self._generate_filter_hash(filter_criteria)
        cached_result = self.cache.get(filter_hash)
        if cached_result:
            self.cache_hits += 1
            return cached_result
        
        # Perform filtering
        matched_tracks = {}
        
        for file_path, track_data in self.tracks_database.items():
            if self._matches_criteria(track_data, filter_criteria):
                matched_tracks[file_path] = track_data
        
        processing_time = time.time() - start_time
        self.total_filter_time += processing_time
        
        result = FilterResult(
            matched_tracks=matched_tracks,
            total_matches=len(matched_tracks),
            processing_time=processing_time,
            filter_hash=filter_hash
        )
        
        # Cache the result
        self.cache.put(filter_hash, result)
        
        return result
    
    def cancel_filter(self):
        """Cancel any running filter operation."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.logger.info("Filter operation cancelled")
    
    def _on_filter_complete(self, result: FilterResult):
        """Handle completion of async filter operation."""
        # Cache the result
        if result.filter_hash:
            self.cache.put(result.filter_hash, result)
        
        self.total_filter_time += result.processing_time
        
        if QT_AVAILABLE:
            self.filter_completed.emit(result)
        
        self.logger.info(f"Filter completed: {result.total_matches} matches in {result.processing_time:.2f}s")
    
    def _generate_filter_hash(self, filter_criteria: List[FilterCriteria]) -> str:
        """Generate hash for filter criteria to use as cache key."""
        import hashlib
        
        criteria_str = ""
        for criterion in sorted(filter_criteria, key=lambda x: x.filter_type.value):
            criteria_str += f"{criterion.filter_type.value}:{criterion.operator}:{criterion.value}:{criterion.case_sensitive}|"
        
        return hashlib.md5(criteria_str.encode()).hexdigest()
    
    def _matches_criteria(self, track_data: TrackData, criteria: List[FilterCriteria]) -> bool:
        """Check if track matches all filter criteria (sync version)."""
        worker = AsyncFilterWorker({}, [])
        return worker._matches_criteria(track_data, criteria)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_stats = self.cache.get_stats()
        
        return {
            'total_filters': self.filter_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / self.filter_count if self.filter_count > 0 else 0,
            'total_filter_time': self.total_filter_time,
            'average_filter_time': self.total_filter_time / self.filter_count if self.filter_count > 0 else 0,
            'cache_stats': cache_stats
        }
    
    def clear_cache(self):
        """Clear the filter cache."""
        self.cache.clear()
        self.logger.info("Filter cache cleared")
