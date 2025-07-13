#!/usr/bin/env python3
"""
Debug parsing specific issue
"""

import sqlite3
from pathlib import Path

def test_parsing():
    """Test the exact parsing issue"""
    
    db_path = "/Users/freddymolina/Library/Application Support/Mixedinkey/Collection11.mikdb"
    
    print("🔍 TESTING PARSING ISSUE")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get one record to test parsing
    cursor.execute("SELECT * FROM ZSONG LIMIT 1")
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    
    print(f"📋 Columns: {columns}")
    print(f"📄 First row: {row[:10]}...") # First 10 values
    
    # Create the row_data dict like the code does
    row_data = dict(zip(columns, row))
    
    print("\n🗺️ TESTING FIELD MAPPING:")
    print("-" * 30)
    
    # Test the field mapping from the code
    field_mapping = {
        'ZARTIST': 'artist',
        'ZNAME': 'title',
        'ZALBUM': 'album', 
        'ZGENRE': 'genre',
        'ZTEMPO': 'bpm',
        'ZKEY': 'key',
        'ZENERGY': 'energy',
        'ZYEAR': 'year',
        'ZBITRATE': 'bitrate',
        'ZFILESIZE': 'file_size',
        'ZVOLUME': 'volume',
    }
    
    track_data = {}
    
    print("🔍 Field mapping results:")
    for db_field, track_field in field_mapping.items():
        if db_field in row_data and row_data[db_field] is not None:
            value = row_data[db_field]
            track_data[track_field] = value
            print(f"  ✅ {db_field} -> {track_field}: {value}")
        else:
            print(f"  ❌ {db_field} -> {track_field}: NOT FOUND or NULL")
    
    print(f"\n📊 Final track_data: {track_data}")
    
    # Test file_path generation
    if 'artist' in track_data and 'title' in track_data:
        artist = str(track_data.get('artist', 'Unknown Artist')).replace('/', '_')
        title = str(track_data.get('title', 'Unknown Title')).replace('/', '_')
        album = str(track_data.get('album', '')).replace('/', '_')
        
        if album:
            filename = f"{artist} - {album} - {title}.mp3"
        else:
            filename = f"{artist} - {title}.mp3"
        
        file_path = f"/MixInKey_Placeholder/{artist}/{filename}"
        track_data['file_path'] = file_path
        print(f"🔗 Generated file_path: {file_path}")
    
    # Test if track would be created
    print(f"\n🎯 WOULD CREATE TRACK: {'YES' if 'file_path' in track_data else 'NO'}")
    print(f"   Required fields present: {{'file_path': 'file_path' in track_data}}")
    
    conn.close()

if __name__ == "__main__":
    test_parsing()