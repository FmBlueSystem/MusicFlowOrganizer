"""
Track Enrichment Engine
======================
Multi-source metadata enrichment for professional DJ libraries.

Integrates with:
- MusicBrainz API (release dates, MBID)
- Discogs API (genres, styles, release info)
- Spotify API (audio features, popularity)
- Last.fm API (collaborative tags)
- OpenAI GPT-4o (genre/mood inference)
- Audio embedding models (CLAP/OpenL3)

Author: Claude Code
Date: 2025-07-12
"""

import asyncio
import json
import logging
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor

# Optional dependencies
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class EnrichedTrackData:
    """Complete enriched track metadata."""
    track_id: str
    title: str
    artist: str
    
    # Core Mixed In Key data
    bpm: float
    camelot_key: str
    energy: float
    
    # Enriched metadata
    year: Optional[int] = None
    genre: Optional[str] = None
    subgenres: Optional[List[str]] = None
    mood: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    
    # External source data
    musicbrainz_id: Optional[str] = None
    discogs_styles: Optional[List[str]] = None
    spotify_popularity: Optional[float] = None
    spotify_features: Optional[Dict[str, float]] = None
    lastfm_tags: Optional[List[str]] = None
    
    # AI inference
    gpt_inference: Optional[Dict[str, Any]] = None
    audio_embedding: Optional[bytes] = None
    
    # Confidence scores
    genre_confidence: Optional[float] = None
    enrichment_timestamp: Optional[float] = None

