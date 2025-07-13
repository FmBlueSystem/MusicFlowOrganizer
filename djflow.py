#!/usr/bin/env python3
"""
DJFlow - Professional DJ Playlist Generation CLI
===============================================
Command-line interface for the MusicFlow DJ Engine.

Features:
- Scan Mixed In Key database
- Enrich tracks with multi-source metadata
- Generate professional DJ playlists
- Export in multiple formats

Author: Claude Code
Date: 2025-07-12
"""

import argparse
import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.mixinkey_integration import MixInKeyIntegration
from plugins.plugin_manager import plugin_manager
from plugins.dj_playlist_plugin import DJPlaylistPlugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DJFlow')

class DJFlowCLI:
    """Command-line interface for DJ playlist generation."""
    
    def __init__(self):
        self.plugin = None
        self.mixinkey = None
        
    def initialize(self):
        """Initialize the DJ engine with configuration."""
        # Load environment variables
        load_dotenv()
        
        # Initialize plugin configuration
        config = {
            'enriched_db_path': os.getenv('MUSICFLOW_DB_PATH', 'musicflow_enriched.db'),
            'redis_url': os.getenv('REDIS_URL'),
            'cache_ttl_days': int(os.getenv('REDIS_TTL_DAYS', '7')),
            
            # API keys
            'musicbrainz_user_agent': os.getenv('MUSICBRAINZ_USER_AGENT', 'DJFlow/1.0'),
            'discogs_token': os.getenv('DISCOGS_TOKEN'),
            'spotify_client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'spotify_client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
            'lastfm_api_key': os.getenv('LASTFM_API_KEY'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'genius_access_token': os.getenv('GENIUS_ACCESS_TOKEN'),
            
            # Weights
            'weight_discogs': float(os.getenv('WEIGHT_DISCOGS', '0.30')),
            'weight_cnn': float(os.getenv('WEIGHT_CNN', '0.25')),
            'weight_gpt': float(os.getenv('WEIGHT_GPT', '0.25')),
            'weight_spotify': float(os.getenv('WEIGHT_SPOTIFY', '0.15')),
            'weight_lastfm': float(os.getenv('WEIGHT_LASTFM', '0.05')),
            
            # Coherence weights
            'w_bpm': float(os.getenv('WEIGHT_BPM', '0.25')),
            'w_key': float(os.getenv('WEIGHT_KEY', '0.30')),
            'w_valence': float(os.getenv('WEIGHT_VALENCE', '0.25')),
            'w_energy': float(os.getenv('WEIGHT_ENERGY', '0.20'))
        }
        
        # Initialize and register plugin
        self.plugin = DJPlaylistPlugin()
        if self.plugin.initialize(config):
            plugin_manager.register_plugin(self.plugin)
            plugin_manager.enable_plugin('DJPlaylistEngine')
            logger.info("DJ Playlist Engine initialized successfully")
        else:
            logger.error("Failed to initialize DJ Playlist Engine")
            sys.exit(1)
            
        # Initialize MixInKey integration
        db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
        if db_path.exists():
            self.mixinkey = MixInKeyIntegration(str(db_path))
            logger.info(f"Connected to Mixed In Key database: {db_path.name}")
        else:
            logger.warning("Mixed In Key database not found")
    
    async def scan_mixinkey(self, path: str = "/"):
        """Scan and enrich tracks from Mixed In Key database."""
        if not self.mixinkey:
            logger.error("Mixed In Key database not available")
            return
        
        logger.info(f"Scanning Mixed In Key database...")
        tracks = self.mixinkey.scan_mixinkey_database(path)
        
        if not tracks:
            logger.warning("No tracks found in Mixed In Key database")
            return
        
        logger.info(f"Found {len(tracks)} tracks in Mixed In Key")
        
        # Progress callback
        def progress_callback(completed, total, batch_results):
            percentage = (completed / total) * 100
            logger.info(f"Enrichment progress: {completed}/{total} ({percentage:.1f}%)")
            for result in batch_results:
                logger.debug(f"  ✓ {result.artist} - {result.title}: {result.genre} ({result.genre_confidence:.2f})")
        
        # Enrich tracks
        logger.info("Starting track enrichment...")
        enriched_tracks = await self.plugin.enrich_tracks_from_mixinkey(
            tracks,
            progress_callback=progress_callback
        )
        
        logger.info(f"Successfully enriched {len(enriched_tracks)} tracks")
        
        # Show enrichment stats
        stats = self.plugin.get_enrichment_stats()
        logger.info(f"Enrichment stats: {stats['total_tracks']} total, "
                   f"{stats['confidence_rate']:.1%} high confidence")
    
    def build_playlist(self, args):
        """Build a professional DJ playlist."""
        logger.info(f"Building playlist with target BPM: {args.target_bpm}, "
                   f"length: {args.length}, lambda: {args.lambda_param}")
        
        # Build configuration
        config = {
            'target_bpm': args.target_bpm,
            'target_length': args.length,
            'lambda_popularity': args.lambda_param,
            'max_bpm_delta': float(os.getenv('MAX_BPM_DELTA', '10')),
            'min_coherence_threshold': float(os.getenv('MIN_COHERENCE_THRESHOLD', '0.6')),
            'energy_arc_type': args.energy_arc,
            'export_format': args.format
        }
        
        # Add optional filters
        if args.genre:
            config['genre_filter'] = args.genre
        if args.year_min and args.year_max:
            config['year_range'] = (args.year_min, args.year_max)
        if args.seed_track:
            config['seed_track_id'] = args.seed_track
        
        # Generate playlist
        result = self.plugin.generate_playlist(config)
        
        if result.get('success'):
            # Save playlist
            output_path = args.output or f"djflow_playlist.{args.format}"
            with open(output_path, 'w') as f:
                f.write(result['playlist_data'])
            
            logger.info(f"Playlist saved to: {output_path}")
            
            # Show quality analysis
            quality = result['quality_analysis']
            logger.info(f"Quality Analysis: {quality['quality_summary']}")
            logger.info(f"  Average coherence: {quality['sequence_analysis']['average_coherence']:.3f}")
            logger.info(f"  Energy arc quality: {quality['sequence_analysis']['energy_arc_quality']:.3f}")
            logger.info(f"  Unique genres: {len(quality['unique_genres'])}")
        else:
            logger.error(f"Failed to generate playlist: {result.get('error')}")
    
    def check_keys(self, key1: str, key2: str):
        """Check Camelot Wheel compatibility between two keys."""
        result = self.plugin.get_camelot_compatibility(key1.upper(), key2.upper())
        
        print(f"\nCamelot Key Compatibility Check")
        print("=" * 40)
        print(f"Key 1: {result['key1']}")
        print(f"Key 2: {result['key2']}")
        print(f"Compatibility Score: {result['compatibility_score']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        
        print(f"\nOther compatible keys for {result['key1']}:")
        for key, score in result['compatible_keys']:
            print(f"  {key}: {score:.2f}")
    
    def show_stats(self):
        """Show enrichment database statistics."""
        stats = self.plugin.get_enrichment_stats()
        
        print(f"\nEnrichment Database Statistics")
        print("=" * 40)
        print(f"Total tracks: {stats['total_tracks']}")
        print(f"High confidence tracks: {stats['high_confidence_tracks']} ({stats['confidence_rate']:.1%})")
        print(f"Recent enrichments (24h): {stats['recent_enrichments']}")
        
        print(f"\nTop Genres:")
        for genre, count in list(stats['genre_distribution'].items())[:10]:
            print(f"  {genre}: {count}")
    
    def export_camelot_wheel(self, output_path: str):
        """Export Camelot Wheel visualization."""
        html_content = self.plugin.export_camelot_wheel_html()
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Camelot Wheel exported to: {output_path}")

def main():
    """Main entry point for DJFlow CLI."""
    parser = argparse.ArgumentParser(
        description='DJFlow - Professional DJ Playlist Generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Scan and enrich Mixed In Key database
  %(prog)s --scan-mik
  
  # Build a 30-track playlist at 128 BPM
  %(prog)s --build-playlist --target-bpm 128 --length 30
  
  # Build playlist with genre filter and energy arc
  %(prog)s --build-playlist --target-bpm 124 --genre "House" --energy-arc peak
  
  # Check key compatibility
  %(prog)s --check-keys 8A 8B
  
  # Export playlist in M3U format
  %(prog)s --build-playlist --target-bpm 120 --format m3u --output my_set.m3u
        '''
    )
    
    # Actions
    parser.add_argument('--scan-mik', action='store_true',
                       help='Scan and enrich Mixed In Key database')
    parser.add_argument('--build-playlist', action='store_true',
                       help='Build a professional DJ playlist')
    parser.add_argument('--check-keys', nargs=2, metavar=('KEY1', 'KEY2'),
                       help='Check Camelot key compatibility')
    parser.add_argument('--stats', action='store_true',
                       help='Show enrichment statistics')
    parser.add_argument('--export-wheel', metavar='PATH',
                       help='Export Camelot Wheel HTML visualization')
    
    # Playlist options
    parser.add_argument('--target-bpm', type=float, default=120,
                       help='Target BPM for playlist (default: 120)')
    parser.add_argument('--length', type=int, default=30,
                       help='Number of tracks in playlist (default: 30)')
    parser.add_argument('--lambda', dest='lambda_param', type=float, default=0.4,
                       help='Popularity weight 0-1 (default: 0.4)')
    parser.add_argument('--energy-arc', choices=['progressive', 'peak', 'valley', 'flat'],
                       default='progressive', help='Energy arc type')
    parser.add_argument('--genre', nargs='+', help='Filter by genres')
    parser.add_argument('--year-min', type=int, help='Minimum release year')
    parser.add_argument('--year-max', type=int, help='Maximum release year')
    parser.add_argument('--seed-track', help='Seed track ID')
    
    # Output options
    parser.add_argument('--format', choices=['json', 'm3u', 'csv'], default='json',
                       help='Export format (default: json)')
    parser.add_argument('--output', '-o', help='Output file path')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize CLI
    cli = DJFlowCLI()
    cli.initialize()
    
    # Execute requested action
    if args.scan_mik:
        asyncio.run(cli.scan_mixinkey())
    elif args.build_playlist:
        cli.build_playlist(args)
    elif args.check_keys:
        cli.check_keys(args.check_keys[0], args.check_keys[1])
    elif args.stats:
        cli.show_stats()
    elif args.export_wheel:
        cli.export_camelot_wheel(args.export_wheel)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()