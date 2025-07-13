"""
Refactored File Organization Engine - SOLID Compliant
====================================================

Main orchestrator for music file organization following SOLID principles.
Delegates responsibilities to specialized components:

- LibraryScanner: File discovery
- TrackAnalyzer: Track analysis and database management
- OrganizationPlanner: Organization planning
- FileOperationsManager: File operations execution

Single Responsibility: High-level workflow orchestration

Developed by BlueSystemIO
"""

import logging
import time
from typing import Dict, List, Optional, Any

from .library_scanner import LibraryScanner
from .track_analyzer import TrackAnalyzer, TrackData
from .organization_planner import OrganizationPlanner, OrganizationPlan, OrganizationScheme
from .file_operations_manager import FileOperationsManager, OrganizationResult
from .mixinkey_integration import MixInKeyIntegration


class FileOrganizer:
    """
    SOLID-compliant music file organization orchestrator.
    
    Coordinates specialized components to provide comprehensive
    music library organization functionality.
    
    Single Responsibility: Workflow orchestration and component coordination
    """
    
    def __init__(self):
        """Initialize the file organizer with specialized components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized components (Dependency Injection)
        self.library_scanner = LibraryScanner()
        self.track_analyzer = TrackAnalyzer()
        self.organization_planner = OrganizationPlanner()
        self.file_operations_manager = FileOperationsManager()
        self.mixinkey_integration = MixInKeyIntegration()
        
        # Current organization plan
        self.current_plan: Optional[OrganizationPlan] = None
        
        self.logger.info("FileOrganizer initialized with SOLID architecture")
    
    def find_audio_files(self, library_path: str) -> List[str]:
        """
        Find all audio files in the given directory.
        
        Args:
            library_path: Path to search for audio files
            
        Returns:
            List of audio file paths
        """
        return self.library_scanner.find_audio_files(library_path)
    
    def scan_library(self, library_path: str, use_mixinkey: bool = True) -> Dict[str, Any]:
        """
        Scan music library and build comprehensive track database.
        
        Args:
            library_path: Path to music library
            use_mixinkey: Whether to integrate MixIn Key data
            
        Returns:
            Dictionary with scan results and statistics
        """
        self.logger.info(f"Scanning music library: {library_path}")
        start_time = time.time()
        
        # Step 1: Find all audio files using LibraryScanner
        audio_files = self.library_scanner.find_audio_files(library_path)
        self.logger.info(f"Found {len(audio_files)} audio files")
        
        # Step 2: Load MixIn Key data if available
        mixinkey_tracks = {}
        if use_mixinkey:
            mixinkey_tracks = self.mixinkey_integration.scan_mixinkey_database(library_path)
            self.logger.info(f"Loaded {len(mixinkey_tracks)} tracks with MixIn Key data")
        
        # Step 3: Build tracks database using TrackAnalyzer
        analysis_stats = self.track_analyzer.build_tracks_database(audio_files, mixinkey_tracks)
        
        scan_time = time.time() - start_time
        self.logger.info(f"Library scan completed in {scan_time:.2f}s")
        
        # Combine results
        scan_results = {
            'total_files': len(audio_files),
            'scan_time': scan_time,
            **analysis_stats
        }
        
        return scan_results
    
    def create_organization_plan(self, source_dir: str, target_dir: str, 
                               scheme: OrganizationScheme) -> OrganizationPlan:
        """
        Create organization plan based on selected scheme.
        
        Args:
            source_dir: Source directory with music files
            target_dir: Target directory for organization
            scheme: Organization scheme to use
            
        Returns:
            OrganizationPlan with detailed file movement plan
        """
        self.logger.info(f"Creating organization plan: {scheme.value}")
        
        # Delegate to OrganizationPlanner
        plan = self.organization_planner.create_plan(
            self.track_analyzer.tracks_database,
            source_dir,
            target_dir,
            scheme
        )
        
        self.current_plan = plan
        self.logger.info(f"Organization plan created: {plan.total_files} files")
        
        return plan
    
    def preview_organization(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """
        Preview organization without moving files.
        
        Args:
            plan: Organization plan to preview
            
        Returns:
            Dictionary with preview information
        """
        self.logger.info("Generating organization preview")
        
        # Delegate to OrganizationPlanner
        return self.organization_planner.preview_plan(plan, self.track_analyzer.tracks_database)
    
    def execute_organization(self, plan: OrganizationPlan, 
                           dry_run: bool = True) -> OrganizationResult:
        """
        Execute organization plan.
        
        Args:
            plan: Organization plan to execute
            dry_run: If True, only simulate the organization
            
        Returns:
            OrganizationResult with execution details
        """
        self.logger.info(f"Executing organization plan (dry_run={dry_run})")
        
        # Delegate to FileOperationsManager
        result = self.file_operations_manager.execute_organization(plan, dry_run)
        
        self.logger.info(f"Organization completed: {result.files_organized} files")
        return result
    
    def export_organization_report(self, result: OrganizationResult, 
                                 output_file: str) -> bool:
        """Export organization report to JSON file."""
        if not self.current_plan:
            self.logger.error("No organization plan available for report")
            return False
        
        # Delegate to FileOperationsManager
        return self.file_operations_manager.export_operation_report(
            result, self.current_plan, output_file
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the analyzed library."""
        # Delegate to TrackAnalyzer
        return self.track_analyzer.get_database_statistics()
    
    def get_library_scanner(self) -> LibraryScanner:
        """Get access to the library scanner component."""
        return self.library_scanner
    
    def get_track_analyzer(self) -> TrackAnalyzer:
        """Get access to the track analyzer component."""
        return self.track_analyzer
    
    def get_organization_planner(self) -> OrganizationPlanner:
        """Get access to the organization planner component."""
        return self.organization_planner
    
    def get_file_operations_manager(self) -> FileOperationsManager:
        """Get access to the file operations manager component."""
        return self.file_operations_manager
    
    def verify_organization(self) -> Dict[str, Any]:
        """Verify that organization was completed correctly."""
        if not self.current_plan:
            return {'error': 'No organization plan available for verification'}
        
        return self.file_operations_manager.verify_organization(self.current_plan)
    
    def restore_from_backup(self, backup_location: str, target_directory: str) -> bool:
        """Restore files from backup."""
        return self.file_operations_manager.restore_from_backup(backup_location, target_directory)