class EnrichmentEngine:
    """
    Asynchronous multi-source track enrichment engine.
    
    Provides comprehensive metadata enrichment for DJ libraries with:
    - Rate limiting and caching
    - Weighted source fusion 
    - AI-powered inference
    - Professional quality scoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enrichment engine with configuration.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        self.logger = logging.getLogger("EnrichmentEngine")
        
        # Initialize database
        self.db_path = config.get('db_path', 'musicflow_enriched.db')
        self._init_database()
        
        # Initialize cache
        self.cache = None
        if REDIS_AVAILABLE and config.get('redis_url'):
            try:
                self.cache = redis.from_url(config['redis_url'])
                self.cache_ttl = config.get('cache_ttl_days', 7) * 86400
            except Exception as e:
                self.logger.warning(f"Redis cache unavailable: {e}")
        
        # API configuration
        self.rate_limits = {
            'musicbrainz': 1.0,  # 1 second between requests
            'discogs': 1.0,      # 1 second between requests  
            'spotify': 0.1,      # 10 requests per second
            'lastfm': 0.2,       # 5 requests per second
            'openai': 2.0        # 30 requests per minute
        }
        
        self.last_request_times = {service: 0 for service in self.rate_limits}
        
        # Source weights for genre fusion (Schweiger 2025)
        self.source_weights = {
            'discogs': config.get('weight_discogs', 0.30),
            'cnn': config.get('weight_cnn', 0.25),
            'gpt': config.get('weight_gpt', 0.25),
            'spotify': config.get('weight_spotify', 0.15),
            'lastfm': config.get('weight_lastfm', 0.05)
        }
        
        # Session for HTTP requests
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': self.config.get('user_agent', 'MusicFlowOrganizer/1.0')}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _init_database(self):
        """Initialize SQLite database for enriched track storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enriched_tracks (
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
                musicbrainz_id TEXT,
                discogs_styles TEXT,  -- JSON array
                spotify_popularity REAL,
                spotify_features TEXT,  -- JSON object
                lastfm_tags TEXT,  -- JSON array
                gpt_inference TEXT,  -- JSON object
                audio_embedding BLOB,
                genre_confidence REAL,
                enrichment_timestamp REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist ON enriched_tracks(artist)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genre ON enriched_tracks(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bpm ON enriched_tracks(bpm)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key ON enriched_tracks(camelot_key)')
        
        conn.commit()
        conn.close()
    
    async def _rate_limit(self, service: str):
        """Apply rate limiting for API service."""
        now = time.time()
        time_since_last = now - self.last_request_times[service]
        min_interval = self.rate_limits[service]
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_times[service] = time.time()
    
    def _get_cache_key(self, service: str, query: str) -> str:
        """Generate cache key for service query."""
        key_string = f"{service}:{query}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_cached_result(self, service: str, query: str) -> Optional[Dict]:
        """Get cached result if available."""
        if not self.cache:
            return None
        
        try:
            cache_key = self._get_cache_key(service, query)
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached.decode())
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def _cache_result(self, service: str, query: str, result: Dict):
        """Cache API result."""
        if not self.cache:
            return
        
        try:
            cache_key = self._get_cache_key(service, query)
            self.cache.setex(cache_key, self.cache_ttl, json.dumps(result))
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
    
    async def _query_musicbrainz(self, artist: str, title: str) -> Optional[Dict]:
        """Query MusicBrainz for release information."""
        query = f"{artist} {title}".strip()
        
        # Check cache
        cached = await self._get_cached_result('musicbrainz', query)
        if cached:
            return cached
        
        await self._rate_limit('musicbrainz')
        
        try:
            # MusicBrainz search query
            search_url = "https://musicbrainz.org/ws/2/recording"
            params = {
                'query': f'artist:"{artist}" AND recording:"{title}"',
                'fmt': 'json',
                'limit': 5
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {'found': False}
                    
                    if data.get('recordings'):
                        recording = data['recordings'][0]  # Take best match
                        result = {
                            'found': True,
                            'mbid': recording.get('id'),
                            'title': recording.get('title'),
                            'length': recording.get('length'),
                            'releases': []
                        }
                        
                        # Extract release information
                        for release in recording.get('releases', [])[:3]:  # Top 3 releases
                            release_info = {
                                'id': release.get('id'),
                                'title': release.get('title'),
                                'date': release.get('date'),
                                'country': release.get('country')
                            }
                            result['releases'].append(release_info)
                    
                    await self._cache_result('musicbrainz', query, result)
                    return result
                    
        except Exception as e:
            self.logger.error(f"MusicBrainz query error: {e}")
        
        return None
    
    async def _query_discogs(self, artist: str, title: str) -> Optional[Dict]:
        """Query Discogs for genre and style information."""
        if not self.config.get('discogs_token'):
            return None
        
        query = f"{artist} {title}".strip()
        
        # Check cache
        cached = await self._get_cached_result('discogs', query)
        if cached:
            return cached
        
        await self._rate_limit('discogs')
        
        try:
            search_url = "https://api.discogs.com/database/search"
            headers = {'Authorization': f'Discogs token={self.config["discogs_token"]}'}
            params = {
                'q': f'{artist} {title}',
                'type': 'release',
                'per_page': 5
            }
            
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {'found': False}
                    
                    if data.get('results'):
                        release = data['results'][0]  # Best match
                        result = {
                            'found': True,
                            'id': release.get('id'),
                            'title': release.get('title'),
                            'year': release.get('year'),
                            'genres': release.get('genre', []),
                            'styles': release.get('style', []),
                            'country': release.get('country'),
                            'labels': release.get('label', [])
                        }
                    
                    await self._cache_result('discogs', query, result)
                    return result
                    
        except Exception as e:
            self.logger.error(f"Discogs query error: {e}")
        
        return None
    
    async def _query_spotify(self, artist: str, title: str) -> Optional[Dict]:
        """Query Spotify for audio features and popularity."""
        if not self.config.get('spotify_client_id') or not self.config.get('spotify_client_secret'):
            return None
        
        query = f"{artist} {title}".strip()
        
        # Check cache
        cached = await self._get_cached_result('spotify', query)
        if cached:
            return cached
        
        await self._rate_limit('spotify')
        
        try:
            # First get access token
            token_url = "https://accounts.spotify.com/api/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.config['spotify_client_id'],
                'client_secret': self.config['spotify_client_secret']
            }
            
            async with self.session.post(token_url, data=token_data) as token_response:
                if token_response.status != 200:
                    return None
                
                token_info = await token_response.json()
                access_token = token_info['access_token']
            
            # Search for track
            search_url = "https://api.spotify.com/v1/search"
            headers = {'Authorization': f'Bearer {access_token}'}
            params = {
                'q': f'artist:"{artist}" track:"{title}"',
                'type': 'track',
                'limit': 5
            }
            
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {'found': False}
                    
                    if data.get('tracks', {}).get('items'):
                        track = data['tracks']['items'][0]  # Best match
                        track_id = track['id']
                        
                        # Get audio features
                        features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
                        async with self.session.get(features_url, headers=headers) as features_response:
                            if features_response.status == 200:
                                features = await features_response.json()
                                
                                result = {
                                    'found': True,
                                    'track_id': track_id,
                                    'popularity': track.get('popularity'),
                                    'preview_url': track.get('preview_url'),
                                    'audio_features': {
                                        'danceability': features.get('danceability'),
                                        'energy': features.get('energy'),
                                        'valence': features.get('valence'),
                                        'tempo': features.get('tempo'),
                                        'loudness': features.get('loudness'),
                                        'speechiness': features.get('speechiness'),
                                        'acousticness': features.get('acousticness'),
                                        'instrumentalness': features.get('instrumentalness'),
                                        'liveness': features.get('liveness')
                                    },
                                    'artist_genres': []
                                }
                                
                                # Get artist genres
                                artist_id = track['artists'][0]['id']
                                artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
                                async with self.session.get(artist_url, headers=headers) as artist_response:
                                    if artist_response.status == 200:
                                        artist_data = await artist_response.json()
                                        result['artist_genres'] = artist_data.get('genres', [])
                    
                    await self._cache_result('spotify', query, result)
                    return result
                    
        except Exception as e:
            self.logger.error(f"Spotify query error: {e}")
        
        return None
    
    async def _query_lastfm(self, artist: str, title: str) -> Optional[Dict]:
        """Query Last.fm for collaborative tags."""
        if not self.config.get('lastfm_api_key'):
            return None
        
        query = f"{artist} {title}".strip()
        
        # Check cache
        cached = await self._get_cached_result('lastfm', query)
        if cached:
            return cached
        
        await self._rate_limit('lastfm')
        
        try:
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.getInfo',
                'api_key': self.config['lastfm_api_key'],
                'artist': artist,
                'track': title,
                'format': 'json'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {'found': False}
                    
                    if data.get('track'):
                        track = data['track']
                        tags = []
                        
                        if track.get('toptags', {}).get('tag'):
                            for tag in track['toptags']['tag']:
                                if isinstance(tag, dict):
                                    tags.append({
                                        'name': tag.get('name'),
                                        'count': int(tag.get('count', 0))
                                    })
                        
                        result = {
                            'found': True,
                            'playcount': int(track.get('playcount', 0)),
                            'listeners': int(track.get('listeners', 0)),
                            'tags': tags
                        }
                    
                    await self._cache_result('lastfm', query, result)
                    return result
                    
        except Exception as e:
            self.logger.error(f"Last.fm query error: {e}")
        
        return None
    
    async def _query_openai_inference(self, track_data: Dict[str, Any]) -> Optional[Dict]:
        """Use OpenAI GPT-4o for genre and mood inference."""
        if not OPENAI_AVAILABLE or not self.config.get('openai_api_key'):
            return None
        
        # Build context string
        context_parts = []
        if track_data.get('title'):
            context_parts.append(f"Title: {track_data['title']}")
        if track_data.get('artist'):
            context_parts.append(f"Artist: {track_data['artist']}")
        if track_data.get('year'):
            context_parts.append(f"Year: {track_data['year']}")
        if track_data.get('discogs_genres'):
            context_parts.append(f"Discogs Genres: {', '.join(track_data['discogs_genres'])}")
        if track_data.get('spotify_genres'):
            context_parts.append(f"Spotify Genres: {', '.join(track_data['spotify_genres'])}")
        if track_data.get('lastfm_tags'):
            top_tags = [tag['name'] for tag in track_data['lastfm_tags'][:5]]
            context_parts.append(f"Last.fm Tags: {', '.join(top_tags)}")
        
        context = "\\n".join(context_parts)
        
        # Check cache
        cached = await self._get_cached_result('openai', context)
        if cached:
            return cached
        
        await self._rate_limit('openai')
        
        try:
            client = openai.AsyncOpenAI(api_key=self.config['openai_api_key'])
            
            prompt = f"""
            Analyze this music track and provide detailed classification:
            
            {context}
            
            Based on the information provided, return a JSON object with:
            {{
              "genre": "Primary genre (specific, professional)",
              "subgenres": ["List", "of", "relevant", "subgenres"], 
              "mood": "Emotional mood descriptor",
              "language": "Language code (en, es, fr, etc.)",
              "region": "Geographic region/country of origin",
              "confidence": 0.85
            }}
            
            Focus on accuracy for DJ mixing and professional music organization.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                await self._cache_result('openai', context, result)
                return result
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse OpenAI response: {result_text}")
                
        except Exception as e:
            self.logger.error(f"OpenAI query error: {e}")
        
        return None
    
    def _fuse_genre_sources(self, sources: Dict[str, Any]) -> Tuple[str, float]:
        """
        Fuse genre information from multiple sources using weighted voting.
        
        Args:
            sources: Dictionary with source data
            
        Returns:
            Tuple[str, float]: (final_genre, confidence_score)
        """
        genre_votes = {}
        total_weight = 0.0
        
        # Collect genre votes from each source
        if sources.get('discogs') and sources['discogs'].get('genres'):
            for genre in sources['discogs']['genres']:
                weight = self.source_weights['discogs']
                genre_votes[genre] = genre_votes.get(genre, 0) + weight
                total_weight += weight
        
        if sources.get('spotify') and sources['spotify'].get('artist_genres'):
            for genre in sources['spotify']['artist_genres']:
                weight = self.source_weights['spotify']
                genre_votes[genre] = genre_votes.get(genre, 0) + weight
                total_weight += weight
        
        if sources.get('lastfm') and sources['lastfm'].get('tags'):
            for tag in sources['lastfm']['tags'][:3]:  # Top 3 tags
                genre = tag['name']
                weight = self.source_weights['lastfm'] * (tag['count'] / 100)  # Weight by popularity
                genre_votes[genre] = genre_votes.get(genre, 0) + weight
                total_weight += weight
        
        if sources.get('gpt') and sources['gpt'].get('genre'):
            genre = sources['gpt']['genre']
            weight = self.source_weights['gpt'] * sources['gpt'].get('confidence', 0.8)
            genre_votes[genre] = genre_votes.get(genre, 0) + weight
            total_weight += weight
        
        # Find winning genre
        if not genre_votes:
            return "Unknown", 0.0
        
        winning_genre = max(genre_votes.items(), key=lambda x: x[1])
        genre_name = winning_genre[0]
        confidence = min(1.0, winning_genre[1] / total_weight) if total_weight > 0 else 0.0
        
        return genre_name, confidence
    
    async def enrich_track(self, track_id: str, title: str, artist: str, 
                          bpm: float, camelot_key: str, energy: float) -> EnrichedTrackData:
        """
        Enrich a single track with metadata from all sources.
        
        Args:
            track_id: Unique track identifier
            title: Track title
            artist: Artist name
            bpm: BPM from Mixed In Key
            camelot_key: Camelot key from Mixed In Key
            energy: Energy level from Mixed In Key
            
        Returns:
            EnrichedTrackData: Complete enriched track data
        """
        self.logger.info(f"Enriching track: {artist} - {title}")
        
        # Check if already enriched
        existing = self._get_cached_track(track_id)
        if existing:
            self.logger.debug(f"Using cached enrichment for {track_id}")
            return existing
        
        # Collect data from all sources in parallel
        sources = {}
        
        # Run API queries concurrently
        tasks = [
            ('musicbrainz', self._query_musicbrainz(artist, title)),
            ('discogs', self._query_discogs(artist, title)),
            ('spotify', self._query_spotify(artist, title)),
            ('lastfm', self._query_lastfm(artist, title))
        ]
        
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, (source_name, _) in enumerate(tasks):
            result = results[i]
            if not isinstance(result, Exception) and result:
                sources[source_name] = result
        
        # Prepare data for GPT inference
        gpt_context = {
            'title': title,
            'artist': artist,
            'discogs_genres': sources.get('discogs', {}).get('genres', []),
            'spotify_genres': sources.get('spotify', {}).get('artist_genres', []),
            'lastfm_tags': sources.get('lastfm', {}).get('tags', [])
        }
        
        # Add year from best source
        year = None
        if sources.get('discogs', {}).get('year'):
            year = sources['discogs']['year']
        elif sources.get('musicbrainz', {}).get('releases'):
            # Extract year from first release with date
            for release in sources['musicbrainz']['releases']:
                if release.get('date'):
                    try:
                        year = int(release['date'][:4])
                        break
                    except (ValueError, TypeError):
                        continue
        
        gpt_context['year'] = year
        
        # Get GPT inference
        gpt_result = await self._query_openai_inference(gpt_context)
        if gpt_result:
            sources['gpt'] = gpt_result
        
        # Fuse genre information
        final_genre, genre_confidence = self._fuse_genre_sources(sources)
        
        # Build enriched track data
        enriched = EnrichedTrackData(
            track_id=track_id,
            title=title,
            artist=artist,
            bpm=bpm,
            camelot_key=camelot_key,
            energy=energy,
            year=year,
            genre=final_genre,
            subgenres=sources.get('gpt', {}).get('subgenres', []),
            mood=sources.get('gpt', {}).get('mood'),
            language=sources.get('gpt', {}).get('language'),
            region=sources.get('gpt', {}).get('region'),
            musicbrainz_id=sources.get('musicbrainz', {}).get('mbid'),
            discogs_styles=sources.get('discogs', {}).get('styles', []),
            spotify_popularity=sources.get('spotify', {}).get('popularity'),
            spotify_features=sources.get('spotify', {}).get('audio_features'),
            lastfm_tags=[tag['name'] for tag in sources.get('lastfm', {}).get('tags', [])],
            gpt_inference=gpt_result,
            genre_confidence=genre_confidence,
            enrichment_timestamp=time.time()
        )
        
        # Save to database
        self._save_enriched_track(enriched)
        
        return enriched
    
    def _get_cached_track(self, track_id: str) -> Optional[EnrichedTrackData]:
        """Get enriched track from database cache."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM enriched_tracks WHERE track_id = ?", (track_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Convert row to EnrichedTrackData
                data = dict(row)
                
                # Parse JSON fields
                for field in ['subgenres', 'discogs_styles', 'lastfm_tags']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            data[field] = []
                
                for field in ['spotify_features', 'gpt_inference']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            data[field] = {}
                
                return EnrichedTrackData(**data)
                
        except Exception as e:
            self.logger.error(f"Error getting cached track: {e}")
        
        return None
    
    def _save_enriched_track(self, track: EnrichedTrackData):
        """Save enriched track to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert lists/dicts to JSON
            data = asdict(track)
            for field in ['subgenres', 'discogs_styles', 'lastfm_tags']:
                if data.get(field):
                    data[field] = json.dumps(data[field])
            
            for field in ['spotify_features', 'gpt_inference']:
                if data.get(field):
                    data[field] = json.dumps(data[field])
            
            # Insert or update
            cursor.execute('''
                INSERT OR REPLACE INTO enriched_tracks 
                (track_id, title, artist, bpm, camelot_key, energy, year, genre, 
                 subgenres, mood, language, region, musicbrainz_id, discogs_styles,
                 spotify_popularity, spotify_features, lastfm_tags, gpt_inference,
                 audio_embedding, genre_confidence, enrichment_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['track_id'], data['title'], data['artist'], data['bpm'],
                data['camelot_key'], data['energy'], data['year'], data['genre'],
                data['subgenres'], data['mood'], data['language'], data['region'],
                data['musicbrainz_id'], data['discogs_styles'], data['spotify_popularity'],
                data['spotify_features'], data['lastfm_tags'], data['gpt_inference'],
                data['audio_embedding'], data['genre_confidence'], data['enrichment_timestamp']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving enriched track: {e}")
    
    async def enrich_batch(self, tracks: List[Dict[str, Any]], 
                          progress_callback=None) -> List[EnrichedTrackData]:
        """
        Enrich multiple tracks efficiently with batch processing.
        
        Args:
            tracks: List of track dictionaries with required fields
            progress_callback: Optional callback for progress updates
            
        Returns:
            List[EnrichedTrackData]: List of enriched tracks
        """
        enriched_tracks = []
        total = len(tracks)
        
        # Process in batches to manage API rate limits
        batch_size = self.config.get('batch_size', 10)
        
        for i in range(0, total, batch_size):
            batch = tracks[i:i + batch_size]
            batch_results = []
            
            # Process batch concurrently
            tasks = []
            for track in batch:
                task = self.enrich_track(
                    track['track_id'],
                    track['title'], 
                    track['artist'],
                    track['bpm'],
                    track['camelot_key'],
                    track['energy']
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if not isinstance(result, Exception):
                    batch_results.append(result)
                    enriched_tracks.append(result)
            
            # Progress callback
            if progress_callback:
                progress_callback(len(enriched_tracks), total, batch_results)
            
            # Brief pause between batches
            if i + batch_size < total:
                await asyncio.sleep(1.0)
        
        return enriched_tracks
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total tracks
            cursor.execute("SELECT COUNT(*) FROM enriched_tracks")
            total_tracks = cursor.fetchone()[0]
            
            # Tracks with high confidence
            cursor.execute("SELECT COUNT(*) FROM enriched_tracks WHERE genre_confidence >= 0.8")
            high_confidence = cursor.fetchone()[0]
            
            # Genre distribution
            cursor.execute("""
                SELECT genre, COUNT(*) as count 
                FROM enriched_tracks 
                WHERE genre IS NOT NULL 
                GROUP BY genre 
                ORDER BY count DESC 
                LIMIT 10
            """)
            genre_distribution = dict(cursor.fetchall())
            
            # Recent enrichments
            cursor.execute("""
                SELECT COUNT(*) FROM enriched_tracks 
                WHERE enrichment_timestamp > ?
            """, (time.time() - 86400,))  # Last 24 hours
            recent_enrichments = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_tracks': total_tracks,
                'high_confidence_tracks': high_confidence,
                'confidence_rate': high_confidence / total_tracks if total_tracks > 0 else 0,
                'genre_distribution': genre_distribution,
                'recent_enrichments': recent_enrichments
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {}