"""
DJ Playlist Generation Plugin for MusicFlow Organizer
====================================================
Integrates advanced playlist generation capabilities into MusicFlow.

Provides:
- Mixed In Key database enrichment
- Multi-source metadata enhancement
- Professional DJ playlist generation
- Harmonic mixing optimization

Author: Claude Code
Date: 2025-07-12
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from .plugin_manager import BasePlugin
from .dj_engine.enrichment import EnrichmentEngine, EnrichedTrackData
from .dj_engine.playlist_builder import PlaylistBuilder, PlaylistConfig
from .dj_engine.camelot_wheel import CamelotWheel
from .dj_engine.coherence_metrics import CoherenceMetrics

class DJPlaylistPlugin(BasePlugin):
    """
    Professional DJ playlist generation plugin.
    
    Extends MusicFlow Organizer with:
    - Track enrichment from multiple sources
    - Harmonic mixing with Camelot Wheel
    - Coherence-based playlist generation
    - Export in multiple formats
    """
    
    def __init__(self):
        super().__init__(name="DJPlaylistEngine", version="1.0.0")
        self.enrichment_engine = None
        self.playlist_builder = None
        self.camelot_wheel = CamelotWheel()
        self.config = {}
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the DJ playlist plugin.
        
        Args:
            config: Plugin configuration
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.config = config
            
            # Set up enrichment engine
            enrichment_config = {
                'db_path': config.get('enriched_db_path', 'musicflow_enriched.db'),
                'redis_url': config.get('redis_url'),
                'cache_ttl_days': config.get('cache_ttl_days', 7),
                'user_agent': config.get('user_agent', 'MusicFlowOrganizer/1.0'),
                
                # API keys
                'musicbrainz_user_agent': config.get('musicbrainz_user_agent'),
                'discogs_token': config.get('discogs_token'),
                'spotify_client_id': config.get('spotify_client_id'),
                'spotify_client_secret': config.get('spotify_client_secret'),
                'lastfm_api_key': config.get('lastfm_api_key'),
                'openai_api_key': config.get('openai_api_key'),
                'genius_access_token': config.get('genius_access_token'),
                
                # Weights
                'weight_discogs': config.get('weight_discogs', 0.30),
                'weight_cnn': config.get('weight_cnn', 0.25),
                'weight_gpt': config.get('weight_gpt', 0.25),
                'weight_spotify': config.get('weight_spotify', 0.15),
                'weight_lastfm': config.get('weight_lastfm', 0.05),
                
                # Performance
                'batch_size': config.get('batch_size', 10)
            }
            
            # Initialize playlist builder
            self.playlist_builder = PlaylistBuilder(
                enriched_db_path=enrichment_config['db_path'],
                config={
                    'w_bpm': config.get('w_bpm', 0.25),
                    'w_key': config.get('w_key', 0.30),
                    'w_valence': config.get('w_valence', 0.25),
                    'w_energy': config.get('w_energy', 0.20)
                }
            )
            
            # Store enrichment config for async initialization
            self.enrichment_config = enrichment_config
            
            self.logger.info("DJ Playlist Plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DJ Playlist Plugin: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Return plugin capabilities."""
        return [
            'track_enrichment',
            'playlist_generation',
            'harmonic_analysis',
            'coherence_scoring',
            'export_playlists',
            'camelot_wheel',
            'mixinkey_integration'
        ]
    
    async def enrich_tracks_from_mixinkey(self, mixinkey_tracks: Dict[str, Any],
                                         progress_callback=None) -> List[EnrichedTrackData]:
        """
        Enrich tracks from Mixed In Key database.
        
        Args:
            mixinkey_tracks: Dictionary of tracks from MixInKey
            progress_callback: Optional progress callback
            
        Returns:
            List[EnrichedTrackData]: Enriched tracks
        """
        if not self.enabled:
            self.logger.warning("Plugin not enabled")
            return []
        
        # Initialize enrichment engine
        async with EnrichmentEngine(self.enrichment_config) as engine:
            # Convert MixInKey tracks to format for enrichment
            tracks_to_enrich = []
            for track_id, track_data in mixinkey_tracks.items():
                tracks_to_enrich.append({
                    'track_id': track_id,
                    'title': track_data.name or track_data.title,
                    'artist': track_data.artist,
                    'bpm': track_data.tempo,
                    'camelot_key': track_data.key,
                    'energy': track_data.energy / 10.0 if track_data.energy else 0.5
                })
            
            # Enrich tracks in batches
            enriched_tracks = await engine.enrich_batch(
                tracks_to_enrich,
                progress_callback=progress_callback
            )
            
            return enriched_tracks
    
    def generate_playlist(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a professional DJ playlist.
        
        Args:
            config: Playlist generation configuration
            
        Returns:
            Dict[str, Any]: Generated playlist with metadata
        """
        if not self.enabled:
            return {'error': 'Plugin not enabled'}
        
        try:
            # Create playlist configuration
            playlist_config = PlaylistConfig(
                target_bpm=config.get('target_bpm'),
                target_length=config.get('target_length', 30),
                lambda_popularity=config.get('lambda_popularity', 0.4),
                max_bpm_delta=config.get('max_bpm_delta', 10.0),
                min_coherence_threshold=config.get('min_coherence_threshold', 0.6),
                energy_arc_type=config.get('energy_arc_type', 'progressive'),
                seed_track_id=config.get('seed_track_id'),
                genre_filter=config.get('genre_filter'),
                year_range=config.get('year_range'),
                exclude_tracks=set(config.get('exclude_tracks', []))
            )
            
            # Generate playlist
            playlist_tracks = self.playlist_builder.build_playlist(playlist_config)
            
            if not playlist_tracks:
                return {'error': 'Failed to generate playlist'}
            
            # Analyze playlist quality
            quality_analysis = self.playlist_builder.analyze_playlist_quality(playlist_tracks)
            
            # Export playlist in requested format
            export_format = config.get('export_format', 'json')
            exported_data = self.playlist_builder.export_playlist(
                playlist_tracks, 
                format=export_format
            )
            
            return {
                'success': True,
                'playlist_data': exported_data,
                'track_count': len(playlist_tracks),
                'quality_analysis': quality_analysis,
                'export_format': export_format
            }
            
        except Exception as e:
            self.logger.error(f"Error generating playlist: {e}")
            return {'error': str(e)}
    
    def get_camelot_compatibility(self, key1: str, key2: str) -> Dict[str, Any]:
        """
        Get Camelot Wheel compatibility between two keys.
        
        Args:
            key1: First Camelot key
            key2: Second Camelot key
            
        Returns:
            Dict[str, Any]: Compatibility information
        """
        score = self.camelot_wheel.get_compatibility_score(key1, key2)
        compatible_keys = self.camelot_wheel.get_compatible_keys(key1)
        
        return {
            'key1': key1,
            'key2': key2,
            'compatibility_score': score,
            'compatible_keys': compatible_keys[:10],  # Top 10
            'recommendation': self._get_compatibility_recommendation(score)
        }
    
    def _get_compatibility_recommendation(self, score: float) -> str:
        """Get human-readable compatibility recommendation."""
        if score >= 0.9:
            return "Perfect harmonic match"
        elif score >= 0.8:
            return "Excellent for mixing"
        elif score >= 0.6:
            return "Good compatibility"
        elif score >= 0.4:
            return "Moderate compatibility"
        elif score >= 0.2:
            return "Use with caution"
        else:
            return "Not recommended for mixing"
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics."""
        if not self.playlist_builder:
            return {'error': 'Plugin not initialized'}
        
        # Create temporary engine for stats
        engine = EnrichmentEngine(self.enrichment_config)
        stats = engine.get_enrichment_stats()
        
        return stats
    
    def scan_and_enrich_directory(self, directory_path: str, 
                                 use_mixinkey: bool = True) -> Dict[str, Any]:
        """
        Scan directory and enrich tracks (integration point with MusicFlow).
        
        Args:
            directory_path: Path to music directory
            use_mixinkey: Whether to use MixInKey data
            
        Returns:
            Dict[str, Any]: Scan and enrichment results
        """
        # This method would integrate with MusicFlow's existing scan functionality
        # For now, return a placeholder
        return {
            'status': 'This method integrates with MusicFlow scanning',
            'directory': directory_path,
            'use_mixinkey': use_mixinkey
        }
    
    def export_camelot_wheel_html(self) -> str:
        """Export interactive Camelot Wheel visualization."""
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Camelot Wheel - MusicFlow DJ Engine</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
        .wheel-container { width: 800px; margin: 50px auto; text-align: center; }
        .wheel { position: relative; width: 600px; height: 600px; margin: 0 auto; }
        .key-segment { position: absolute; cursor: pointer; transition: all 0.3s; }
        .key-segment:hover { transform: scale(1.1); filter: brightness(1.2); }
        .compatibility-info { margin-top: 30px; padding: 20px; background: #2a2a2a; border-radius: 10px; }
        h1 { color: #4a9eff; }
    </style>
</head>
<body>
    <div class="wheel-container">
        <h1>Camelot Wheel - Professional DJ Harmonic Mixing</h1>
        <div class="wheel" id="camelotWheel">
            <!-- Wheel segments would be generated here -->
        </div>
        <div class="compatibility-info">
            <h3>Click on keys to see compatibility</h3>
            <div id="compatibilityDisplay"></div>
        </div>
    </div>
    <script>
        const camelotData = {camelot_json};
        // Interactive JavaScript would go here
    </script>
</body>
</html>
        '''
        
        # Generate Camelot data
        camelot_json = json.dumps({
            key: {
                'position': data['position'],
                'mode': data['mode'],
                'musical_key': data['key']
            }
            for key, data in self.camelot_wheel.camelot_keys.items()
        })
        
        return html_template.replace('{camelot_json}', camelot_json)