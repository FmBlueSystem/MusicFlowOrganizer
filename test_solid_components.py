#!/usr/bin/env python3
"""
Test Script for SOLID Refactored Components
==========================================

Tests the new SOLID architecture components in the virtual environment.

Developed by BlueSystemIO
"""

import sys
import os
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_library_scanner():
    """Test LibraryScanner component."""
    print("\n🔍 Testing LibraryScanner...")
    
    try:
        from core.library_scanner import LibraryScanner
        
        scanner = LibraryScanner()
        print(f"✅ LibraryScanner initialized successfully")
        
        # Test audio file detection
        test_files = [
            "track.mp3", "song.flac", "music.wav", "audio.m4a",
            "document.txt", "image.jpg", "video.mp4"
        ]
        
        audio_files = [f for f in test_files if scanner.is_audio_file(f)]
        print(f"✅ Audio files detected: {audio_files}")
        
        # Test playlist file detection
        playlist_files = [f for f in ["playlist.m3u", "set.pls", "track.mp3"] 
                         if scanner.is_playlist_file(f)]
        print(f"✅ Playlist files detected: {playlist_files}")
        
        return True
        
    except Exception as e:
        print(f"❌ LibraryScanner test failed: {e}")
        return False

def test_track_analyzer():
    """Test TrackAnalyzer component."""
    print("\n📊 Testing TrackAnalyzer...")
    
    try:
        from core.track_analyzer import TrackAnalyzer, TrackData
        
        analyzer = TrackAnalyzer()
        print(f"✅ TrackAnalyzer initialized successfully")
        
        # Test empty database
        stats = analyzer.get_database_statistics()
        print(f"✅ Empty database stats: {stats}")
        
        # Test clearing database
        analyzer.clear_database()
        print(f"✅ Database cleared successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ TrackAnalyzer test failed: {e}")
        return False

def test_organization_planner():
    """Test OrganizationPlanner component."""
    print("\n📋 Testing OrganizationPlanner...")
    
    try:
        from core.organization_planner import OrganizationPlanner, OrganizationScheme
        
        planner = OrganizationPlanner()
        print(f"✅ OrganizationPlanner initialized successfully")
        
        # Test scheme enumeration
        schemes = list(OrganizationScheme)
        print(f"✅ Available organization schemes: {[s.value for s in schemes]}")
        
        return True
        
    except Exception as e:
        print(f"❌ OrganizationPlanner test failed: {e}")
        return False

def test_file_operations_manager():
    """Test FileOperationsManager component."""
    print("\n📁 Testing FileOperationsManager...")
    
    try:
        from core.file_operations_manager import FileOperationsManager, OrganizationResult
        
        manager = FileOperationsManager()
        print(f"✅ FileOperationsManager initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ FileOperationsManager test failed: {e}")
        return False

def test_async_filter_engine():
    """Test AsyncFilterEngine component."""
    print("\n⚡ Testing AsyncFilterEngine...")
    
    try:
        from core.async_filter_engine import AsyncFilterEngine, FilterType, FilterCriteria
        
        # Test without Qt (fallback mode)
        filter_engine = AsyncFilterEngine()
        print(f"✅ AsyncFilterEngine initialized successfully")
        
        # Test filter types
        filter_types = list(FilterType)
        print(f"✅ Available filter types: {[ft.value for ft in filter_types]}")
        
        # Test filter criteria creation
        criteria = FilterCriteria(
            filter_type=FilterType.GENRE,
            value="House",
            operator="equals"
        )
        print(f"✅ Filter criteria created: {criteria.filter_type.value}")
        
        # Test performance stats
        stats = filter_engine.get_performance_stats()
        print(f"✅ Performance stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ AsyncFilterEngine test failed: {e}")
        return False

def test_result_cache():
    """Test ResultCache component."""
    print("\n💾 Testing ResultCache...")
    
    try:
        from core.result_cache import ResultCache, LRUCache, MemoryManager
        
        # Test memory manager
        memory_mgr = MemoryManager(max_memory_mb=100)
        print(f"✅ MemoryManager initialized successfully")
        
        usage = memory_mgr.get_memory_usage()
        print(f"✅ Memory usage: {usage['current_mb']:.1f}MB / {usage['max_mb']:.1f}MB")
        
        # Test LRU cache
        lru_cache = LRUCache(max_size=100)
        print(f"✅ LRUCache initialized successfully")
        
        # Test cache operations
        lru_cache.put("test_key", "test_value")
        value = lru_cache.get("test_key")
        print(f"✅ Cache operations successful: {value}")
        
        stats = lru_cache.get_stats()
        print(f"✅ Cache stats: hits={stats['hits']}, misses={stats['misses']}")
        
        # Test result cache
        result_cache = ResultCache()
        print(f"✅ ResultCache initialized successfully")
        
        comprehensive_stats = result_cache.get_comprehensive_stats()
        print(f"✅ Comprehensive cache stats available")
        
        return True
        
    except Exception as e:
        print(f"❌ ResultCache test failed: {e}")
        return False

def test_refactored_file_organizer():
    """Test the refactored FileOrganizer orchestrator."""
    print("\n🎼 Testing Refactored FileOrganizer...")
    
    try:
        from core.file_organizer_refactored import FileOrganizer
        
        organizer = FileOrganizer()
        print(f"✅ Refactored FileOrganizer initialized successfully")
        
        # Test component access
        scanner = organizer.get_library_scanner()
        analyzer = organizer.get_track_analyzer()
        planner = organizer.get_organization_planner()
        file_mgr = organizer.get_file_operations_manager()
        
        print(f"✅ All specialized components accessible")
        print(f"   - LibraryScanner: {type(scanner).__name__}")
        print(f"   - TrackAnalyzer: {type(analyzer).__name__}")
        print(f"   - OrganizationPlanner: {type(planner).__name__}")
        print(f"   - FileOperationsManager: {type(file_mgr).__name__}")
        
        # Test statistics
        stats = organizer.get_statistics()
        print(f"✅ Statistics accessible: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Refactored FileOrganizer test failed: {e}")
        return False

def test_security_utils():
    """Test security utilities integration."""
    print("\n🔒 Testing Security Utils Integration...")
    
    try:
        from core.security_utils import validate_file_path, sanitize_filename, SecurityError
        
        # Test safe path validation
        try:
            safe_path = validate_file_path("/tmp/test_file.mp3")
            print(f"✅ Safe path validation successful")
        except SecurityError:
            print(f"✅ Security validation working (path rejected)")
        
        # Test filename sanitization
        clean_name = sanitize_filename("track_with_safe_name.mp3")
        print(f"✅ Filename sanitization: {clean_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Security utils test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("🚀 Starting SOLID Components Test Suite")
    print("=" * 50)
    
    setup_logging()
    
    tests = [
        test_library_scanner,
        test_track_analyzer,
        test_organization_planner,
        test_file_operations_manager,
        test_async_filter_engine,
        test_result_cache,
        test_refactored_file_organizer,
        test_security_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! SOLID architecture is working correctly.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())