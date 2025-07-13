"""
Performance Manager for MusicFlow Organizer
============================================

Parallel processing and performance optimization for large music libraries.
Provides thread pool management, progress tracking, and efficient batch processing.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from threading import Lock
import multiprocessing
from dataclasses import dataclass
from queue import Queue

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.audio_analyzer import AudioAnalyzer, AudioAnalysisResult
from core.genre_classifier import GenreClassifier, GenreClassificationResult
from core.mixinkey_integration import MixInKeyIntegration, MixInKeyTrackData
from audio.audio_cache import AudioCache


@dataclass
class ProcessingTask:
    """Individual processing task."""
    file_path: str
    task_id: int
    priority: int = 0  # Higher number = higher priority


@dataclass
class ProcessingResult:
    """Result of a processing task."""
    task_id: int
    file_path: str
    success: bool
    error_message: Optional[str] = None
    mixinkey_data: Optional[MixInKeyTrackData] = None
    genre_result: Optional[GenreClassificationResult] = None
    analysis_result: Optional[AudioAnalysisResult] = None
    processing_time: float = 0.0


class PerformanceManager:
    """
    High-performance music library processing manager.
    
    Handles parallel analysis, progress tracking, and optimization
    for large music collections.
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_cache: bool = True, mixinkey_integration=None):
        """
        Initialize performance manager.
        
        Args:
            max_workers: Maximum number of worker threads (None = auto-detect)
            use_cache: Whether to use audio cache for optimization
            mixinkey_integration: Pre-configured MixInKeyIntegration instance
        """
        self.logger = logging.getLogger(__name__)
        
        # Determine optimal number of workers
        if max_workers is None:
            # Use 75% of available CPU cores, minimum 2, maximum 8
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = max(2, min(8, int(cpu_count * 0.75)))
        else:
            self.max_workers = max_workers
        
        # Thread pool
        self.executor: Optional[ThreadPoolExecutor] = None
        
        # Processing components
        self.audio_analyzer = AudioAnalyzer() if self.max_workers <= 4 else None
        self.genre_classifier = GenreClassifier()
        self.mixinkey_integration = mixinkey_integration or MixInKeyIntegration()
        
        # Cache system
        self.use_cache = use_cache
        self.audio_cache = AudioCache() if use_cache else None
        
        # Processing state
        self.is_processing = False
        self.current_tasks: Dict[int, Future] = {}
        self.completed_tasks: List[ProcessingResult] = []
        self.failed_tasks: List[ProcessingResult] = []
        self.task_counter = 0
        
        # Progress tracking
        self.total_tasks = 0
        self.completed_count = 0
        self.failed_count = 0
        self.start_time = 0.0
        
        # MixIn Key database cache
        self.mixinkey_tracks_cache = {}
        
        # Thread safety
        self.progress_lock = Lock()
        
        self.logger.info(f"Performance manager initialized with {self.max_workers} workers")
    
    def process_library(self, file_paths: List[str], 
                       progress_callback: Optional[Callable] = None,
                       use_mixinkey: bool = True) -> Dict[str, Any]:
        """
        Process music library with parallel analysis.
        
        Args:
            file_paths: List of audio file paths to process
            progress_callback: Callback function for progress updates
            use_mixinkey: Whether to use MixIn Key integration
            
        Returns:
            Dictionary with processing results
        """
        self.logger.info(f"Starting parallel processing of {len(file_paths)} files")
        
        # Initialize processing state
        self._reset_processing_state()
        self.total_tasks = len(file_paths)
        self.start_time = time.time()
        self.is_processing = True
        
        # Load MixIn Key database once at the start if using it
        if use_mixinkey and self.mixinkey_integration.database_path:
            self.logger.info("Loading MixIn Key database once for all files...")
            # Call progress callback if available
            if progress_callback:
                progress_callback(5, len(file_paths), None)
            self.mixinkey_tracks_cache = self.mixinkey_integration.scan_mixinkey_database("/dummy/path")
            self.logger.info(f"Loaded {len(self.mixinkey_tracks_cache)} tracks from MixIn Key database")
        else:
            self.mixinkey_tracks_cache = {}
        
        # Create tasks
        tasks = [
            ProcessingTask(file_path=path, task_id=i)
            for i, path in enumerate(file_paths)
        ]
        
        # Start thread pool
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        try:
            # Submit all tasks
            for task in tasks:
                future = self.executor.submit(
                    self._process_single_file, 
                    task, 
                    use_mixinkey
                )
                self.current_tasks[task.task_id] = future
            
            # Process results as they complete
            results = {}
            for future in as_completed(self.current_tasks.values()):
                try:
                    result = future.result()
                    self._handle_task_result(result, results)
                    
                    # Call progress callback
                    if progress_callback:
                        progress_callback(
                            self.completed_count + self.failed_count,
                            self.total_tasks,
                            result
                        )
                        
                except Exception as e:
                    self.logger.error(f"Task processing error: {e}")
                    with self.progress_lock:
                        self.failed_count += 1
            
            # Calculate final statistics
            total_time = time.time() - self.start_time
            
            return {
                'success': True,
                'tracks_database': results,
                'total_files': len(file_paths),
                'processed_files': self.completed_count,
                'failed_files': self.failed_count,
                'processing_time': total_time,
                'files_per_second': len(file_paths) / total_time if total_time > 0 else 0,
                'cache_hits': self._get_cache_hits(),
                'mixinkey_analyzed': self._count_mixinkey_analyzed(results)
            }
            
        except Exception as e:
            self.logger.error(f"Library processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tracks_database': {},
                'total_files': len(file_paths),
                'processed_files': self.completed_count,
                'failed_files': self.failed_count
            }
        
        finally:
            self._cleanup_processing()
    
    def cancel_processing(self) -> bool:
        """
        Cancel ongoing processing.
        
        Returns:
            True if cancellation was successful
        """
        if not self.is_processing or not self.executor:
            return False
        
        try:
            # Cancel all pending tasks
            for future in self.current_tasks.values():
                future.cancel()
            
            # Shutdown executor
            self.executor.shutdown(wait=False)
            self.is_processing = False
            
            self.logger.info("Processing cancelled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel processing: {e}")
            return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        with self.progress_lock:
            if self.start_time > 0:
                elapsed_time = time.time() - self.start_time
                rate = (self.completed_count + self.failed_count) / elapsed_time if elapsed_time > 0 else 0
            else:
                elapsed_time = 0
                rate = 0
            
            return {
                'is_processing': self.is_processing,
                'total_tasks': self.total_tasks,
                'completed_count': self.completed_count,
                'failed_count': self.failed_count,
                'remaining_count': self.total_tasks - self.completed_count - self.failed_count,
                'progress_percent': ((self.completed_count + self.failed_count) / self.total_tasks * 100) if self.total_tasks > 0 else 0,
                'elapsed_time': elapsed_time,
                'processing_rate': rate,
                'estimated_remaining': (self.total_tasks - self.completed_count - self.failed_count) / rate if rate > 0 else 0
            }
    
    def _process_single_file(self, task: ProcessingTask, use_mixinkey: bool) -> ProcessingResult:
        """
        Process a single audio file.
        
        Args:
            task: Processing task
            use_mixinkey: Whether to use MixIn Key integration
            
        Returns:
            ProcessingResult with analysis data
        """
        start_time = time.time()
        file_path = task.file_path
        
        try:
            # Check cache first
            cached_data = None
            if self.use_cache and self.audio_cache:
                cached_data = self.audio_cache.get_track_data(file_path)
            
            # Initialize result
            result = ProcessingResult(
                task_id=task.task_id,
                file_path=file_path,
                success=False
            )
            
            # Get MixIn Key data
            mixinkey_data = None
            if use_mixinkey:
                if cached_data and cached_data.bpm and cached_data.key:
                    # Use cached MixIn Key data
                    mixinkey_data = MixInKeyTrackData(
                        file_path=file_path,
                        filename=Path(file_path).name,
                        artist=cached_data.artist or "",
                        title=cached_data.title or "",
                        album=cached_data.album or "",
                        genre=cached_data.genre or "",
                        bpm=cached_data.bpm,
                        key=cached_data.key,
                        energy=cached_data.energy,
                        duration=cached_data.duration,
                        analyzed_by_mixinkey=True
                    )
                else:
                    # Try to get from pre-loaded MixIn Key database cache
                    mixinkey_data = self.mixinkey_tracks_cache.get(file_path)
                    
                    # If not found in cache and cache is empty, try to match by filename
                    if not mixinkey_data and self.mixinkey_tracks_cache:
                        filename = Path(file_path).name
                        for cached_path, cached_track in self.mixinkey_tracks_cache.items():
                            if cached_track.filename == filename:
                                # Found a match by filename, update the file path
                                mixinkey_data = cached_track
                                mixinkey_data.file_path = file_path
                                break
            
            # Perform audio analysis if needed
            analysis_result = None
            if not mixinkey_data and self.audio_analyzer:
                analysis_result = self.audio_analyzer.analyze_file(file_path)
                if analysis_result.success:
                    # Convert to MixIn Key format
                    mixinkey_data = MixInKeyTrackData(
                        file_path=file_path,
                        filename=Path(file_path).name,
                        bpm=analysis_result.bpm,
                        key=analysis_result.key,
                        energy=int(analysis_result.energy_level * 10) if analysis_result.energy_level else None,
                        duration=analysis_result.duration,
                        analyzed_by_mixinkey=False
                    )
            
            # Genre classification
            genre_result = None
            if mixinkey_data:
                # Create analysis result for genre classifier
                if not analysis_result:
                    analysis_result = AudioAnalysisResult(
                        file_path=file_path,
                        duration=mixinkey_data.duration or 0,
                        sample_rate=44100,
                        bpm=mixinkey_data.bpm,
                        key=mixinkey_data.key,
                        energy_level=mixinkey_data.energy / 10 if mixinkey_data.energy and isinstance(mixinkey_data.energy, (int, float)) else None
                    )
                
                genre_result = self.genre_classifier.classify_genre(analysis_result)
            
            # Cache the results
            if self.use_cache and self.audio_cache and mixinkey_data:
                cache_data = {
                    'title': mixinkey_data.title,
                    'artist': mixinkey_data.artist,
                    'album': mixinkey_data.album,
                    'genre': mixinkey_data.genre or (genre_result.primary_genre if genre_result else None),
                    'duration': mixinkey_data.duration,
                    'bpm': mixinkey_data.bpm,
                    'key': mixinkey_data.key,
                    'energy': mixinkey_data.energy
                }
                self.audio_cache.cache_track_data(file_path, **cache_data)
            
            # Build successful result
            result.success = True
            result.mixinkey_data = mixinkey_data
            result.genre_result = genre_result
            result.analysis_result = analysis_result
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            # Build error result
            error_msg = f"Processing failed: {str(e)}"
            self.logger.warning(f"Failed to process {file_path}: {error_msg}")
            
            return ProcessingResult(
                task_id=task.task_id,
                file_path=file_path,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
    
    def _handle_task_result(self, result: ProcessingResult, results: Dict[str, Any]):
        """Handle completed task result."""
        with self.progress_lock:
            if result.success:
                self.completed_count += 1
                self.completed_tasks.append(result)
                
                # Add to results database
                if result.mixinkey_data:
                    results[result.file_path] = {
                        'mixinkey_data': result.mixinkey_data,
                        'genre_classification': result.genre_result,
                        'analysis_result': result.analysis_result
                    }
            else:
                self.failed_count += 1
                self.failed_tasks.append(result)
    
    def _reset_processing_state(self):
        """Reset processing state for new operation."""
        self.current_tasks.clear()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.task_counter = 0
        self.total_tasks = 0
        self.completed_count = 0
        self.failed_count = 0
        self.start_time = 0.0
        # Note: Don't clear mixinkey_tracks_cache here as it might be reused
    
    def _cleanup_processing(self):
        """Clean up after processing."""
        self.is_processing = False
        
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        
        self.current_tasks.clear()
    
    def _get_cache_hits(self) -> int:
        """Get number of cache hits during processing."""
        if not self.use_cache or not self.audio_cache:
            return 0
        
        # This is an approximation - in a real implementation,
        # you'd track cache hits during processing
        return len([t for t in self.completed_tasks if t.processing_time < 0.1])
    
    def _count_mixinkey_analyzed(self, results: Dict[str, Any]) -> int:
        """Count tracks analyzed by MixIn Key."""
        return len([
            track_data for track_data in results.values()
            if track_data['mixinkey_data'] and track_data['mixinkey_data'].analyzed_by_mixinkey
        ])
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        # Check cache usage
        if not self.use_cache:
            recommendations.append("Enable audio cache for faster repeated analysis")
        
        # Check worker count
        cpu_count = multiprocessing.cpu_count()
        if self.max_workers < cpu_count // 2:
            recommendations.append(f"Consider increasing worker count (current: {self.max_workers}, CPU cores: {cpu_count})")
        
        # Check failure rate
        if self.failed_count > 0 and self.total_tasks > 0:
            failure_rate = self.failed_count / self.total_tasks
            if failure_rate > 0.1:
                recommendations.append(f"High failure rate ({failure_rate:.1%}) - check file formats and permissions")
        
        # Check processing rate
        stats = self.get_processing_stats()
        if stats['processing_rate'] < 1.0:
            recommendations.append("Consider using SSD storage for better I/O performance")
        
        return recommendations