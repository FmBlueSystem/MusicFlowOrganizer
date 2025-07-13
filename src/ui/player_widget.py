"""
Audio Player Widget for MusicFlow Organizer
============================================

Professional audio player widget with visual controls for track preview
during music library organization.
"""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
    QSlider, QFrame, QSizePolicy, QToolButton, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

# Import audio player
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from audio.preview_player import PreviewPlayer, PlaybackState


class PlayerWidget(QWidget):
    """
    Professional audio player widget with visual controls.
    
    Provides play/pause, seek, volume controls and track information
    for previewing music during organization.
    """
    
    # Signals
    track_requested = Signal(str)  # Request to load specific track
    
    def __init__(self):
        """Initialize the player widget."""
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize audio player
        self.player = PreviewPlayer()
        
        # State
        self.is_seeking = False
        self.auto_preview = True
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.setup_styles()
        
        # Update initial state
        self.update_ui_state()
        
        self.logger.info("Player widget initialized")
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)
        
        # Track info section
        self.create_track_info_section(main_layout)
        
        # Controls section
        self.create_controls_section(main_layout)
        
        # Progress section
        self.create_progress_section(main_layout)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
    
    def create_track_info_section(self, parent_layout):
        """Create track information display section."""
        info_layout = QHBoxLayout()
        
        # Track title and artist
        self.track_label = QLabel("No track loaded")
        self.track_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.track_label.setStyleSheet("color: #2c3e50;")
        
        # Duration info
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setStyleSheet("color: #7f8c8d;")
        self.time_label.setMinimumWidth(80)
        
        info_layout.addWidget(self.track_label, 1)
        info_layout.addWidget(self.time_label)
        
        parent_layout.addLayout(info_layout)
    
    def create_controls_section(self, parent_layout):
        """Create playback controls section."""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Quick preview buttons
        self.intro_btn = self.create_control_button("Intro", "Preview intro (5%)")
        self.drop_btn = self.create_control_button("Drop", "Preview drop (30%)")
        self.outro_btn = self.create_control_button("Outro", "Preview outro (90%)")
        
        # Main playback controls
        self.play_pause_btn = self.create_control_button("▶", "Play/Pause (Space)")
        self.stop_btn = self.create_control_button("⏹", "Stop")
        
        # Volume control
        self.volume_label = QLabel("Vol:")
        self.volume_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(80)
        self.volume_slider.setToolTip("Volume control")
        
        # Add widgets to layout
        controls_layout.addWidget(self.intro_btn)
        controls_layout.addWidget(self.drop_btn)
        controls_layout.addWidget(self.outro_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #bdc3c7;")
        controls_layout.addWidget(separator)
        
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.stop_btn)
        
        # Spacer
        controls_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        controls_layout.addWidget(self.volume_label)
        controls_layout.addWidget(self.volume_slider)
        
        parent_layout.addLayout(controls_layout)
    
    def create_progress_section(self, parent_layout):
        """Create progress/seek section."""
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.setValue(0)
        self.position_slider.setToolTip("Click to seek to position")
        
        progress_layout.addWidget(self.position_slider)
        
        parent_layout.addLayout(progress_layout)
    
    def create_control_button(self, text: str, tooltip: str = "") -> QPushButton:
        """Create a styled control button."""
        button = QPushButton(text)
        button.setMinimumWidth(50)
        button.setMaximumWidth(70)
        button.setMinimumHeight(28)
        if tooltip:
            button.setToolTip(tooltip)
        return button
    
    def setup_connections(self):
        """Set up signal connections."""
        # Player signals
        self.player.playback_state_changed.connect(self.on_playback_state_changed)
        self.player.position_changed.connect(self.on_position_changed)
        self.player.duration_changed.connect(self.on_duration_changed)
        self.player.volume_changed.connect(self.on_volume_changed)
        self.player.track_changed.connect(self.on_track_changed)
        self.player.error_occurred.connect(self.on_error)
        
        # UI controls
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        self.stop_btn.clicked.connect(self.stop)
        self.intro_btn.clicked.connect(self.preview_intro)
        self.drop_btn.clicked.connect(self.preview_drop)
        self.outro_btn.clicked.connect(self.preview_outro)
        
        self.volume_slider.valueChanged.connect(self.on_volume_slider_changed)
        self.position_slider.sliderPressed.connect(self.on_seek_start)
        self.position_slider.sliderReleased.connect(self.on_seek_end)
        self.position_slider.valueChanged.connect(self.on_seek_changed)
    
    def setup_styles(self):
        """Set up widget styles."""
        self.setStyleSheet("""
            PlayerWidget {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
            
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 3px;
            }
        """)
    
    def load_track(self, file_path: str) -> bool:
        """
        Load a track for preview.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if loaded successfully
        """
        return self.player.load_track(file_path)
    
    def play(self) -> bool:
        """Start playback."""
        return self.player.play()
    
    def pause(self) -> bool:
        """Pause playback."""
        return self.player.pause()
    
    def stop(self) -> bool:
        """Stop playback."""
        return self.player.stop()
    
    def toggle_playback(self) -> bool:
        """Toggle play/pause."""
        return self.player.toggle_playback()
    
    def preview_intro(self) -> bool:
        """Preview track intro."""
        return self.player.preview_intro()
    
    def preview_drop(self) -> bool:
        """Preview track drop."""
        return self.player.preview_drop()
    
    def preview_outro(self) -> bool:
        """Preview track outro."""
        return self.player.preview_outro()
    
    def set_auto_preview(self, enabled: bool):
        """Enable/disable auto-preview when track is loaded."""
        self.auto_preview = enabled
    
    # Slot methods
    def on_playback_state_changed(self, state: str):
        """Handle playback state changes."""
        self.update_play_button(state)
        self.update_controls_enabled(state)
    
    def on_position_changed(self, position_ms: int):
        """Handle position changes."""
        if not self.is_seeking and self.player.duration > 0:
            # Update position slider
            percent = (position_ms / self.player.duration) * 100
            self.position_slider.setValue(int(percent))
        
        # Update time display
        self.update_time_display(position_ms, self.player.duration)
    
    def on_duration_changed(self, duration_ms: int):
        """Handle duration changes."""
        self.update_time_display(self.player.position, duration_ms)
        
        # Enable controls if we have a valid duration
        if duration_ms > 0:
            self.enable_preview_controls(True)
            
            # Auto-preview if enabled
            if self.auto_preview and self.player.state == PlaybackState.LOADING:
                QTimer.singleShot(100, self.play)  # Small delay to ensure loading is complete
    
    def on_volume_changed(self, volume: float):
        """Handle volume changes."""
        # Update volume slider without triggering signal
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(int(volume * 100))
        self.volume_slider.blockSignals(False)
    
    def on_track_changed(self, file_path: str):
        """Handle track changes."""
        self.update_track_display(file_path)
    
    def on_error(self, error_message: str):
        """Handle player errors."""
        self.track_label.setText(f"Error: {error_message}")
        self.track_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.enable_controls(False)
    
    def on_volume_slider_changed(self, value: int):
        """Handle volume slider changes."""
        volume = value / 100.0
        self.player.set_volume(volume)
    
    def on_seek_start(self):
        """Handle seek start."""
        self.is_seeking = True
    
    def on_seek_end(self):
        """Handle seek end."""
        self.is_seeking = False
        
        # Seek to new position
        if self.player.duration > 0:
            percent = self.position_slider.value() / 100.0
            position_ms = int(self.player.duration * percent)
            self.player.seek(position_ms)
    
    def on_seek_changed(self, value: int):
        """Handle seek slider changes during dragging."""
        if self.is_seeking and self.player.duration > 0:
            # Update time display while dragging
            percent = value / 100.0
            position_ms = int(self.player.duration * percent)
            self.update_time_display(position_ms, self.player.duration)
    
    # UI Update methods
    def update_play_button(self, state: str):
        """Update play/pause button appearance."""
        if state == PlaybackState.PLAYING.value:
            self.play_pause_btn.setText("⏸")
            self.play_pause_btn.setToolTip("Pause (Space)")
        else:
            self.play_pause_btn.setText("▶")
            self.play_pause_btn.setToolTip("Play (Space)")
    
    def update_controls_enabled(self, state: str):
        """Update controls enabled state."""
        has_track = self.player.current_track is not None
        is_error = state == PlaybackState.ERROR.value
        
        self.enable_controls(has_track and not is_error)
    
    def update_track_display(self, file_path: str):
        """Update track information display."""
        if file_path:
            # Get track info including cached metadata
            track_info = self.player.get_track_info()
            
            # Build display text
            if track_info.get('artist') and track_info.get('title'):
                display_text = f"{track_info['artist']} - {track_info['title']}"
            elif track_info.get('title'):
                display_text = track_info['title']
            else:
                display_text = Path(file_path).stem
            
            # Add cache indicator
            if track_info.get('cached'):
                display_text += " 💾"  # Cache indicator
            
            self.track_label.setText(display_text)
            self.track_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        else:
            self.track_label.setText("No track loaded")
            self.track_label.setStyleSheet("color: #7f8c8d;")
    
    def update_time_display(self, position_ms: int, duration_ms: int):
        """Update time display."""
        position_str = self._format_time(position_ms)
        duration_str = self._format_time(duration_ms)
        self.time_label.setText(f"{position_str} / {duration_str}")
    
    def enable_controls(self, enabled: bool):
        """Enable/disable all controls."""
        self.play_pause_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(enabled)
        self.position_slider.setEnabled(enabled)
        self.enable_preview_controls(enabled)
    
    def enable_preview_controls(self, enabled: bool):
        """Enable/disable preview controls."""
        self.intro_btn.setEnabled(enabled)
        self.drop_btn.setEnabled(enabled)
        self.outro_btn.setEnabled(enabled)
    
    def update_ui_state(self):
        """Update UI based on current player state."""
        has_player = self.player.is_available
        
        if not has_player:
            self.track_label.setText("Audio preview not available")
            self.track_label.setStyleSheet("color: #e74c3c;")
            self.enable_controls(False)
        else:
            self.enable_controls(False)  # Will be enabled when track loads
    
    def _format_time(self, ms: int) -> str:
        """Format time in milliseconds to MM:SS."""
        if ms <= 0:
            return "00:00"
        
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes:02d}:{seconds:02d}"
    
    # Keyboard shortcuts support
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Space:
            self.toggle_playback()
            event.accept()
        elif event.key() == Qt.Key_S:
            self.stop()
            event.accept()
        elif event.key() == Qt.Key_1:
            self.preview_intro()
            event.accept()
        elif event.key() == Qt.Key_2:
            self.preview_drop()
            event.accept()
        elif event.key() == Qt.Key_3:
            self.preview_outro()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def get_player_info(self) -> dict:
        """Get current player information."""
        return self.player.get_track_info()