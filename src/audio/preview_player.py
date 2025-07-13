"""
Audio Preview Player for MusicFlow Organizer
=============================================

Professional audio preview functionality for track validation during organization.
Supports multiple audio formats and provides essential playback controls.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

# Import cache system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from audio.audio_cache import AudioCache

try:
    from PySide6.QtCore import QObject, Signal, QUrl, QTimer
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    AUDIO_AVAILABLE = True
except ImportError:
    logging.warning("PySide6 QtMultimedia not available - audio preview disabled")
    AUDIO_AVAILABLE = False
    
    # Create stub classes for type hints
    class QObject:
        pass
    class Signal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass
        def connect(self, func):
            pass


class PlaybackState(Enum):
    """Audio playback states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    ERROR = "error"


class PreviewPlayer(QObject):
    """
    Professional audio preview player for music organization.
    
    Provides essential playback functionality for track validation
    during the organization process.
    """
    
    # Signals for UI updates
    playback_state_changed = Signal(str)  # PlaybackState value
    position_changed = Signal(int)        # Position in milliseconds
    duration_changed = Signal(int)        # Duration in milliseconds
    volume_changed = Signal(float)        # Volume 0.0 to 1.0
    track_changed = Signal(str)           # Current track path
    error_occurred = Signal(str)          # Error message
    
    # Supported audio formats
    SUPPORTED_FORMATS = {
        '.mp3', '.flac', '.wav', '.m4a', '.aac', 
        '.ogg', '.wma', '.aiff', '.opus'
    }
    
    def __init__(self):
        """Initialize the preview player."""
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize audio cache
        self.audio_cache = AudioCache()
        
        if not AUDIO_AVAILABLE:
            self.logger.error("Audio functionality not available")
            self.media_player = None
            self.audio_output = None
            self._state = PlaybackState.ERROR
            return
        
        # Initialize media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Player state
        self._state = PlaybackState.STOPPED
        self._current_track = None
        self._volume = 0.7  # Default volume
        self._duration = 0
        self._position = 0
        
        # Position update timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.setInterval(100)  # Update every 100ms
        
        # Connect media player signals
        self._setup_connections()
        
        # Set initial volume
        self.set_volume(self._volume)
        
        self.logger.info("Preview player initialized successfully")
    
    def _setup_connections(self):
        """Set up media player signal connections."""
        if not self.media_player:
            return
        
        self.media_player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.media_player.errorOccurred.connect(self._on_error)
        self.audio_output.volumeChanged.connect(self._on_volume_changed)
    
    def load_track(self, file_path: str) -> bool:
        """
        Load an audio track for preview.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if track loaded successfully
        """
        if not self.media_player:
            self.logger.error("Media player not available")
            return False
        
        try:
            # Validate file
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"Audio file not found: {file_path}")
                self.error_occurred.emit(f"File not found: {path.name}")
                return False
            
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                self.logger.warning(f"Unsupported audio format: {path.suffix}")
                self.error_occurred.emit(f"Unsupported format: {path.suffix}")
                return False
            
            # Stop current playback
            self.stop()
            
            # Load new track
            self._current_track = file_path
            file_url = QUrl.fromLocalFile(file_path)
            self.media_player.setSource(file_url)
            
            self._set_state(PlaybackState.LOADING)
            self.track_changed.emit(file_path)
            
            self.logger.debug(f"Loading track: {path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load track {file_path}: {e}")
            self.error_occurred.emit(f"Load error: {str(e)}")
            return False
    
    def play(self) -> bool:
        """
        Start playback.
        
        Returns:
            True if playback started successfully
        """
        if not self.media_player or not self._current_track:
            return False
        
        try:
            self.media_player.play()
            self.position_timer.start()
            return True
        except Exception as e:
            self.logger.error(f"Playback error: {e}")
            self.error_occurred.emit(f"Playback error: {str(e)}")
            return False
    
    def pause(self) -> bool:
        """
        Pause playback.
        
        Returns:
            True if paused successfully
        """
        if not self.media_player:
            return False
        
        try:
            self.media_player.pause()
            self.position_timer.stop()
            return True
        except Exception as e:
            self.logger.error(f"Pause error: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop playback.
        
        Returns:
            True if stopped successfully
        """
        if not self.media_player:
            return False
        
        try:
            self.media_player.stop()
            self.position_timer.stop()
            self._position = 0
            self.position_changed.emit(0)
            return True
        except Exception as e:
            self.logger.error(f"Stop error: {e}")
            return False
    
    def seek(self, position_ms: int) -> bool:
        """
        Seek to position in track.
        
        Args:
            position_ms: Position in milliseconds
            
        Returns:
            True if seek successful
        """
        if not self.media_player or self._duration == 0:
            return False
        
        try:
            # Clamp position to valid range
            position_ms = max(0, min(position_ms, self._duration))
            self.media_player.setPosition(position_ms)
            self._position = position_ms
            self.position_changed.emit(position_ms)
            return True
        except Exception as e:
            self.logger.error(f"Seek error: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """
        Set playback volume.
        
        Args:
            volume: Volume level 0.0 to 1.0
            
        Returns:
            True if volume set successfully
        """
        if not self.audio_output:
            return False
        
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))
            self.audio_output.setVolume(volume)
            self._volume = volume
            return True
        except Exception as e:
            self.logger.error(f"Volume error: {e}")
            return False
    
    def quick_preview(self, position_percent: float = 0.3) -> bool:
        """
        Quick preview at specific position (useful for checking drops, etc.).
        
        Args:
            position_percent: Position as percentage of track (0.0 to 1.0)
            
        Returns:
            True if preview started successfully
        """
        if self._duration == 0:
            return False
        
        position_ms = int(self._duration * position_percent)
        if self.seek(position_ms):
            return self.play()
        return False
    
    def preview_intro(self) -> bool:
        """Preview track intro (first 10%)."""
        return self.quick_preview(0.05)
    
    def preview_drop(self) -> bool:
        """Preview track drop/main section (around 30%)."""
        return self.quick_preview(0.3)
    
    def preview_outro(self) -> bool:
        """Preview track outro (last 10%)."""
        return self.quick_preview(0.9)
    
    def toggle_playback(self) -> bool:
        """
        Toggle between play and pause.
        
        Returns:
            True if operation successful
        """
        if self._state == PlaybackState.PLAYING:
            return self.pause()
        elif self._state in (PlaybackState.PAUSED, PlaybackState.STOPPED):
            return self.play()
        return False
    
    # Properties
    @property
    def state(self) -> PlaybackState:
        """Current playback state."""
        return self._state
    
    @property
    def current_track(self) -> Optional[str]:
        """Currently loaded track path."""
        return self._current_track
    
    @property
    def volume(self) -> float:
        """Current volume level."""
        return self._volume
    
    @property
    def position(self) -> int:
        """Current position in milliseconds."""
        return self._position
    
    @property
    def duration(self) -> int:
        """Track duration in milliseconds."""
        return self._duration
    
    @property
    def position_percent(self) -> float:
        """Current position as percentage (0.0 to 1.0)."""
        if self._duration == 0:
            return 0.0
        return self._position / self._duration
    
    @property
    def is_available(self) -> bool:
        """Check if audio functionality is available."""
        return AUDIO_AVAILABLE and self.media_player is not None
    
    # Private methods
    def _set_state(self, state: PlaybackState):
        """Update internal state and emit signal."""
        if self._state != state:
            self._state = state
            self.playback_state_changed.emit(state.value)
    
    def _update_position(self):
        """Update position from media player."""
        if self.media_player:
            current_pos = self.media_player.position()
            if current_pos != self._position:
                self._position = current_pos
                self.position_changed.emit(current_pos)
    
    def _on_playback_state_changed(self, state):
        """Handle media player state changes."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._set_state(PlaybackState.PLAYING)
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self._set_state(PlaybackState.PAUSED)
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self._set_state(PlaybackState.STOPPED)
    
    def _on_duration_changed(self, duration):
        """Handle duration change."""
        self._duration = duration
        self.duration_changed.emit(duration)
    
    def _on_volume_changed(self, volume):
        """Handle volume change."""
        self._volume = volume
        self.volume_changed.emit(volume)
    
    def _on_error(self, error):
        """Handle media player errors."""
        error_msg = f"Media player error: {error}"
        self.logger.error(error_msg)
        self._set_state(PlaybackState.ERROR)
        self.error_occurred.emit(error_msg)
    
    def get_track_info(self) -> Dict[str, Any]:
        """
        Get information about current track.
        
        Returns:
            Dictionary with track information
        """
        if not self._current_track:
            return {}
        
        path = Path(self._current_track)
        
        # Base info
        info = {
            'file_path': self._current_track,
            'filename': path.name,
            'format': path.suffix.lower(),
            'duration_ms': self._duration,
            'duration_str': self._format_duration(self._duration),
            'state': self._state.value,
            'position_ms': self._position,
            'position_str': self._format_duration(self._position),
            'volume': self._volume
        }
        
        # Add cached metadata if available
        cached_data = self.audio_cache.get_track_data(self._current_track)
        if cached_data:
            info.update({
                'title': cached_data.title,
                'artist': cached_data.artist,
                'album': cached_data.album,
                'genre': cached_data.genre,
                'bitrate': cached_data.bitrate,
                'cached': True
            })
        else:
            info['cached'] = False
        
        return info
    
    def _format_duration(self, duration_ms: int) -> str:
        """Format duration in milliseconds to MM:SS format."""
        if duration_ms <= 0:
            return "00:00"
        
        total_seconds = duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        return f"{minutes:02d}:{seconds:02d}"