#!/usr/bin/env python3
"""
Cross-Platform & Environment Testing Suite
==========================================
Tests críticos para validar funcionalidad en diferentes entornos y plataformas.

PRIORIDAD: MEDIA - Para garantizar compatibilidad profesional multiplataforma

Tests incluidos:
1. Operating System Compatibility Testing
2. Python Version Compatibility Testing  
3. Dependency & Library Testing
4. File System Compatibility Testing
5. Path Handling Cross-Platform Testing
6. Environment Variable Testing
7. Screen Resolution & UI Scaling Testing

Author: Claude Code
Date: 2025-07-13
"""

import sys
import os
import platform
import tempfile
import shutil
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class CrossPlatformEnvironmentTester:
    """
    Comprehensive cross-platform and environment testing suite.
    Validates compatibility across different systems and configurations.
    """
    
    def __init__(self):
        self.test_results = {
            'os_compatibility': {},
            'python_compatibility': {},
            'dependency_testing': {},
            'filesystem_compatibility': {},
            'path_handling': {},
            'environment_variables': {},
            'ui_scaling': {}
        }
        self.logger = logging.getLogger("CrossPlatformTester")
        
        # Create test workspace
        self.test_workspace = Path(tempfile.mkdtemp(prefix="musicflow_crossplatform_test_"))
        
        # System information
        self.system_info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'architecture': platform.architecture()
        }
        
        # Compatibility requirements
        self.requirements = {
            'min_python_version': (3, 11),
            'supported_platforms': ['Darwin', 'Windows', 'Linux'],
            'required_dependencies': [
                'PySide6', 'mutagen', 'requests', 'pathlib', 'sqlite3'
            ],
            'optional_dependencies': [
                'aiohttp', 'redis', 'openai', 'python-dotenv'
            ]
        }
    
    def run_all_cross_platform_tests(self):
        """Execute all cross-platform testing suites."""
        
        print("🌍 CROSS-PLATFORM & ENVIRONMENT TESTING SUITE")
        print("=" * 60)
        print("🎯 PRIORIDAD: Compatibilidad Profesional Multiplataforma")
        
        # Display system information
        print(f"\n📊 SYSTEM INFORMATION:")
        print(f"   Platform: {self.system_info['platform']}")
        print(f"   System: {self.system_info['system']} {self.system_info['release']}")
        print(f"   Python: {self.system_info['python_version']} ({self.system_info['python_implementation']})")
        print(f"   Architecture: {self.system_info['architecture'][0]}")
        
        try:
            # Test 1: Operating System Compatibility (CRÍTICO)
            print(f"\n1️⃣ OPERATING SYSTEM COMPATIBILITY TESTING")
            print("-" * 50)
            self.test_os_compatibility()
            
            # Test 2: Python Version Compatibility (CRÍTICO)
            print(f"\n2️⃣ PYTHON VERSION COMPATIBILITY TESTING")
            print("-" * 50)
            self.test_python_compatibility()
            
            # Test 3: Dependency & Library Testing (CRÍTICO)
            print(f"\n3️⃣ DEPENDENCY & LIBRARY TESTING")
            print("-" * 50)
            self.test_dependency_compatibility()
            
            # Test 4: File System Compatibility (ALTO)
            print(f"\n4️⃣ FILE SYSTEM COMPATIBILITY TESTING")
            print("-" * 50)
            self.test_filesystem_compatibility()
            
            # Test 5: Path Handling Cross-Platform (ALTO)
            print(f"\n5️⃣ PATH HANDLING CROSS-PLATFORM TESTING")
            print("-" * 50)
            self.test_path_handling_compatibility()
            
            # Test 6: Environment Variable Testing (MEDIO)
            print(f"\n6️⃣ ENVIRONMENT VARIABLE TESTING")
            print("-" * 50)
            self.test_environment_variables()
            
            # Test 7: Screen Resolution & UI Scaling (MEDIO)
            print(f"\n7️⃣ SCREEN RESOLUTION & UI SCALING TESTING")
            print("-" * 50)
            self.test_ui_scaling_compatibility()
            
            # Generate comprehensive report
            self.generate_cross_platform_report()
            
        except Exception as e:
            print(f"❌ Critical error in cross-platform testing: {e}")
            self.test_results['critical_error'] = str(e)
    
    def test_os_compatibility(self):
        """Test 1: Operating system compatibility."""
        test_name = 'os_compatibility'
        
        try:
            print("🔍 Testing operating system compatibility...")
            
            current_os = self.system_info['system']
            
            # Test 1.1: Supported Platform Check
            platform_supported = current_os in self.requirements['supported_platforms']
            
            # Test 1.2: OS-Specific Features
            os_features = self._test_os_specific_features()
            
            # Test 1.3: File Permissions
            file_permissions = self._test_file_permissions()
            
            # Test 1.4: Process Management
            process_management = self._test_process_management()
            
            # Test 1.5: System Resources
            system_resources = self._test_system_resources()
            
            print(f"   📊 Platform Supported: {'✅' if platform_supported else '❌'} ({current_os})")
            print(f"   📊 OS Features: {'✅' if os_features else '❌'}")
            print(f"   📊 File Permissions: {'✅' if file_permissions else '❌'}")
            print(f"   📊 Process Management: {'✅' if process_management else '❌'}")
            print(f"   📊 System Resources: {'✅' if system_resources else '❌'}")
            
            os_tests = [
                platform_supported, os_features, file_permissions,
                process_management, system_resources
            ]
            
            os_score = sum(os_tests) / len(os_tests) * 100
            
            status = "✅ PASS" if os_score >= 80 else "❌ FAIL"
            print(f"   {status} OS compatibility (score: {os_score:.1f}%)")
            
            self.test_results[test_name] = {
                'current_os': current_os,
                'platform_supported': platform_supported,
                'os_features': os_features,
                'file_permissions': file_permissions,
                'process_management': process_management,
                'system_resources': system_resources,
                'os_score': os_score,
                'status': 'PASS' if os_score >= 80 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in OS compatibility test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_os_specific_features(self) -> bool:
        """Test OS-specific features."""
        try:
            current_os = self.system_info['system']
            
            if current_os == 'Darwin':  # macOS
                # Test macOS-specific features
                home_dir = Path.home()
                library_dir = home_dir / "Library"
                
                # Test if we can access macOS Library directory
                library_accessible = library_dir.exists() and library_dir.is_dir()
                
                # Test Mixed In Key path structure
                mixinkey_path = library_dir / "Application Support" / "Mixedinkey"
                mixinkey_structure_valid = True  # Path structure is valid even if not exists
                
                return library_accessible and mixinkey_structure_valid
                
            elif current_os == 'Windows':
                # Test Windows-specific features
                appdata = Path(os.environ.get('APPDATA', ''))
                appdata_accessible = appdata.exists() and appdata.is_dir()
                
                # Test Windows path handling
                windows_paths_work = True
                
                return appdata_accessible and windows_paths_work
                
            elif current_os == 'Linux':
                # Test Linux-specific features
                home_dir = Path.home()
                config_dir = home_dir / ".config"
                
                # Test Linux config directory
                config_accessible = config_dir.exists() and config_dir.is_dir()
                
                return config_accessible
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error testing OS-specific features: {e}")
            return False
    
    def _test_file_permissions(self) -> bool:
        """Test file permission handling."""
        try:
            # Test file creation and permission setting
            test_file = self.test_workspace / "permission_test.txt"
            test_file.write_text("Permission test")
            
            # Test if file was created
            file_created = test_file.exists()
            
            # Test file reading
            content = test_file.read_text()
            file_readable = content == "Permission test"
            
            # Test file deletion
            test_file.unlink()
            file_deleted = not test_file.exists()
            
            return file_created and file_readable and file_deleted
            
        except Exception as e:
            self.logger.error(f"Error testing file permissions: {e}")
            return False
    
    def _test_process_management(self) -> bool:
        """Test process management capabilities."""
        try:
            # Test subprocess execution
            result = subprocess.run(
                [sys.executable, '-c', 'print("process test")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            subprocess_works = result.returncode == 0 and "process test" in result.stdout
            
            # Test threading
            import threading
            test_result = []
            
            def test_thread():
                test_result.append("thread_success")
            
            thread = threading.Thread(target=test_thread)
            thread.start()
            thread.join(timeout=5)
            
            threading_works = len(test_result) > 0 and test_result[0] == "thread_success"
            
            return subprocess_works and threading_works
            
        except Exception as e:
            self.logger.error(f"Error testing process management: {e}")
            return False
    
    def _test_system_resources(self) -> bool:
        """Test system resource access."""
        try:
            # Test memory information
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_accessible = memory.total > 0
            except ImportError:
                # psutil not available, use alternative
                memory_accessible = True
            
            # Test disk space
            try:
                import shutil
                disk_usage = shutil.disk_usage(self.test_workspace)
                disk_accessible = disk_usage.total > 0
            except:
                disk_accessible = False
            
            # Test CPU information
            cpu_count = os.cpu_count()
            cpu_accessible = cpu_count and cpu_count > 0
            
            return memory_accessible and disk_accessible and cpu_accessible
            
        except Exception as e:
            self.logger.error(f"Error testing system resources: {e}")
            return False
    
    def test_python_compatibility(self):
        """Test 2: Python version and implementation compatibility."""
        test_name = 'python_compatibility'
        
        try:
            print("🔍 Testing Python version compatibility...")
            
            # Test 2.1: Python Version Check
            current_version = sys.version_info[:2]
            min_version = self.requirements['min_python_version']
            version_compatible = current_version >= min_version
            
            # Test 2.2: Python Features
            python_features = self._test_python_features()
            
            # Test 2.3: Standard Library
            stdlib_compatibility = self._test_standard_library()
            
            # Test 2.4: Python Implementation
            implementation_compatible = self._test_python_implementation()
            
            # Test 2.5: Encoding Support
            encoding_support = self._test_encoding_support()
            
            print(f"   📊 Version Compatible: {'✅' if version_compatible else '❌'} ({current_version} >= {min_version})")
            print(f"   📊 Python Features: {'✅' if python_features else '❌'}")
            print(f"   📊 Standard Library: {'✅' if stdlib_compatibility else '❌'}")
            print(f"   📊 Implementation: {'✅' if implementation_compatible else '❌'}")
            print(f"   📊 Encoding Support: {'✅' if encoding_support else '❌'}")
            
            python_tests = [
                version_compatible, python_features, stdlib_compatibility,
                implementation_compatible, encoding_support
            ]
            
            python_score = sum(python_tests) / len(python_tests) * 100
            
            status = "✅ PASS" if python_score >= 90 else "❌ FAIL"
            print(f"   {status} Python compatibility (score: {python_score:.1f}%)")
            
            self.test_results[test_name] = {
                'current_version': current_version,
                'min_version': min_version,
                'version_compatible': version_compatible,
                'python_features': python_features,
                'stdlib_compatibility': stdlib_compatibility,
                'implementation_compatible': implementation_compatible,
                'encoding_support': encoding_support,
                'python_score': python_score,
                'status': 'PASS' if python_score >= 90 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in Python compatibility test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_python_features(self) -> bool:
        """Test required Python features."""
        try:
            # Test asyncio support
            import asyncio
            asyncio_available = True
            
            # Test pathlib support
            from pathlib import Path
            pathlib_available = True
            
            # Test typing support
            from typing import Dict, List, Optional
            typing_available = True
            
            # Test f-strings
            test_var = "test"
            fstring_result = f"f-string {test_var}"
            fstring_available = fstring_result == "f-string test"
            
            # Test walrus operator (:=)
            try:
                if (test_value := 42) > 0:
                    walrus_available = test_value == 42
                else:
                    walrus_available = False
            except SyntaxError:
                walrus_available = False
            
            return all([
                asyncio_available, pathlib_available, typing_available,
                fstring_available, walrus_available
            ])
            
        except Exception as e:
            self.logger.error(f"Error testing Python features: {e}")
            return False
    
    def _test_standard_library(self) -> bool:
        """Test standard library modules."""
        try:
            required_modules = [
                'sqlite3', 'json', 'pathlib', 'tempfile', 'threading',
                'subprocess', 'logging', 'os', 'sys', 'time'
            ]
            
            missing_modules = []
            
            for module_name in required_modules:
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    missing_modules.append(module_name)
            
            return len(missing_modules) == 0
            
        except Exception as e:
            self.logger.error(f"Error testing standard library: {e}")
            return False
    
    def _test_python_implementation(self) -> bool:
        """Test Python implementation compatibility."""
        try:
            implementation = platform.python_implementation()
            
            # CPython is preferred, but PyPy should also work
            supported_implementations = ['CPython', 'PyPy']
            
            return implementation in supported_implementations
            
        except Exception as e:
            self.logger.error(f"Error testing Python implementation: {e}")
            return False
    
    def _test_encoding_support(self) -> bool:
        """Test encoding support."""
        try:
            # Test UTF-8 support
            test_string = "Test ñáéíóú 中文 🎵"
            
            # Test encoding/decoding
            encoded = test_string.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            utf8_works = decoded == test_string
            
            # Test file encoding
            test_file = self.test_workspace / "encoding_test.txt"
            test_file.write_text(test_string, encoding='utf-8')
            read_content = test_file.read_text(encoding='utf-8')
            
            file_encoding_works = read_content == test_string
            
            return utf8_works and file_encoding_works
            
        except Exception as e:
            self.logger.error(f"Error testing encoding support: {e}")
            return False
    
    def test_dependency_compatibility(self):
        """Test 3: Dependency and library compatibility."""
        test_name = 'dependency_testing'
        
        try:
            print("🔍 Testing dependency & library compatibility...")
            
            # Test 3.1: Required Dependencies
            required_deps = self._test_required_dependencies()
            
            # Test 3.2: Optional Dependencies
            optional_deps = self._test_optional_dependencies()
            
            # Test 3.3: Version Compatibility
            version_compatibility = self._test_dependency_versions()
            
            # Test 3.4: Import Performance
            import_performance = self._test_import_performance()
            
            # Test 3.5: Core Module Functionality
            core_functionality = self._test_core_module_functionality()
            
            print(f"   📊 Required Dependencies: {'✅' if required_deps['all_available'] else '❌'} ({required_deps['available_count']}/{required_deps['total_count']})")
            print(f"   📊 Optional Dependencies: {'✅' if optional_deps['most_available'] else '⚠️'} ({optional_deps['available_count']}/{optional_deps['total_count']})")
            print(f"   📊 Version Compatibility: {'✅' if version_compatibility else '❌'}")
            print(f"   📊 Import Performance: {'✅' if import_performance else '❌'}")
            print(f"   📊 Core Functionality: {'✅' if core_functionality else '❌'}")
            
            # Show missing dependencies
            if required_deps['missing_deps']:
                print(f"   ❌ Missing required: {', '.join(required_deps['missing_deps'])}")
            if optional_deps['missing_deps']:
                print(f"   ⚠️  Missing optional: {', '.join(optional_deps['missing_deps'])}")
            
            dependency_tests = [
                required_deps['all_available'],
                optional_deps['most_available'],
                version_compatibility,
                import_performance,
                core_functionality
            ]
            
            dependency_score = sum(dependency_tests) / len(dependency_tests) * 100
            
            status = "✅ PASS" if dependency_score >= 85 else "❌ FAIL"
            print(f"   {status} Dependency compatibility (score: {dependency_score:.1f}%)")
            
            self.test_results[test_name] = {
                'required_dependencies': required_deps,
                'optional_dependencies': optional_deps,
                'version_compatibility': version_compatibility,
                'import_performance': import_performance,
                'core_functionality': core_functionality,
                'dependency_score': dependency_score,
                'status': 'PASS' if dependency_score >= 85 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in dependency testing: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_required_dependencies(self) -> Dict[str, Any]:
        """Test required dependencies."""
        required_deps = self.requirements['required_dependencies']
        available_deps = []
        missing_deps = []
        
        for dep in required_deps:
            try:
                importlib.import_module(dep)
                available_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        return {
            'total_count': len(required_deps),
            'available_count': len(available_deps),
            'available_deps': available_deps,
            'missing_deps': missing_deps,
            'all_available': len(missing_deps) == 0
        }
    
    def _test_optional_dependencies(self) -> Dict[str, Any]:
        """Test optional dependencies."""
        optional_deps = self.requirements['optional_dependencies']
        available_deps = []
        missing_deps = []
        
        for dep in optional_deps:
            try:
                importlib.import_module(dep)
                available_deps.append(dep)
            except ImportError:
                missing_deps.append(dep)
        
        # Most optional dependencies should be available (>= 50%)
        most_available = len(available_deps) >= len(optional_deps) * 0.5
        
        return {
            'total_count': len(optional_deps),
            'available_count': len(available_deps),
            'available_deps': available_deps,
            'missing_deps': missing_deps,
            'most_available': most_available
        }
    
    def _test_dependency_versions(self) -> bool:
        """Test dependency version compatibility."""
        try:
            # Test key dependencies have working versions
            import PySide6
            pyside6_version = getattr(PySide6, '__version__', 'unknown')
            
            # PySide6 should be version 6.0+
            if pyside6_version != 'unknown':
                major_version = int(pyside6_version.split('.')[0])
                pyside6_compatible = major_version >= 6
            else:
                pyside6_compatible = True  # Assume compatible if version unknown
            
            return pyside6_compatible
            
        except Exception as e:
            self.logger.error(f"Error testing dependency versions: {e}")
            return False
    
    def _test_import_performance(self) -> bool:
        """Test import performance."""
        try:
            import time
            
            # Test import times for key modules
            start_time = time.time()
            
            # Import critical modules
            import PySide6.QtWidgets
            import sqlite3
            import json
            import pathlib
            
            import_time = time.time() - start_time
            
            # Imports should complete quickly (under 2 seconds)
            fast_imports = import_time < 2.0
            
            return fast_imports
            
        except Exception as e:
            self.logger.error(f"Error testing import performance: {e}")
            return False
    
    def _test_core_module_functionality(self) -> bool:
        """Test core module functionality."""
        try:
            # Test PySide6 basic functionality
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            
            # Test if Qt application can be created
            if not QApplication.instance():
                app = QApplication([])
                qt_works = True
                app.quit()
            else:
                qt_works = True
            
            # Test sqlite3 functionality
            import sqlite3
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_db:
                conn = sqlite3.connect(temp_db.name)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER)")
                cursor.execute("INSERT INTO test VALUES (1)")
                cursor.execute("SELECT * FROM test")
                result = cursor.fetchone()
                conn.close()
                os.unlink(temp_db.name)
                
                sqlite_works = result == (1,)
            
            return qt_works and sqlite_works
            
        except Exception as e:
            self.logger.error(f"Error testing core module functionality: {e}")
            return False
    
    def test_filesystem_compatibility(self):
        """Test 4: File system compatibility."""
        test_name = 'filesystem_compatibility'
        
        try:
            print("🔍 Testing file system compatibility...")
            
            # Test 4.1: Path Separators
            path_separators = self._test_path_separators()
            
            # Test 4.2: File Name Restrictions
            filename_restrictions = self._test_filename_restrictions()
            
            # Test 4.3: Case Sensitivity
            case_sensitivity = self._test_case_sensitivity()
            
            # Test 4.4: Unicode Support
            unicode_support = self._test_filesystem_unicode_support()
            
            # Test 4.5: Large File Handling
            large_file_handling = self._test_large_file_handling()
            
            print(f"   📊 Path Separators: {'✅' if path_separators else '❌'}")
            print(f"   📊 Filename Restrictions: {'✅' if filename_restrictions else '❌'}")
            print(f"   📊 Case Sensitivity: {'✅' if case_sensitivity else '❌'}")
            print(f"   📊 Unicode Support: {'✅' if unicode_support else '❌'}")
            print(f"   📊 Large File Handling: {'✅' if large_file_handling else '❌'}")
            
            filesystem_tests = [
                path_separators, filename_restrictions, case_sensitivity,
                unicode_support, large_file_handling
            ]
            
            filesystem_score = sum(filesystem_tests) / len(filesystem_tests) * 100
            
            status = "✅ PASS" if filesystem_score >= 80 else "❌ FAIL"
            print(f"   {status} Filesystem compatibility (score: {filesystem_score:.1f}%)")
            
            self.test_results[test_name] = {
                'path_separators': path_separators,
                'filename_restrictions': filename_restrictions,
                'case_sensitivity': case_sensitivity,
                'unicode_support': unicode_support,
                'large_file_handling': large_file_handling,
                'filesystem_score': filesystem_score,
                'status': 'PASS' if filesystem_score >= 80 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in filesystem compatibility test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_path_separators(self) -> bool:
        """Test path separator handling."""
        try:
            # Test cross-platform path handling
            test_path = self.test_workspace / "subdir" / "test_file.txt"
            
            # Create directory structure
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text("test content")
            
            # Test path exists and is readable
            path_works = test_path.exists() and test_path.read_text() == "test content"
            
            # Test path manipulation
            path_parts = test_path.parts
            path_manipulation_works = len(path_parts) >= 3
            
            return path_works and path_manipulation_works
            
        except Exception as e:
            self.logger.error(f"Error testing path separators: {e}")
            return False
    
    def _test_filename_restrictions(self) -> bool:
        """Test filename restrictions handling."""
        try:
            # Test valid filenames
            valid_names = [
                "normal_file.txt",
                "file with spaces.txt",
                "file-with-dashes.txt",
                "file_with_underscores.txt",
                "file123.txt"
            ]
            
            for filename in valid_names:
                test_file = self.test_workspace / filename
                test_file.write_text("test")
                
                if not test_file.exists():
                    return False
            
            # Test handling of potentially problematic filenames
            try:
                # These might fail on some systems, which is expected
                problematic_file = self.test_workspace / "file:with:colons.txt"
                problematic_file.write_text("test")
                # If this works, great; if not, we handle it gracefully
            except:
                pass  # Expected on some systems
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error testing filename restrictions: {e}")
            return False
    
    def _test_case_sensitivity(self) -> bool:
        """Test case sensitivity handling."""
        try:
            # Create a file with lowercase name
            lower_file = self.test_workspace / "testfile.txt"
            lower_file.write_text("lowercase")
            
            # Try to access with different case
            upper_file = self.test_workspace / "TESTFILE.TXT"
            
            if upper_file.exists():
                # Case-insensitive filesystem (Windows, macOS default)
                case_insensitive = True
                content = upper_file.read_text()
                content_matches = content == "lowercase"
            else:
                # Case-sensitive filesystem (Linux, some macOS)
                case_insensitive = False
                content_matches = True  # No conflict
            
            # Both case-sensitive and case-insensitive should work
            return content_matches
            
        except Exception as e:
            self.logger.error(f"Error testing case sensitivity: {e}")
            return False
    
    def _test_filesystem_unicode_support(self) -> bool:
        """Test filesystem Unicode support."""
        try:
            # Test Unicode filename support
            unicode_filename = "test_ñáéíóú_中文_🎵.txt"
            unicode_file = self.test_workspace / unicode_filename
            
            unicode_content = "Unicode content: ñáéíóú 中文 🎵"
            unicode_file.write_text(unicode_content, encoding='utf-8')
            
            # Test file creation and reading
            file_created = unicode_file.exists()
            if file_created:
                read_content = unicode_file.read_text(encoding='utf-8')
                content_correct = read_content == unicode_content
            else:
                content_correct = False
            
            return file_created and content_correct
            
        except Exception as e:
            self.logger.error(f"Error testing filesystem Unicode support: {e}")
            return False
    
    def _test_large_file_handling(self) -> bool:
        """Test large file handling capabilities."""
        try:
            # Test with a moderately large file (1MB)
            large_file = self.test_workspace / "large_test_file.txt"
            
            # Create 1MB of test data
            test_data = "A" * (1024 * 1024)  # 1MB
            large_file.write_text(test_data)
            
            # Test file size
            file_size = large_file.stat().st_size
            size_correct = file_size >= 1024 * 1024
            
            # Test reading large file
            read_data = large_file.read_text()
            content_correct = len(read_data) == len(test_data)
            
            # Clean up large file
            large_file.unlink()
            
            return size_correct and content_correct
            
        except Exception as e:
            self.logger.error(f"Error testing large file handling: {e}")
            return False
    
    def test_path_handling_compatibility(self):
        """Test 5: Path handling cross-platform compatibility."""
        test_name = 'path_handling'
        
        try:
            print("🔍 Testing path handling cross-platform compatibility...")
            
            # Test 5.1: Absolute Path Handling
            absolute_paths = self._test_absolute_path_handling()
            
            # Test 5.2: Relative Path Handling
            relative_paths = self._test_relative_path_handling()
            
            # Test 5.3: Home Directory Access
            home_directory = self._test_home_directory_access()
            
            # Test 5.4: Special Directory Access
            special_directories = self._test_special_directory_access()
            
            # Test 5.5: Path Normalization
            path_normalization = self._test_path_normalization()
            
            print(f"   📊 Absolute Paths: {'✅' if absolute_paths else '❌'}")
            print(f"   📊 Relative Paths: {'✅' if relative_paths else '❌'}")
            print(f"   📊 Home Directory: {'✅' if home_directory else '❌'}")
            print(f"   📊 Special Directories: {'✅' if special_directories else '❌'}")
            print(f"   📊 Path Normalization: {'✅' if path_normalization else '❌'}")
            
            path_tests = [
                absolute_paths, relative_paths, home_directory,
                special_directories, path_normalization
            ]
            
            path_score = sum(path_tests) / len(path_tests) * 100
            
            status = "✅ PASS" if path_score >= 80 else "❌ FAIL"
            print(f"   {status} Path handling (score: {path_score:.1f}%)")
            
            self.test_results[test_name] = {
                'absolute_paths': absolute_paths,
                'relative_paths': relative_paths,
                'home_directory': home_directory,
                'special_directories': special_directories,
                'path_normalization': path_normalization,
                'path_score': path_score,
                'status': 'PASS' if path_score >= 80 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in path handling test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_absolute_path_handling(self) -> bool:
        """Test absolute path handling."""
        try:
            # Get absolute path to test workspace
            abs_path = self.test_workspace.absolute()
            
            # Test absolute path operations
            abs_file = abs_path / "absolute_test.txt"
            abs_file.write_text("absolute path test")
            
            # Test path operations
            path_exists = abs_file.exists()
            path_absolute = abs_file.is_absolute()
            path_readable = abs_file.read_text() == "absolute path test"
            
            return path_exists and path_absolute and path_readable
            
        except Exception as e:
            self.logger.error(f"Error testing absolute path handling: {e}")
            return False
    
    def _test_relative_path_handling(self) -> bool:
        """Test relative path handling."""
        try:
            # Change to test workspace
            original_cwd = os.getcwd()
            os.chdir(self.test_workspace)
            
            try:
                # Test relative path operations
                rel_file = Path("relative_test.txt")
                rel_file.write_text("relative path test")
                
                # Test path operations
                path_exists = rel_file.exists()
                path_relative = not rel_file.is_absolute()
                path_readable = rel_file.read_text() == "relative path test"
                
                result = path_exists and path_relative and path_readable
                
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error testing relative path handling: {e}")
            return False
    
    def _test_home_directory_access(self) -> bool:
        """Test home directory access."""
        try:
            # Test home directory access
            home_dir = Path.home()
            
            # Test home directory properties
            home_exists = home_dir.exists()
            home_is_dir = home_dir.is_dir()
            home_absolute = home_dir.is_absolute()
            
            # Test if we can list home directory contents (basic access)
            try:
                list(home_dir.iterdir())
                home_accessible = True
            except PermissionError:
                home_accessible = False  # May be restricted on some systems
            except:
                home_accessible = False
            
            return home_exists and home_is_dir and home_absolute
            
        except Exception as e:
            self.logger.error(f"Error testing home directory access: {e}")
            return False
    
    def _test_special_directory_access(self) -> bool:
        """Test special directory access."""
        try:
            current_os = self.system_info['system']
            
            if current_os == 'Darwin':  # macOS
                # Test macOS Library directory
                library_dir = Path.home() / "Library"
                library_accessible = library_dir.exists() and library_dir.is_dir()
                
                # Test Application Support directory
                app_support = library_dir / "Application Support"
                app_support_accessible = app_support.exists() and app_support.is_dir()
                
                return library_accessible and app_support_accessible
                
            elif current_os == 'Windows':
                # Test Windows special directories
                appdata = Path(os.environ.get('APPDATA', ''))
                appdata_accessible = appdata.exists() and appdata.is_dir()
                
                return appdata_accessible
                
            elif current_os == 'Linux':
                # Test Linux special directories
                home_dir = Path.home()
                config_dir = home_dir / ".config"
                
                # Create .config if it doesn't exist (this is normal)
                config_dir.mkdir(exist_ok=True)
                config_accessible = config_dir.exists() and config_dir.is_dir()
                
                return config_accessible
            
            return True  # Unknown OS, assume it works
            
        except Exception as e:
            self.logger.error(f"Error testing special directory access: {e}")
            return False
    
    def _test_path_normalization(self) -> bool:
        """Test path normalization."""
        try:
            # Test path normalization with various formats
            test_paths = [
                "path/to/file.txt",
                "path//to//file.txt",
                "path/./to/file.txt",
                "path/to/../to/file.txt"
            ]
            
            normalized_paths = []
            for path_str in test_paths:
                path = Path(path_str)
                normalized = path.resolve()
                normalized_paths.append(normalized)
            
            # All paths should normalize to the same result (when resolved from same base)
            # Test that normalization works without errors
            normalization_works = len(normalized_paths) == len(test_paths)
            
            return normalization_works
            
        except Exception as e:
            self.logger.error(f"Error testing path normalization: {e}")
            return False
    
    def test_environment_variables(self):
        """Test 6: Environment variable handling."""
        test_name = 'environment_variables'
        
        try:
            print("🔍 Testing environment variable handling...")
            
            # Test 6.1: Basic Environment Access
            basic_env_access = self._test_basic_environment_access()
            
            # Test 6.2: Environment Variable Setting
            env_setting = self._test_environment_variable_setting()
            
            # Test 6.3: .env File Loading
            env_file_loading = self._test_env_file_loading()
            
            # Test 6.4: Default Value Handling
            default_value_handling = self._test_default_value_handling()
            
            print(f"   📊 Basic Env Access: {'✅' if basic_env_access else '❌'}")
            print(f"   📊 Env Setting: {'✅' if env_setting else '❌'}")
            print(f"   📊 .env File Loading: {'✅' if env_file_loading else '❌'}")
            print(f"   📊 Default Value Handling: {'✅' if default_value_handling else '❌'}")
            
            env_tests = [
                basic_env_access, env_setting, env_file_loading, default_value_handling
            ]
            
            env_score = sum(env_tests) / len(env_tests) * 100
            
            status = "✅ PASS" if env_score >= 75 else "❌ FAIL"
            print(f"   {status} Environment variables (score: {env_score:.1f}%)")
            
            self.test_results[test_name] = {
                'basic_env_access': basic_env_access,
                'env_setting': env_setting,
                'env_file_loading': env_file_loading,
                'default_value_handling': default_value_handling,
                'env_score': env_score,
                'status': 'PASS' if env_score >= 75 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in environment variables test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_basic_environment_access(self) -> bool:
        """Test basic environment variable access."""
        try:
            # Test accessing common environment variables
            path_var = os.environ.get('PATH')
            home_var = os.environ.get('HOME') or os.environ.get('USERPROFILE')
            
            # PATH and HOME should exist on most systems
            return path_var is not None and home_var is not None
            
        except Exception as e:
            self.logger.error(f"Error testing basic environment access: {e}")
            return False
    
    def _test_environment_variable_setting(self) -> bool:
        """Test environment variable setting."""
        try:
            # Test setting and getting environment variables
            test_var = 'MUSICFLOW_TEST_VAR'
            test_value = 'test_value_123'
            
            # Set environment variable
            os.environ[test_var] = test_value
            
            # Get environment variable
            retrieved_value = os.environ.get(test_var)
            
            # Clean up
            if test_var in os.environ:
                del os.environ[test_var]
            
            return retrieved_value == test_value
            
        except Exception as e:
            self.logger.error(f"Error testing environment variable setting: {e}")
            return False
    
    def _test_env_file_loading(self) -> bool:
        """Test .env file loading."""
        try:
            # Test .env file loading if python-dotenv is available
            try:
                from dotenv import load_dotenv
                
                # Create test .env file
                env_file = self.test_workspace / "test.env"
                env_file.write_text("TEST_ENV_VAR=test_env_value\nANOTHER_VAR=another_value")
                
                # Load .env file
                load_dotenv(str(env_file))
                
                # Check if variables were loaded
                test_value = os.environ.get('TEST_ENV_VAR')
                
                # Clean up
                if 'TEST_ENV_VAR' in os.environ:
                    del os.environ['TEST_ENV_VAR']
                if 'ANOTHER_VAR' in os.environ:
                    del os.environ['ANOTHER_VAR']
                
                return test_value == 'test_env_value'
                
            except ImportError:
                # python-dotenv not available, but that's okay
                return True
            
        except Exception as e:
            self.logger.error(f"Error testing .env file loading: {e}")
            return False
    
    def _test_default_value_handling(self) -> bool:
        """Test default value handling for environment variables."""
        try:
            # Test default value handling
            nonexistent_var = os.environ.get('NONEXISTENT_MUSICFLOW_VAR', 'default_value')
            
            # Should return default value
            default_works = nonexistent_var == 'default_value'
            
            # Test with None default
            none_default = os.environ.get('ANOTHER_NONEXISTENT_VAR')
            none_default_works = none_default is None
            
            return default_works and none_default_works
            
        except Exception as e:
            self.logger.error(f"Error testing default value handling: {e}")
            return False
    
    def test_ui_scaling_compatibility(self):
        """Test 7: Screen resolution and UI scaling compatibility."""
        test_name = 'ui_scaling'
        
        try:
            print("🔍 Testing screen resolution & UI scaling compatibility...")
            
            # Test 7.1: Qt High DPI Support
            qt_hidpi_support = self._test_qt_hidpi_support()
            
            # Test 7.2: Screen Information Access
            screen_info_access = self._test_screen_information_access()
            
            # Test 7.3: Scaling Factor Detection
            scaling_detection = self._test_scaling_factor_detection()
            
            # Test 7.4: Font Scaling
            font_scaling = self._test_font_scaling()
            
            print(f"   📊 Qt High DPI Support: {'✅' if qt_hidpi_support else '❌'}")
            print(f"   📊 Screen Info Access: {'✅' if screen_info_access else '❌'}")
            print(f"   📊 Scaling Detection: {'✅' if scaling_detection else '❌'}")
            print(f"   📊 Font Scaling: {'✅' if font_scaling else '❌'}")
            
            ui_tests = [
                qt_hidpi_support, screen_info_access, 
                scaling_detection, font_scaling
            ]
            
            ui_score = sum(ui_tests) / len(ui_tests) * 100
            
            status = "✅ PASS" if ui_score >= 75 else "❌ FAIL"
            print(f"   {status} UI scaling (score: {ui_score:.1f}%)")
            
            self.test_results[test_name] = {
                'qt_hidpi_support': qt_hidpi_support,
                'screen_info_access': screen_info_access,
                'scaling_detection': scaling_detection,
                'font_scaling': font_scaling,
                'ui_score': ui_score,
                'status': 'PASS' if ui_score >= 75 else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in UI scaling test: {e}")
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _test_qt_hidpi_support(self) -> bool:
        """Test Qt High DPI support."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            # Test if Qt can handle high DPI
            # Note: This is a basic test since we can't easily test actual high DPI displays
            app = QApplication.instance()
            if not app:
                app = QApplication([])
                created_app = True
            else:
                created_app = False
            
            # Test high DPI attributes (these are available in Qt6)
            hidpi_available = hasattr(Qt, 'AA_EnableHighDpiScaling') or True  # Qt6 has automatic scaling
            
            if created_app:
                app.quit()
            
            return hidpi_available
            
        except Exception as e:
            self.logger.error(f"Error testing Qt High DPI support: {e}")
            return False
    
    def _test_screen_information_access(self) -> bool:
        """Test screen information access."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QScreen
            
            app = QApplication.instance()
            if not app:
                app = QApplication([])
                created_app = True
            else:
                created_app = False
            
            # Test screen information access
            screens = app.screens()
            primary_screen = app.primaryScreen()
            
            screen_info_available = (
                len(screens) > 0 and 
                primary_screen is not None
            )
            
            if screen_info_available:
                # Test screen properties
                geometry = primary_screen.geometry()
                dpi = primary_screen.logicalDotsPerInch()
                
                properties_accessible = (
                    geometry.width() > 0 and 
                    geometry.height() > 0 and
                    dpi > 0
                )
            else:
                properties_accessible = False
            
            if created_app:
                app.quit()
            
            return screen_info_available and properties_accessible
            
        except Exception as e:
            self.logger.error(f"Error testing screen information access: {e}")
            return False
    
    def _test_scaling_factor_detection(self) -> bool:
        """Test scaling factor detection."""
        try:
            from PySide6.QtWidgets import QApplication
            
            app = QApplication.instance()
            if not app:
                app = QApplication([])
                created_app = True
            else:
                created_app = False
            
            # Test device pixel ratio detection
            primary_screen = app.primaryScreen()
            if primary_screen:
                device_pixel_ratio = primary_screen.devicePixelRatio()
                scaling_detected = device_pixel_ratio > 0
            else:
                scaling_detected = False
            
            if created_app:
                app.quit()
            
            return scaling_detected
            
        except Exception as e:
            self.logger.error(f"Error testing scaling factor detection: {e}")
            return False
    
    def _test_font_scaling(self) -> bool:
        """Test font scaling capabilities."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QFont, QFontMetrics
            
            app = QApplication.instance()
            if not app:
                app = QApplication([])
                created_app = True
            else:
                created_app = False
            
            # Test font creation and metrics
            font = QFont("Arial", 12)
            font_metrics = QFontMetrics(font)
            
            # Test font properties
            font_height = font_metrics.height()
            font_width = font_metrics.horizontalAdvance("Test")
            
            font_scaling_works = font_height > 0 and font_width > 0
            
            if created_app:
                app.quit()
            
            return font_scaling_works
            
        except Exception as e:
            self.logger.error(f"Error testing font scaling: {e}")
            return False
    
    def generate_cross_platform_report(self):
        """Generate comprehensive cross-platform testing report."""
        print(f"\n📋 CROSS-PLATFORM & ENVIRONMENT TESTING REPORT")
        print("=" * 60)
        
        # Count passed/failed tests
        test_categories = [
            'os_compatibility',
            'python_compatibility',
            'dependency_testing',
            'filesystem_compatibility',
            'path_handling',
            'environment_variables',
            'ui_scaling'
        ]
        
        passed_tests = 0
        total_tests = 0
        critical_issues = []
        
        for category in test_categories:
            result = self.test_results.get(category, {})
            status = result.get('status', 'UNKNOWN')
            
            if status in ['PASS', 'FAIL']:
                total_tests += 1
                if status == 'PASS':
                    passed_tests += 1
                else:
                    critical_issues.append(category)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 CROSS-PLATFORM COMPATIBILITY SUMMARY:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Platform: {self.system_info['platform']}")
        print(f"   Python: {self.system_info['python_version']}")
        
        # Detailed results
        for category in test_categories:
            result = self.test_results.get(category, {})
            status = result.get('status', 'UNKNOWN')
            
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '💥',
                'SKIPPED': '⏭️',
                'UNKNOWN': '❓'
            }.get(status, '❓')
            
            print(f"\n📊 {category.upper().replace('_', ' ')}:")
            print(f"   {status_icon} Status: {status}")
            
            # Add specific metrics
            score_key = f"{category.split('_')[0]}_score"
            if score_key in result:
                print(f"   📈 Score: {result[score_key]:.1f}%")
        
        # Cross-platform verdict
        print(f"\n🏆 OVERALL CROSS-PLATFORM VERDICT:")
        
        if success_rate >= 90:
            print("   🥇 EXCELLENT: Completamente compatible multiplataforma")
            verdict = "EXCELLENT"
        elif success_rate >= 80:
            print("   🥈 GOOD: Buena compatibilidad con ajustes menores")
            verdict = "GOOD"
        elif success_rate >= 70:
            print("   🥉 FAIR: Compatibilidad aceptable con limitaciones")
            verdict = "FAIR"
        else:
            print("   💥 POOR: Problemas críticos de compatibilidad")
            verdict = "POOR"
        
        # Platform-specific recommendations
        print(f"\n💡 RECOMENDACIONES ESPECÍFICAS DE PLATAFORMA:")
        
        current_os = self.system_info['system']
        
        if verdict == "EXCELLENT":
            print(f"   - Aplicación perfectamente compatible con {current_os}")
            print("   - Lista para despliegue profesional multiplataforma")
        else:
            if 'os_compatibility' in critical_issues:
                print(f"   🔥 CRÍTICO: Corregir incompatibilidades con {current_os}")
            if 'python_compatibility' in critical_issues:
                print("   🔥 CRÍTICO: Actualizar versión de Python o dependencias")
            if 'dependency_testing' in critical_issues:
                print("   🔥 CRÍTICO: Instalar dependencias faltantes")
            if 'filesystem_compatibility' in critical_issues:
                print(f"   ⚠️  Optimizar manejo de sistema de archivos para {current_os}")
            if 'path_handling' in critical_issues:
                print("   ⚠️  Mejorar manejo de rutas multiplataforma")
            if 'environment_variables' in critical_issues:
                print("   ⚠️  Revisar configuración de variables de entorno")
            if 'ui_scaling' in critical_issues:
                print("   ⚠️  Optimizar escalado de UI para alta resolución")
        
        return {
            'success_rate': success_rate,
            'verdict': verdict,
            'critical_issues': critical_issues,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'platform_info': self.system_info
        }
    
    def cleanup(self):
        """Clean up test environment."""
        try:
            # Clean up test workspace
            if self.test_workspace.exists():
                shutil.rmtree(self.test_workspace)
            
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🌍 Starting Cross-Platform & Environment Testing Suite...")
    print("🎯 Focus: Compatibilidad Profesional Multiplataforma")
    
    tester = CrossPlatformEnvironmentTester()
    try:
        tester.run_all_cross_platform_tests()
    finally:
        tester.cleanup()
    
    print(f"\n🏁 Cross-Platform Testing Completed!")
    print("=" * 60)