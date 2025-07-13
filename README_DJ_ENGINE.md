# DJ Playlist Generation Engine

## Overview

The DJ Playlist Generation Engine is a professional-grade plugin for MusicFlow Organizer that provides advanced playlist generation capabilities optimized for DJs. It integrates seamlessly with Mixed In Key databases and enriches tracks with metadata from multiple sources.

## Features

### 🎵 Core Capabilities
- **Mixed In Key Integration**: Direct reading of Collection11.mikdb databases
- **Multi-Source Enrichment**: MusicBrainz, Discogs, Spotify, Last.fm, OpenAI GPT-4o
- **Harmonic Mixing**: Extended Camelot Wheel with 42+ compatibility relationships
- **Coherence Metrics**: Schweiger 2025 methodology (BPM, key, valence, energy)
- **Professional Playlists**: Greedy algorithm with energy arc management

### 🔧 Technical Features
- **Asynchronous Processing**: High-performance API integration
- **Redis Caching**: 7-day TTL for API responses
- **Weighted Genre Fusion**: Configurable source weights
- **Multiple Export Formats**: JSON, M3U, CSV
- **Non-Destructive Plugin**: Modular architecture preserves existing functionality

## Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
# or with Poetry
poetry install
```

2. **Configure API Keys**:
Edit `.env` file with your API credentials:
```env
DISCOGS_TOKEN=your_token_here
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_secret
LASTFM_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
```

3. **Verify Mixed In Key Database**:
```bash
ls ~/Library/Application\ Support/Mixedinkey/Collection11.mikdb
```

## Usage

### Command Line Interface (djflow.py)

#### Scan and Enrich Mixed In Key Database
```bash
./djflow.py --scan-mik
```

#### Generate Professional DJ Playlist
```bash
# Basic playlist at 128 BPM
./djflow.py --build-playlist --target-bpm 128 --length 30

# House music playlist with peak energy arc
./djflow.py --build-playlist --target-bpm 124 --genre House --energy-arc peak

# Export as M3U for DJ software
./djflow.py --build-playlist --target-bpm 120 --format m3u -o my_set.m3u
```

#### Check Harmonic Compatibility
```bash
./djflow.py --check-keys 8A 9A
```

#### View Statistics
```bash
./djflow.py --stats
```

### Python API

```python
from src.plugins.dj_playlist_plugin import DJPlaylistPlugin
from src.plugins.dj_engine.playlist_builder import PlaylistConfig

# Initialize plugin
plugin = DJPlaylistPlugin()
plugin.initialize(config)
plugin.enable()

# Generate playlist
config = PlaylistConfig(
    target_bpm=124,
    target_length=50,
    lambda_popularity=0.6,  # Favor popular tracks
    energy_arc_type='progressive'
)

result = plugin.generate_playlist(config.dict())
```

## Configuration

### Environment Variables
```env
# Playlist defaults
DEFAULT_PLAYLIST_LENGTH=30
DEFAULT_TARGET_BPM=120
DEFAULT_LAMBDA_POPULARITY=0.4
MAX_BPM_DELTA=10
MIN_COHERENCE_THRESHOLD=0.6

# Source weights (must sum to 1.0)
WEIGHT_DISCOGS=0.30
WEIGHT_CNN=0.25
WEIGHT_GPT=0.25
WEIGHT_SPOTIFY=0.15
WEIGHT_LASTFM=0.05

# Coherence weights (must sum to 1.0)
WEIGHT_BPM=0.25
WEIGHT_KEY=0.30
WEIGHT_VALENCE=0.25
WEIGHT_ENERGY=0.20
```

### Energy Arc Types
- **progressive**: Gradual build from 0.3 to 0.9
- **peak**: Build to peak at 70%, then wind down
- **valley**: Start high, dip in middle, recover
- **flat**: Consistent energy throughout

## Algorithm Details

### Greedy Track Selection
```
Score(track_n, candidate) = 0.6 × key_score + 0.2 × tempo_similarity + 0.2 × coherence_mood
```

### Lambda Parameter
Balances popularity vs novelty:
```
total_score = λ × popularity + (1-λ) × novelty
```
- λ = 1.0: Only popular tracks
- λ = 0.0: Only novel/underground tracks
- λ = 0.4: Balanced selection (default)

### Camelot Wheel Compatibility
| Relationship | Score | Example |
|-------------|-------|---------|
| Same key | 1.0 | 8A → 8A |
| Relative major/minor | 0.9 | 8A → 8B |
| Adjacent keys | 0.8 | 8A → 7A, 9A |
| Perfect fifth | 0.7 | 8A → 3A |
| Third minor | 0.6 | 8A → 11A |
| Submediant | 0.5 | 8A → 12A |

## Database Schema

### Enriched Tracks Table
```sql
CREATE TABLE enriched_tracks (
    track_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    bpm REAL,
    camelot_key TEXT,
    energy REAL,
    year INTEGER,
    genre TEXT,
    subgenres TEXT,  -- JSON array
    mood TEXT,
    language TEXT,
    region TEXT,
    spotify_popularity REAL,
    genre_confidence REAL,
    enrichment_timestamp REAL
);
```

## Performance Metrics

- **Enrichment Speed**: ~5-10 tracks/second (with caching)
- **Playlist Generation**: <2 seconds for 50 tracks
- **Genre Accuracy**: 90%+ with multi-source fusion
- **Coherence Average**: 0.70+ for professional playlists

## Troubleshooting

### No Mixed In Key Database Found
```bash
# Check alternate locations
find ~/Library -name "*.mikdb" 2>/dev/null
```

### API Rate Limits
- Increase delays in `rate_limits` configuration
- Enable Redis caching for better performance

### Low Genre Confidence
- Ensure all API keys are configured
- Check internet connectivity
- Verify track metadata quality

## Future Enhancements

1. **Audio Analysis**: CNN-based genre classification
2. **Lyrics Analysis**: Mood detection from lyrics
3. **Web Interface**: React-based playlist builder
4. **DJ Software Export**: Direct integration with Traktor/Serato
5. **Collaborative Playlists**: Multi-user playlist generation

## License

This plugin is part of MusicFlow Organizer and follows the same license terms.