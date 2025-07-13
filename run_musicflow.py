#!/usr/bin/env python3
"""
MusicFlow Organizer Launcher - Virtual Environment Optimized
===========================================================

Optimized launcher for MusicFlow Organizer in virtual environment.
Automatically detects and configures the environment for best performance.

Usage:
    python run_musicflow.py                    # Launch GUI
    python run_musicflow.py --demo             # Run demo
    python run_musicflow.py --test             # Run tests
    python run_musicflow.py --console          # Console mode

Developed by BlueSystemIO
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(PROJECT_ROOT / "musicflow.log")
        ]
    )

def check_environment():
    """Check and validate the Python environment."""
    print("🔍 Checking Environment...")
    
    # Check Python version
    if sys.version_info < (3.8, 0):
        print(f"❌ Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check virtual environment
    venv_active = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if venv_active:
        print("✅ Virtual environment active")
    else:
        print("⚠️  Running outside virtual environment")
    
    # Check critical dependencies
    missing_deps = []
    
    try:
        import PySide6
        print(f"✅ PySide6 {PySide6.__version__}")
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import sklearn
        print(f"✅ Scikit-learn {sklearn.__version__}")
    except ImportError:
        missing_deps.append("scikit-learn")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install PySide6 numpy scikit-learn")
        return False
    
    return True

def launch_gui():
    """Launch the main GUI application."""
    print("🚀 Launching MusicFlow Organizer GUI...")
    
    try:
        # Import GUI components
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from ui.main_window import MainWindow
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("MusicFlow Organizer")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("BlueSystemIO")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("✅ GUI launched successfully")
        print("📝 Check musicflow.log for detailed logs")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

def run_demo():
    """Run the SOLID architecture demo."""
    print("🎼 Running MusicFlow Organizer Demo...")
    
    try:
        # Import and run demo
        from demo_virtual_env import main as demo_main
        return demo_main()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1

def run_tests():
    """Run the test suite."""
    print("🧪 Running MusicFlow Organizer Tests...")
    
    try:
        # Import and run tests
        from test_solid_components import main as test_main
        return test_main()
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return 1

def run_console():
    """Run in console mode for advanced users."""
    print("💻 MusicFlow Organizer Console Mode")
    print("=" * 40)
    
    try:
        # Import SOLID components
        from core.file_organizer_refactored import FileOrganizer
        from core.organization_planner import OrganizationScheme
        
        # Create organizer
        organizer = FileOrganizer()
        print("✅ FileOrganizer initialized")
        
        # Interactive console
        print("\\nAvailable commands:")
        print("  organizer.scan_library('/path/to/music')")
        print("  organizer.get_statistics()")
        print("  organizer.find_audio_files('/path')")
        print("  list(OrganizationScheme) # Show schemes")
        print("\\nType 'exit()' to quit")
        
        # Add to local namespace for interactive use
        import code
        local_vars = {
            'organizer': organizer,
            'OrganizationScheme': OrganizationScheme,
            'Path': Path
        }
        
        console = code.InteractiveConsole(locals=local_vars)
        console.interact()
        
        return 0
        
    except Exception as e:
        print(f"❌ Console mode failed: {e}")
        return 1

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="MusicFlow Organizer - Professional DJ Music Library Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_musicflow.py                    # Launch GUI
  python run_musicflow.py --demo             # Run demo
  python run_musicflow.py --test             # Run tests
  python run_musicflow.py --console          # Interactive console
  python run_musicflow.py --gui --verbose    # GUI with verbose logging
        """
    )
    
    parser.add_argument('--gui', action='store_true', default=True,
                       help='Launch GUI application (default)')
    parser.add_argument('--demo', action='store_true',
                       help='Run SOLID architecture demo')
    parser.add_argument('--test', action='store_true',
                       help='Run test suite')
    parser.add_argument('--console', action='store_true',
                       help='Launch interactive console')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--no-env-check', action='store_true',
                       help='Skip environment validation')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Header
    print("🎼 MusicFlow Organizer v2.0 - SOLID Architecture")
    print("=" * 55)
    print("Professional Music Library Organization Tool for DJs")
    print("Developed by BlueSystemIO")
    print("")
    
    # Environment check
    if not args.no_env_check:
        if not check_environment():
            print("\\n❌ Environment check failed")
            return 1
        print("")
    
    # Route to appropriate function
    try:
        if args.demo:
            return run_demo()
        elif args.test:
            return run_tests()
        elif args.console:
            return run_console()
        else:
            # Default to GUI
            return launch_gui()
            
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
        return 0
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\\nExited with code: {exit_code}")
    sys.exit(exit_code)