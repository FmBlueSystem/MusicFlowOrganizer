"""
Organization Planning Engine - SRP-compliant component
=====================================================

Responsible for creating and managing file organization plans.
Part of the SOLID refactoring of FileOrganizer.

Developed by BlueSystemIO
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from .track_analyzer import TrackData
from .mixinkey_integration import MixInKeyTrackData
from .genre_classifier import GenreClassificationResult
from .audio_analyzer import AudioAnalysisResult


class OrganizationScheme(Enum):
    """Available organization schemes."""
    BY_GENRE = "by_genre"
    BY_BPM = "by_bpm"
    BY_KEY = "by_key"
    BY_ENERGY = "by_energy"
    BY_YEAR = "by_year"
    DJ_WORKFLOW = "dj_workflow"  # Comprehensive DJ-friendly structure


@dataclass
class OrganizationPlan:
    """Plan for organizing a music library."""
    
    source_directory: str
    target_directory: str
    scheme: OrganizationScheme
    files_to_organize: List[Tuple[str, List[str]]]  # (source_path, target_path_segments)
    total_files: int
    estimated_size: int
    preview_mode: bool = True
    create_backup: bool = True
    preserve_structure: bool = False


class OrganizationPlanner:
    """
    Responsible for creating organization plans based on track data.
    
    Single Responsibility: Organization planning and path generation
    """
    
    def __init__(self):
        """Initialize the organization planner."""
        self.logger = logging.getLogger(__name__)
    
    def create_plan(self, tracks_database: Dict[str, TrackData], 
                   source_dir: str, target_dir: str, 
                   scheme: OrganizationScheme) -> OrganizationPlan:
        """
        Create organization plan based on tracks database and scheme.
        
        Args:
            tracks_database: Dictionary of track data
            source_dir: Source directory with music files
            target_dir: Target directory for organization
            scheme: Organization scheme to use
            
        Returns:
            OrganizationPlan with detailed file movement plan
        """
        self.logger.info(f"Creating organization plan: {scheme.value}")
        
        files_to_organize = []
        total_size = 0
        
        for file_path, track_data in tracks_database.items():
            # Generate target path based on scheme
            target_path_segments = self._get_target_path(scheme, track_data)
            files_to_organize.append((file_path, target_path_segments))
            
            # Calculate file size
            try:
                total_size += Path(file_path).stat().st_size
            except OSError:
                pass
        
        plan = OrganizationPlan(
            source_directory=source_dir,
            target_directory=target_dir,
            scheme=scheme,
            files_to_organize=files_to_organize,
            total_files=len(files_to_organize),
            estimated_size=total_size
        )
        
        self.logger.info(f"Organization plan created: {len(files_to_organize)} files")
        return plan
    
    def preview_plan(self, plan: OrganizationPlan, tracks_database: Dict[str, TrackData]) -> Dict[str, Any]:
        """
        Generate preview of organization plan without moving files.
        
        Args:
            plan: Organization plan to preview
            tracks_database: Track data for statistics
            
        Returns:
            Dictionary with preview information
        """
        self.logger.info("Generating organization preview")
        
        folder_structure = defaultdict(list)
        genre_distribution = defaultdict(int)
        bpm_distribution = defaultdict(int)
        key_distribution = defaultdict(int)
        
        for source_path, target_segments in plan.files_to_organize:
            # Build folder structure
            folder_path = "/".join(target_segments[:-1])  # Exclude filename
            filename = target_segments[-1]
            folder_structure[folder_path].append(filename)
            
            # Get track data for statistics
            track_data = tracks_database.get(source_path)
            if track_data:
                # Genre distribution
                if track_data.genre_classification:
                    genre_distribution[track_data.genre_classification.primary_genre] += 1
                
                # BPM and key distribution
                if track_data.mixinkey_data:
                    if track_data.mixinkey_data.bpm:
                        bpm_range = f"{int(track_data.mixinkey_data.bpm // 10) * 10}-{int(track_data.mixinkey_data.bpm // 10) * 10 + 9}"
                        bmp_distribution[bpm_range] += 1
                    
                    if track_data.mixinkey_data.key:
                        key_distribution[track_data.mixinkey_data.key] += 1
        
        return {
            'folder_structure': dict(folder_structure),
            'total_folders': len(folder_structure),
            'genre_distribution': dict(genre_distribution),
            'bpm_distribution': dict(bpm_distribution),
            'key_distribution': dict(key_distribution),
            'estimated_size_mb': plan.estimated_size // (1024 * 1024),
            'total_files': plan.total_files
        }
    
    def _get_target_path(self, scheme: OrganizationScheme, track_data: TrackData) -> List[str]:
        """
        Generate target path segments based on organization scheme.
        
        Args:
            scheme: Organization scheme
            track_data: Track data
            
        Returns:
            List of path segments
        """
        if scheme == OrganizationScheme.BY_GENRE:
            return self._get_genre_path(track_data)
        
        elif scheme == OrganizationScheme.BY_BPM:
            return self._get_bpm_path(track_data)
        
        elif scheme == OrganizationScheme.BY_KEY:
            return self._get_key_path(track_data)
        
        elif scheme == OrganizationScheme.BY_ENERGY:
            return self._get_energy_path(track_data)
        
        elif scheme == OrganizationScheme.BY_YEAR:
            return self._get_year_path(track_data)
        
        elif scheme == OrganizationScheme.DJ_WORKFLOW:
            return self._get_dj_workflow_path(track_data)
        
        else:
            # Fallback
            return ["Other", Path(track_data.file_path).name]
    
    def _get_genre_path(self, track_data: TrackData) -> List[str]:
        """Generate genre-based path."""
        if track_data.genre_classification and track_data.analysis_result:
            # Use genre classifier's organization path
            from .genre_classifier import GenreClassifier
            genre_classifier = GenreClassifier()
            path = genre_classifier.get_organization_path(
                track_data.genre_classification, 
                track_data.analysis_result
            )
            path.append(Path(track_data.file_path).name)
            return path
        else:
            return ["Unclassified", Path(track_data.file_path).name]
    
    def _get_bpm_path(self, track_data: TrackData) -> List[str]:
        """Generate BPM-based path."""
        if track_data.mixinkey_data and track_data.mixinkey_data.bpm:
            bpm = int(track_data.mixinkey_data.bpm)
            bpm_range = f"{(bpm // 10) * 10}-{(bpm // 10) * 10 + 9} BPM"
            return ["By BPM", bpm_range, Path(track_data.file_path).name]
        else:
            return ["Unknown BPM", Path(track_data.file_path).name]
    
    def _get_key_path(self, track_data: TrackData) -> List[str]:
        """Generate key-based path."""
        if track_data.mixinkey_data and track_data.mixinkey_data.key:
            key = track_data.mixinkey_data.key
            # Get note name from Camelot notation if available
            from .mixinkey_integration import MixInKeyIntegration
            mixinkey = MixInKeyIntegration()
            camelot_wheel = mixinkey.CAMELOT_WHEEL
            note_info = camelot_wheel.get(key, {})
            note_name = note_info.get('note', 'Unknown')
            
            key_folder = f"{key} - {note_name}"
            return ["By Key", key_folder, Path(track_data.file_path).name]
        else:
            return ["Unknown Key", Path(track_data.file_path).name]
    
    def _get_energy_path(self, track_data: TrackData) -> List[str]:
        """Generate energy-based path."""
        if track_data.genre_classification:
            energy_category = track_data.genre_classification.energy_category or "Medium Energy"
        else:
            energy_category = "Unknown Energy"
        
        return ["By Energy", energy_category, Path(track_data.file_path).name]
    
    def _get_year_path(self, track_data: TrackData) -> List[str]:
        """Generate year-based path."""
        if track_data.mixinkey_data and track_data.mixinkey_data.year:
            year = str(track_data.mixinkey_data.year)
        else:
            year = "Unknown Year"
        
        return ["By Year", year, Path(track_data.file_path).name]
    
    def _get_dj_workflow_path(self, track_data: TrackData) -> List[str]:
        """Generate comprehensive DJ workflow path."""
        path = []
        
        # Primary genre organization
        if track_data.genre_classification and track_data.genre_classification.primary_genre:
            # Find main category
            from .genre_classifier import GenreClassifier
            genre_classifier = GenreClassifier()
            
            main_category = None
            for category, genres in genre_classifier.GENRE_HIERARCHY.items():
                if track_data.genre_classification.primary_genre in genres:
                    main_category = category
                    break
            
            if main_category:
                path.append(main_category)
                path.append(track_data.genre_classification.primary_genre)
                
                # Add sub-genre if available
                if track_data.genre_classification.sub_genre:
                    path.append(track_data.genre_classification.sub_genre)
            else:
                path.extend(["Other", track_data.genre_classification.primary_genre])
        else:
            path.append("Unclassified")
        
        # Add BPM range for electronic music
        if (len(path) > 0 and path[0] == "Electronic" and 
            track_data.mixinkey_data and track_data.mixinkey_data.bpm):
            bpm = int(track_data.mixinkey_data.bpm)
            bpm_range = f"{(bpm // 5) * 5}-{(bpm // 5) * 5 + 4} BPM"
            path.append(bpm_range)
        
        path.append(Path(track_data.file_path).name)
        return path
