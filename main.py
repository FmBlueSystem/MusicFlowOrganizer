#!/usr/bin/env python3
"""
MusicFlow Organizer - Professional Music Library Organization Tool for DJs
========================================================================

A powerful application that analyzes music libraries recursively and organizes them
according to professional DJ best practices using AI-powered genre classification,
BPM analysis, key detection, and intelligent similarity grouping.

Features:
• Recursive directory scanning with metadata extraction
• Advanced genre classification and similarity detection
• BPM and key analysis for harmonic mixing
• Energy level and mood classification
• Smart folder structure based on DJ best practices
• Preview mode before reorganization
• Support for all major audio formats

Created by BlueSystemIO, Freddy Molina
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont, QFontDatabase

def setup_application():
    """Initialize the application with proper settings."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MusicFlow Organizer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BlueSystemIO")
    app.setOrganizationDomain("bluesystemio.com")
    
    # Enable high DPI scaling (only if attributes exist and not deprecated)
    # Note: These attributes are deprecated in Qt6 and automatic high DPI is default
    
    # Set application icon
    icon_path = Path(__file__).parent / "assets" / "icon.icns"
    if icon_path.exists():
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app

def main():
    """Main application entry point."""
    print("🎧 MusicFlow Organizer v1.0")
    print("=" * 60)
    print("Professional Music Library Organization Tool for DJs")
    print("Intelligent genre classification • BPM analysis • Smart organization")
    print()
    print("Features:")
    print("🔍 Recursive directory scanning with metadata extraction")
    print("🎵 Advanced genre classification and similarity detection") 
    print("⚡ BPM and key analysis for harmonic mixing")
    print("📊 Energy level and mood classification")
    print("📁 Smart folder structure based on DJ best practices")
    print("👁️ Preview mode before reorganization")
    print("🎶 Support for all major audio formats")
    print()
    print("🤖 Generated with Claude Code")
    print("Co-Authored-By: Claude <noreply@anthropic.com>")
    print("=" * 60)
    
    # Create application
    app = setup_application()
    
    try:
        # Import and create main window
        from ui.main_window import MusicFlowMainWindow
        window = MusicFlowMainWindow()
        window.show()
        
        print("🚀 MusicFlow Organizer launched successfully!")
        print("💡 Workflow: Scan → Analyze → Preview → Organize")
        print("📂 Start by selecting your music library folder")
        print("⚙️ Configure organization preferences in Settings")
        print("🎯 Preview organization before applying changes")
        print("Created by BlueSystemIO, Freddy Molina")
        
        # Run application
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install PySide6 librosa mutagen scikit-learn essentia-tensorflow")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())