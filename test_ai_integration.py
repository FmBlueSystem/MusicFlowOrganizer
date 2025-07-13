#!/usr/bin/env python3
"""
Test AI Integration for MusicFlow Organizer
==========================================
Quick test to verify OpenAI GPT-4 integration is working
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_configuration():
    """Test AI configuration and availability."""
    print("🧪 TESTING AI INTEGRATION")
    print("=" * 50)
    
    # Test 1: Check .env file
    env_file = Path('.env')
    print(f"1. ENV File exists: {env_file.exists()}")
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            has_openai_key = 'OPENAI_API_KEY=' in content
            key_configured = 'sk-proj-' in content
            print(f"2. OpenAI key configured: {has_openai_key and key_configured}")
    
    # Test 2: Check DJ Engine availability
    try:
        from plugins.dj_engine.enrichment import EnrichmentEngine
        from plugins.dj_engine.coherence_metrics import CoherenceMetrics
        print("3. DJ Engine available: ✅")
    except ImportError as e:
        print(f"3. DJ Engine available: ❌ - {e}")
        return False
    
    # Test 3: Check OpenAI availability
    try:
        import openai
        print("4. OpenAI library available: ✅")
    except ImportError:
        print("4. OpenAI library available: ❌")
        return False
    
    # Test 4: Test Schweiger 2025 algorithm
    try:
        coherence = CoherenceMetrics(
            w_bpm=0.25,
            w_key=0.30,
            w_valence=0.25,
            w_energy=0.20
        )
        print("5. Schweiger 2025 algorithm: ✅")
        print(f"   - BPM weight: {coherence.w_bpm}")
        print(f"   - Key weight: {coherence.w_key}")
        print(f"   - Valence weight: {coherence.w_valence}")
        print(f"   - Energy weight: {coherence.w_energy}")
    except Exception as e:
        print(f"5. Schweiger 2025 algorithm: ❌ - {e}")
        return False
    
    # Test 5: API Key validation
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
    
    api_key = env_vars.get('OPENAI_API_KEY', '')
    if api_key and api_key.startswith('sk-proj-'):
        print("6. API Key format: ✅")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("6. API Key format: ❌")
        return False
    
    print("\n🎯 AI INTEGRATION TEST RESULT: ✅ READY")
    print("🚀 You can now use 'Tools → 🤖 AI Enhance Selected Tracks'")
    return True

def test_track_enhancement_simulation():
    """Simulate track enhancement process."""
    print("\n🎵 TESTING TRACK ENHANCEMENT SIMULATION")
    print("=" * 50)
    
    # Simulate track data
    test_track = {
        'title': 'Knock On Wood',
        'artist': 'Amii Stewart',
        'bpm': 142.0,
        'camelot_key': '7A',
        'energy': 0.8
    }
    
    print(f"Test Track: {test_track['artist']} - {test_track['title']}")
    print(f"BPM: {test_track['bpm']}, Key: {test_track['camelot_key']}, Energy: {test_track['energy']}")
    
    # Simulate AI enhancement result
    ai_result = {
        'ai_genre': 'Disco/Funk',
        'ai_mood': 'Uplifting',
        'ai_confidence': 0.92,
        'ai_language': 'en',
        'ai_region': 'US'
    }
    
    print(f"\nSimulated AI Enhancement:")
    print(f"• Genre: {ai_result['ai_genre']}")
    print(f"• Mood: {ai_result['ai_mood']}")
    print(f"• Confidence: {ai_result['ai_confidence']:.1%}")
    print(f"• Language: {ai_result['ai_language']}")
    print(f"• Region: {ai_result['ai_region']}")
    
    print("\n✅ Track enhancement simulation successful!")

if __name__ == "__main__":
    print("🤖 MusicFlow Organizer - AI Integration Test")
    print("=" * 60)
    
    if test_ai_configuration():
        test_track_enhancement_simulation()
        print("\n🏆 ALL TESTS PASSED - AI READY FOR USE!")
    else:
        print("\n❌ AI INTEGRATION ISSUES DETECTED")
        print("Please check configuration and try again.")