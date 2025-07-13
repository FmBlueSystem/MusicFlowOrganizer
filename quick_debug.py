#!/usr/bin/env python3
"""
Quick debug script to see exactly what's happening
"""

import sqlite3
from pathlib import Path
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(__file__))
from src.core.mixinkey_integration import MixInKeyIntegration

def test_mixinkey_integration():
    """Test the actual integration class"""
    
    db_path = "/Users/freddymolina/Library/Application Support/Mixedinkey/Collection11.mikdb"
    
    print("🔍 TESTING MIXINKEY INTEGRATION CLASS")
    print("=" * 50)
    
    # Test with the actual class
    integration = MixInKeyIntegration(database_path=db_path)
    
    # Test scanning
    print("📊 Testing scan_mixinkey_database...")
    tracks = integration.scan_mixinkey_database("/fake/library/path")
    
    print(f"✅ Result: {len(tracks)} tracks found")
    
    if tracks:
        print("\n🎵 Sample tracks:")
        for i, (path, track) in enumerate(list(tracks.items())[:3]):
            print(f"  {i+1}. {track.artist} - {track.title}")
            print(f"     BPM: {track.bpm}, Key: {track.key}, Energy: {track.energy}")
            print(f"     Path: {path}")
    else:
        print("❌ No tracks found - checking database directly...")
        
        # Direct database check
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ZSONG")
        count = cursor.fetchone()[0]
        print(f"   Direct DB query: {count} records in ZSONG")
        
        cursor.execute("SELECT ZARTIST, ZNAME, ZTEMPO FROM ZSONG LIMIT 1")
        sample = cursor.fetchone()
        print(f"   Sample record: {sample}")
        
        conn.close()

if __name__ == "__main__":
    test_mixinkey_integration()