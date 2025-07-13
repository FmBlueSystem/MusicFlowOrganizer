#!/usr/bin/env python3
"""
Test Persistence System
=======================
Verificar que el sistema de persistencia de datos funciona correctamente
"""

import json
import time
from pathlib import Path

def test_cache_system():
    """Test the persistence cache system."""
    print("🔍 TESTING PERSISTENCE SYSTEM")
    print("=" * 50)
    
    settings_dir = Path.home() / ".musicflow_organizer"
    cache_file = settings_dir / "analysis_cache.json"
    settings_file = settings_dir / "settings.json"
    
    print(f"📁 Settings directory: {settings_dir}")
    print(f"📁 Directory exists: {settings_dir.exists()}")
    
    if settings_file.exists():
        print(f"⚙️  Settings file exists: {settings_file}")
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            print(f"📊 Settings content: {json.dumps(settings, indent=2)}")
        except Exception as e:
            print(f"❌ Error reading settings: {e}")
    else:
        print("📝 No settings file found")
    
    if cache_file.exists():
        print(f"💾 Cache file exists: {cache_file}")
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Show cache summary
            library_path = cache_data.get('library_path', 'Unknown')
            tracks_count = len(cache_data.get('tracks_database', {}))
            cache_timestamp = cache_data.get('cache_timestamp', 0)
            cache_age = time.time() - cache_timestamp
            cache_age_hours = cache_age / 3600
            
            print(f"📊 CACHE SUMMARY:")
            print(f"   • Library Path: {library_path}")
            print(f"   • Tracks Count: {tracks_count}")
            print(f"   • Cache Age: {cache_age_hours:.1f} hours")
            print(f"   • App Version: {cache_data.get('app_version', 'Unknown')}")
            
            # Verify cache validity
            if cache_age > (7 * 24 * 3600):  # 7 days
                print("⚠️  Cache is older than 7 days - would be ignored")
            else:
                print("✅ Cache is fresh and valid")
            
            if Path(library_path).exists():
                print("✅ Library path still exists")
            else:
                print("❌ Library path no longer exists")
                
        except Exception as e:
            print(f"❌ Error reading cache: {e}")
    else:
        print("📝 No cache file found yet")
    
    print(f"\n🎯 PERSISTENCE STATUS:")
    if cache_file.exists():
        print("✅ App will load previous analysis on next startup")
        print("✅ User won't need to re-analyze library")
        print("✅ Fast startup with cached data")
    else:
        print("📝 No cached data - first run will require analysis")
        print("📝 After analysis, data will be cached for future runs")

def create_test_cache():
    """Create a test cache file to demonstrate functionality."""
    print(f"\n🧪 CREATING TEST CACHE")
    print("=" * 50)
    
    settings_dir = Path.home() / ".musicflow_organizer"
    settings_dir.mkdir(exist_ok=True)
    
    cache_file = settings_dir / "analysis_cache.json"
    
    # Create test data
    test_cache = {
        'library_path': '/path/to/test/library',
        'analysis_results': {
            'total_files': 100,
            'mixinkey_analyzed': 85,
            'processed_files': 100,
            'processing_time': 45.2
        },
        'tracks_database': {
            '/path/to/track1.mp3': {
                'title': 'Test Track 1',
                'artist': 'Test Artist',
                'genre': 'Electronic',
                'bpm': 128.0,
                'key': '7A'
            },
            '/path/to/track2.mp3': {
                'title': 'Test Track 2', 
                'artist': 'Test Artist 2',
                'genre': 'House',
                'bpm': 125.5,
                'key': '8B'
            }
        },
        'cache_timestamp': time.time(),
        'app_version': '1.0.0'
    }
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(test_cache, f, indent=2)
        
        print(f"✅ Test cache created: {cache_file}")
        print(f"📊 Test data contains {len(test_cache['tracks_database'])} tracks")
        print("🔄 Next app startup will load this test data")
        
    except Exception as e:
        print(f"❌ Failed to create test cache: {e}")

if __name__ == "__main__":
    print("🎧 MUSICFLOW ORGANIZER - PERSISTENCE TEST")
    print("=" * 80)
    
    test_cache_system()
    
    print(f"\n💡 INSTRUCTIONS:")
    print("1. Run this test to check current persistence status")
    print("2. Launch MusicFlow Organizer and analyze a library")
    print("3. Close the app and run this test again")
    print("4. Relaunch MusicFlow - it should load cached data")
    print("5. No re-analysis needed!")
    
    print(f"\n📋 CACHE BENEFITS:")
    print("✅ Instant app startup with previous data")
    print("✅ No need to re-analyze same library")
    print("✅ Preserves AI enhancements and custom data")
    print("✅ 7-day cache expiration for data freshness")
    print("✅ Auto-detection of library path changes")
    
    # Optionally create test cache
    user_input = input("\nCreate test cache? (y/n): ").lower()
    if user_input == 'y':
        create_test_cache()