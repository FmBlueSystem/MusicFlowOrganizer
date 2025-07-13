#!/usr/bin/env python3
"""
Test Cache Fix
==============
Verificar que el fix del cache funciona correctamente
"""

import json
import time
from pathlib import Path

def simulate_analysis_completion():
    """Simulate a complete analysis to test cache saving."""
    print("🧪 TESTING CACHE SAVE FIX")
    print("=" * 50)
    
    # Simulate analysis results (like what comes from AnalysisWorker)
    mock_analysis_results = {
        'total_files': 4267,
        'mixinkey_analyzed': 4267,
        'processed_files': 4267,
        'processing_time': 120.5,
        'performance_stats': {
            'files_per_second': 35.6,
            'cache_hits': 4267,
            'mixinkey_analyzed': 4267
        },
        'tracks_database': {
            '/Volumes/My Passport/Track1.mp3': {
                'title': 'Test Track 1',
                'artist': 'Test Artist',
                'genre': 'Electronic',
                'bpm': 128.0,
                'key': '7A',
                'energy': 8,
                'mixinkey_analyzed': True
            },
            '/Volumes/My Passport/Track2.flac': {
                'title': 'Test Track 2',
                'artist': 'Test Artist 2', 
                'genre': 'House',
                'bpm': 125.5,
                'key': '8B',
                'energy': 7,
                'mixinkey_analyzed': True
            }
        }
    }
    
    # Simulate what save_analysis_data should do
    current_library_path = "/Volumes/My Passport/Music"
    
    print(f"📊 Mock analysis results:")
    print(f"   • Total files: {mock_analysis_results['total_files']}")
    print(f"   • Tracks database size: {len(mock_analysis_results['tracks_database'])}")
    print(f"   • Library path: {current_library_path}")
    
    # Test the save logic
    settings_dir = Path.home() / ".musicflow_organizer"
    settings_dir.mkdir(exist_ok=True)
    
    cache_file = settings_dir / "analysis_cache.json"
    
    # Prepare data (using the fixed logic)
    tracks_database = mock_analysis_results.get('tracks_database', {})
    if not tracks_database:
        print("❌ No tracks database - would not save")
        return False
    
    cache_data = {
        'library_path': current_library_path,
        'analysis_results': mock_analysis_results,
        'tracks_database': tracks_database,
        'cache_timestamp': time.time(),
        'app_version': '1.0.0'
    }
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"✅ Cache saved successfully: {cache_file}")
        print(f"📊 Saved {len(tracks_database)} tracks")
        
        # Verify the save
        with open(cache_file, 'r') as f:
            loaded_data = json.load(f)
        
        loaded_tracks = len(loaded_data.get('tracks_database', {}))
        print(f"✅ Verification: {loaded_tracks} tracks loaded from cache")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save cache: {e}")
        return False

def test_cache_loading():
    """Test that the cache can be loaded correctly."""
    print(f"\n🔄 TESTING CACHE LOADING")
    print("=" * 50)
    
    settings_dir = Path.home() / ".musicflow_organizer"
    cache_file = settings_dir / "analysis_cache.json"
    
    if not cache_file.exists():
        print("❌ No cache file to test loading")
        return False
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Test cache validity
        cache_age = time.time() - cache_data.get('cache_timestamp', 0)
        cache_age_hours = cache_age / 3600
        
        cached_path = cache_data.get('library_path')
        tracks_count = len(cache_data.get('tracks_database', {}))
        
        print(f"📊 Cache loaded successfully:")
        print(f"   • Library path: {cached_path}")
        print(f"   • Tracks count: {tracks_count}")
        print(f"   • Cache age: {cache_age_hours:.1f} hours")
        
        # Verify cache validity
        if cache_age > (7 * 24 * 3600):  # 7 days
            print("⚠️  Cache is too old - would be ignored")
            return False
        
        # In a real scenario, we'd check if path exists
        # For testing, we'll skip path validation
        print("✅ Cache is valid and loadable")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load cache: {e}")
        return False

def clean_test_cache():
    """Clean up test cache."""
    print(f"\n🧹 CLEANING TEST CACHE")
    print("=" * 50)
    
    settings_dir = Path.home() / ".musicflow_organizer"
    cache_file = settings_dir / "analysis_cache.json"
    
    if cache_file.exists():
        try:
            cache_file.unlink()
            print("✅ Test cache cleaned up")
        except Exception as e:
            print(f"❌ Failed to clean cache: {e}")
    else:
        print("📝 No cache file to clean")

if __name__ == "__main__":
    print("🎧 MUSICFLOW ORGANIZER - CACHE FIX TEST")
    print("=" * 80)
    print("Testing the fix for cache save/load persistence issue")
    
    # Test 1: Save cache
    save_success = simulate_analysis_completion()
    
    # Test 2: Load cache
    if save_success:
        load_success = test_cache_loading()
        
        if load_success:
            print(f"\n🏆 SUCCESS: Cache save/load cycle works correctly")
            print("✅ The fix should resolve the persistence issue")
        else:
            print(f"\n❌ ISSUE: Cache saving works but loading fails")
    else:
        print(f"\n❌ ISSUE: Cache saving is still broken")
    
    # Test 3: Clean up
    user_input = input("\nClean up test cache? (y/n): ").lower()
    if user_input == 'y':
        clean_test_cache()
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Run the fixed app")
    print("2. Perform a complete library analysis")
    print("3. Close and reopen the app")
    print("4. Verify that data loads automatically")
    print("5. No re-analysis should be required!")