#!/usr/bin/env python3
"""
Debug MixInKeyTrackData creation issue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.mixinkey_integration import MixInKeyTrackData

def test_dataclass_creation():
    """Test creating MixInKeyTrackData object"""
    
    print("🔍 TESTING MixInKeyTrackData CREATION")
    print("=" * 50)
    
    # Test data from our previous debug
    track_data = {
        'artist': 'Dire Straits', 
        'title': 'Tunnel of Love (Intro: The Carousel Waltz)', 
        'album': 'Making Movies', 
        'bpm': 141.27252197265625, 
        'key': '7A', 
        'energy': 6.0, 
        'year': 1980, 
        'bitrate': 829435, 
        'file_size': 50751045, 
        'volume': -15.67032241821289,
        'file_path': '/MixInKey_Placeholder/Dire Straits/Dire Straits - Making Movies - Tunnel of Love (Intro: The Carousel Waltz).mp3',
        'filename': 'Dire Straits - Making Movies - Tunnel of Love (Intro: The Carousel Waltz).mp3'
    }
    
    print(f"📊 Track data: {track_data}")
    
    try:
        # Try to create the object
        result = MixInKeyTrackData(**track_data, analyzed_by_mixinkey=True)
        print(f"✅ SUCCESS: Created track object")
        print(f"   Artist: {result.artist}")
        print(f"   Title: {result.title}")
        print(f"   BPM: {result.bpm}")
        print(f"   Key: {result.key}")
        print(f"   Energy: {result.energy}")
        print(f"   File path: {result.file_path}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED to create track object: {e}")
        print(f"   Error type: {type(e)}")
        
        # Try to identify which field is causing the problem
        print("\n🔍 Testing individual fields:")
        required_fields = ['file_path', 'filename']
        
        for field in required_fields:
            if field not in track_data:
                print(f"   ❌ Missing required field: {field}")
            else:
                print(f"   ✅ Has required field: {field} = {track_data[field]}")
        
        # Try with minimal data
        print("\n🔍 Testing with minimal data:")
        try:
            minimal_data = {
                'file_path': track_data['file_path'],
                'filename': track_data['filename']
            }
            minimal_result = MixInKeyTrackData(**minimal_data, analyzed_by_mixinkey=True)
            print("   ✅ Minimal object creation works")
        except Exception as e2:
            print(f"   ❌ Even minimal creation fails: {e2}")
        
        return False

if __name__ == "__main__":
    test_dataclass_creation()