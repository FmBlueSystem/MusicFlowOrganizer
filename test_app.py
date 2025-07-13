#!/usr/bin/env python3
"""
MusicFlow Organizer Test Script
===============================

Quick test to verify the application can be launched and core modules work.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from core.mixinkey_integration import MixInKeyIntegration
        print("✅ MixInKeyIntegration imported successfully")
        
        from core.genre_classifier import GenreClassifier
        print("✅ GenreClassifier imported successfully")
        
        from core.audio_analyzer import AudioAnalyzer
        print("✅ AudioAnalyzer imported successfully")
        
        from core.file_organizer import FileOrganizer
        print("✅ FileOrganizer imported successfully")
        
        from core.similarity_engine import SimilarityEngine
        print("✅ SimilarityEngine imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_core_functionality():
    """Test basic functionality of core modules."""
    print("\n🧪 Testing core functionality...")
    
    try:
        # Import modules again for testing
        from core.mixinkey_integration import MixInKeyIntegration
        from core.genre_classifier import GenreClassifier
        from core.file_organizer import FileOrganizer
        from core.similarity_engine import SimilarityEngine
        
        # Test MixInKeyIntegration
        mixinkey = MixInKeyIntegration()
        print("✅ MixInKeyIntegration initialized")
        
        # Test GenreClassifier
        classifier = GenreClassifier()
        print("✅ GenreClassifier initialized")
        
        # Test SimilarityEngine
        similarity = SimilarityEngine()
        print("✅ SimilarityEngine initialized")
        
        # Test FileOrganizer
        organizer = FileOrganizer()
        print("✅ FileOrganizer initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

def test_gui_imports():
    """Test GUI module imports."""
    print("\n🖥️ Testing GUI imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6 imported successfully")
        
        from ui.main_window import MusicFlowMainWindow
        print("✅ Main window imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ GUI import error: {e}")
        print("   Run: pip install PySide6")
        return False

def main():
    """Run all tests."""
    print("🎧 MusicFlow Organizer - Application Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test core functionality
    if not test_core_functionality():
        success = False
    
    # Test GUI imports
    if not test_gui_imports():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All tests passed! Application is ready to launch.")
        print("   Run: python main.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("   Install missing dependencies with:")
        print("   pip install -r requirements.txt")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())