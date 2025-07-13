#!/usr/bin/env python3
"""
Debug Persistence System
=========================
Sistema de logging detallado para evaluar la persistencia
"""

import logging
import sys
import os
import json
import time
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/musicflow_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_persistence_status():
    """Check current persistence status with detailed logging."""
    logger.info("🔍 CHECKING PERSISTENCE STATUS")
    logger.info("=" * 50)
    
    settings_dir = Path.home() / ".musicflow_organizer"
    cache_file = settings_dir / "analysis_cache.json"
    settings_file = settings_dir / "settings.json"
    
    logger.info(f"📁 Settings directory: {settings_dir}")
    logger.info(f"📁 Directory exists: {settings_dir.exists()}")
    
    # Check settings file
    if settings_file.exists():
        logger.info(f"⚙️  Settings file found: {settings_file}")
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            logger.info(f"📊 Settings content: {json.dumps(settings, indent=2)}")
        except Exception as e:
            logger.error(f"❌ Error reading settings: {e}")
    else:
        logger.warning("📝 No settings file found")
    
    # Check cache file
    if cache_file.exists():
        logger.info(f"💾 Cache file found: {cache_file}")
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            library_path = cache_data.get('library_path', 'Unknown')
            tracks_count = len(cache_data.get('tracks_database', {}))
            cache_timestamp = cache_data.get('cache_timestamp', 0)
            cache_age = time.time() - cache_timestamp
            cache_age_hours = cache_age / 3600
            
            logger.info(f"📊 CACHE DETAILS:")
            logger.info(f"   • Library Path: {library_path}")
            logger.info(f"   • Tracks Count: {tracks_count}")
            logger.info(f"   • Cache Age: {cache_age_hours:.1f} hours")
            logger.info(f"   • App Version: {cache_data.get('app_version', 'Unknown')}")
            
            # Check cache validity
            if cache_age > (7 * 24 * 3600):  # 7 days
                logger.warning("⚠️  Cache is older than 7 days - would be ignored by app")
            else:
                logger.info("✅ Cache is fresh and valid")
            
            if Path(library_path).exists():
                logger.info("✅ Library path still exists")
            else:
                logger.error("❌ Library path no longer exists")
                
        except Exception as e:
            logger.error(f"❌ Error reading cache: {e}")
    else:
        logger.warning("📝 No cache file found - first run will require analysis")
    
    return cache_file.exists()

def monitor_app_startup():
    """Monitor the app startup process."""
    logger.info("\n🚀 MONITORING APP STARTUP PROCESS")
    logger.info("=" * 50)
    
    # Add src to path for importing
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MusicFlowMainWindow
        
        logger.info("📦 Successfully imported MusicFlow components")
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            logger.info("🔧 Created new QApplication instance")
        else:
            logger.info("🔧 Using existing QApplication instance")
        
        # Create main window
        logger.info("🪟 Creating MusicFlowMainWindow...")
        main_window = MusicFlowMainWindow()
        
        logger.info("🎨 Showing main window...")
        main_window.show()
        
        # Log initial UI state
        library_path = main_window.library_path_edit.text()
        analysis_status = main_window.analysis_status.text()
        tracks_count = len(main_window.tracks_database)
        
        logger.info(f"📊 INITIAL UI STATE:")
        logger.info(f"   • Library path field: '{library_path}'")
        logger.info(f"   • Analysis status: '{analysis_status}'")
        logger.info(f"   • Tracks in database: {tracks_count}")
        
        if tracks_count > 0:
            logger.info("✅ SUCCESS: App loaded with cached data - NO RE-ANALYSIS NEEDED")
        else:
            logger.warning("📝 App started empty - will require library analysis")
        
        # Monitor for 30 seconds then exit
        logger.info("⏰ Monitoring app for 30 seconds...")
        
        # Run event loop for a short time
        from PySide6.QtCore import QTimer
        
        def check_status():
            current_tracks = len(main_window.tracks_database)
            current_status = main_window.analysis_status.text()
            logger.info(f"🔄 Status update: {current_tracks} tracks, status: '{current_status}'")
        
        timer = QTimer()
        timer.timeout.connect(check_status)
        timer.start(5000)  # Check every 5 seconds
        
        # Auto-close after 30 seconds
        def auto_close():
            logger.info("⏰ 30 seconds elapsed - closing app")
            final_tracks = len(main_window.tracks_database)
            final_status = main_window.analysis_status.text()
            logger.info(f"📊 FINAL STATE: {final_tracks} tracks, status: '{final_status}'")
            app.quit()
        
        close_timer = QTimer()
        close_timer.timeout.connect(auto_close)
        close_timer.setSingleShot(True)
        close_timer.start(30000)  # 30 seconds
        
        logger.info("🎮 Starting event loop...")
        app.exec()
        
    except Exception as e:
        logger.error(f"❌ Error during app startup monitoring: {e}")
        import traceback
        logger.error(traceback.format_exc())

def create_detailed_log_analysis():
    """Analyze the detailed log for persistence patterns."""
    logger.info("\n📋 CREATING DETAILED LOG ANALYSIS")
    logger.info("=" * 50)
    
    log_file = Path("/tmp/musicflow_debug.log")
    if log_file.exists():
        logger.info(f"📖 Reading log file: {log_file}")
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Analyze key patterns
        patterns_to_check = [
            "load_analysis_data",
            "save_analysis_data", 
            "Successfully loaded analysis data from cache",
            "No cache file found",
            "Cache is too old",
            "Library path no longer exists",
            "Analysis cache cleared",
            "Starting analysis...",
            "Analysis complete"
        ]
        
        logger.info("🔍 Analyzing log patterns:")
        for pattern in patterns_to_check:
            count = log_content.count(pattern)
            if count > 0:
                logger.info(f"   • '{pattern}': {count} occurrences")
        
    else:
        logger.warning("📝 No log file found to analyze")

if __name__ == "__main__":
    print("🎧 MUSICFLOW ORGANIZER - PERSISTENCE DEBUG")
    print("=" * 80)
    print("Este script monitoreará detalladamente el comportamiento de persistencia")
    print("🤖 Generated with Claude Code")
    
    # Step 1: Check current persistence status
    has_cache = check_persistence_status()
    
    # Step 2: Monitor app startup
    monitor_app_startup()
    
    # Step 3: Analyze results
    create_detailed_log_analysis()
    
    print(f"\n📋 LOG LOCATIONS:")
    print(f"• Detailed log: /tmp/musicflow_debug.log")
    print(f"• Console output: Above")
    
    print(f"\n🎯 EXPECTED BEHAVIOR:")
    if has_cache:
        print("✅ App should start with cached data (no re-analysis)")
        print("✅ Library path should be pre-filled")
        print("✅ Results table should show tracks immediately")
    else:
        print("📝 App should start empty (first run)")
        print("📝 User will need to select library and analyze")
        print("📝 After analysis, cache will be created for next run")