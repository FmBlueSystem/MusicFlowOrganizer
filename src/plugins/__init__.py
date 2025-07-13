"""
MusicFlow Organizer Plugin System
=================================
Modular plugin architecture for extending MusicFlow functionality.
"""

__version__ = "1.0.0"
__all__ = ["DJPlaylistPlugin", "PluginManager"]

from .plugin_manager import PluginManager
from .dj_playlist_plugin import DJPlaylistPlugin