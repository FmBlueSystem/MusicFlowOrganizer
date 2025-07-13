"""
File Operations Manager - SRP-compliant component
================================================

Responsible for executing file operations safely with backup and recovery.
Part of the SOLID refactoring of FileOrganizer.

Developed by BlueSystemIO
"""

import os
import shutil
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

from .organization_planner import OrganizationPlan
from .security_utils import is_safe_file_operation, validate_file_path, SecurityError


@dataclass
class OrganizationResult:
    """Result of organization operation."""
    
    success: bool
    files_organized: int
    files_failed: int
    total_time: float
    errors: List[str]
    backup_location: Optional[str] = None
    organization_summary: Dict[str, int] = None
    
    def __post_init__(self):
        if self.organization_summary is None:
            self.organization_summary = {}


class FileOperationsManager:
    """
    Responsible for executing file operations safely with backup and recovery.
    
    Single Responsibility: File operations execution and safety management
    """
    
    def __init__(self):
        """Initialize the file operations manager."""
        self.logger = logging.getLogger(__name__)
    
    def execute_organization(self, plan: OrganizationPlan, dry_run: bool = True) -> OrganizationResult:
        """
        Execute organization plan with safety checks and backup.
        
        Args:
            plan: Organization plan to execute
            dry_run: If True, only simulate the organization
            
        Returns:
            OrganizationResult with execution details
        """
        self.logger.info(f"Executing organization plan (dry_run={dry_run})")
        start_time = time.time()
        
        files_organized = 0
        files_failed = 0
        errors = []
        backup_location = None
        organization_summary = defaultdict(int)
        
        try:
            # Create backup if requested and not dry run
            if plan.create_backup and not dry_run:
                backup_location = self._create_backup(plan.source_directory)
                self.logger.info(f"Backup created at: {backup_location}")
            
            # Create target directory
            if not dry_run:
                Path(plan.target_directory).mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Target directory prepared: {plan.target_directory}")
            
            # Process each file
            for source_path, target_segments in plan.files_to_organize:
                try:
                    # Build full target path
                    target_path = Path(plan.target_directory) / Path(*target_segments)
                    
                    # Perform safety checks
                    if not dry_run:
                        self._validate_file_operation(source_path, str(target_path))
                    
                    if not dry_run:
                        # Create target directory
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Execute file operation
                        if plan.preserve_structure:
                            self._safe_copy(source_path, target_path)
                        else:
                            self._safe_move(source_path, target_path)
                    
                    files_organized += 1
                    
                    # Update summary
                    folder_category = target_segments[0] if target_segments else "Other"
                    organization_summary[folder_category] += 1
                    
                    if files_organized % 100 == 0:
                        self.logger.info(f"Organized {files_organized}/{plan.total_files} files")
                    
                except Exception as e:
                    files_failed += 1
                    error_msg = f"Failed to organize {source_path}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Critical error during organization: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)
        
        execution_time = time.time() - start_time
        
        result = OrganizationResult(
            success=files_failed == 0,
            files_organized=files_organized,
            files_failed=files_failed,
            total_time=execution_time,
            errors=errors,
            backup_location=backup_location,
            organization_summary=dict(organization_summary)
        )
        
        self.logger.info(f"Organization completed: {files_organized} files in {execution_time:.2f}s")
        return result
    
    def restore_from_backup(self, backup_location: str, target_directory: str) -> bool:
        """
        Restore files from backup location.
        
        Args:
            backup_location: Path to backup directory
            target_directory: Directory to restore to
            
        Returns:
            True if restoration was successful
        """
        try:
            self.logger.info(f"Restoring from backup: {backup_location}")
            
            # Validate paths
            validate_file_path(backup_location)
            validate_file_path(target_directory)
            
            # Remove existing target if it exists
            if Path(target_directory).exists():
                shutil.rmtree(target_directory)
            
            # Copy backup to target
            shutil.copytree(backup_location, target_directory)
            
            self.logger.info(f"Restoration completed: {target_directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Restoration failed: {e}")
            return False
    
    def verify_organization(self, plan: OrganizationPlan) -> Dict[str, Any]:
        """
        Verify that organization was completed correctly.
        
        Args:
            plan: Organization plan to verify
            
        Returns:
            Dictionary with verification results
        """
        self.logger.info("Verifying organization")
        
        verification_results = {
            'total_expected': plan.total_files,
            'total_found': 0,
            'missing_files': [],
            'unexpected_files': [],
            'size_verification': True,
            'structure_verification': True
        }
        
        try:
            # Check each expected file
            for source_path, target_segments in plan.files_to_organize:
                target_path = Path(plan.target_directory) / Path(*target_segments)
                
                if target_path.exists():
                    verification_results['total_found'] += 1
                    
                    # Verify file size
                    try:
                        source_size = Path(source_path).stat().st_size if Path(source_path).exists() else 0
                        target_size = target_path.stat().st_size
                        
                        if source_size != target_size and source_size > 0:
                            verification_results['size_verification'] = False
                            
                    except OSError:
                        pass
                else:
                    verification_results['missing_files'].append(str(target_path))
            
            # Check for unexpected files
            if Path(plan.target_directory).exists():
                expected_files = set()
                for _, target_segments in plan.files_to_organize:
                    target_path = Path(plan.target_directory) / Path(*target_segments)
                    expected_files.add(str(target_path))
                
                for root, dirs, files in os.walk(plan.target_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path not in expected_files:
                            verification_results['unexpected_files'].append(file_path)
            
            verification_results['verification_passed'] = (
                verification_results['total_found'] == verification_results['total_expected'] and
                len(verification_results['missing_files']) == 0 and
                verification_results['size_verification'] and
                verification_results['structure_verification']
            )
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            verification_results['verification_error'] = str(e)
            verification_results['verification_passed'] = False
        
        return verification_results
    
    def export_operation_report(self, result: OrganizationResult, plan: OrganizationPlan, output_file: str) -> bool:
        """
        Export organization operation report to JSON file.
        
        Args:
            result: Organization result
            plan: Organization plan that was executed
            output_file: Output file path
            
        Returns:
            True if export was successful
        """
        try:
            report = {
                'timestamp': time.time(),
                'plan_details': {
                    'source_directory': plan.source_directory,
                    'target_directory': plan.target_directory,
                    'scheme': plan.scheme.value,
                    'total_files': plan.total_files,
                    'estimated_size_mb': plan.estimated_size // (1024 * 1024),
                    'preview_mode': plan.preview_mode,
                    'create_backup': plan.create_backup,
                    'preserve_structure': plan.preserve_structure
                },
                'execution_results': {
                    'success': result.success,
                    'files_organized': result.files_organized,
                    'files_failed': result.files_failed,
                    'total_time': result.total_time,
                    'errors': result.errors,
                    'backup_location': result.backup_location,
                    'organization_summary': result.organization_summary
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Operation report exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            return False
    
    def _create_backup(self, source_dir: str) -> str:
        """
        Create backup of source directory.
        
        Args:
            source_dir: Directory to backup
            
        Returns:
            Path to backup directory
        """
        backup_name = f"musicflow_backup_{int(time.time())}"
        backup_path = Path(source_dir).parent / backup_name
        
        self.logger.info(f"Creating backup: {backup_path}")
        
        # Validate paths
        validate_file_path(source_dir)
        
        # Create backup
        shutil.copytree(source_dir, backup_path)
        
        return str(backup_path)
    
    def _validate_file_operation(self, source_path: str, target_path: str):
        """
        Validate that file operation is safe.
        
        Args:
            source_path: Source file path
            target_path: Target file path
            
        Raises:
            SecurityError: If operation is not safe
        """
        try:
            # Use security utils for validation
            is_safe_file_operation(source_path, target_path)
        except SecurityError as e:
            self.logger.error(f"Security validation failed: {e}")
            raise
    
    def _safe_copy(self, source_path: str, target_path: Path):
        """
        Safely copy file with error handling.
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        try:
            shutil.copy2(source_path, target_path)
            self.logger.debug(f"Copied: {source_path} -> {target_path}")
        except Exception as e:
            raise Exception(f"Copy operation failed: {e}")
    
    def _safe_move(self, source_path: str, target_path: Path):
        """
        Safely move file with error handling.
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        try:
            shutil.move(source_path, target_path)
            self.logger.debug(f"Moved: {source_path} -> {target_path}")
        except Exception as e:
            raise Exception(f"Move operation failed: {e}")
