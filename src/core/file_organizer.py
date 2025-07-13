"""
Professional File Organization Engine for MusicFlow Organizer
=============================================================

Intelligent music file organization based on:
- MixIn Key analysis data integration
- DJ best practices and workflow optimization
- Genre classification and harmonic mixing
- Safe file operations with backup and preview
- Multiple organization schemes (genre, BPM, energy, key)

Built following professional DJ standards for music library management.
"""

import os
import shutil
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time
from collections import defaultdict

from .mixinkey_integration import MixInKeyIntegration, MixInKeyTrackData
from .genre_classifier import GenreClassifier, GenreClassificationResult
from .audio_analyzer import AudioAnalyzer, AudioAnalysisResult


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


class FileOrganizer:
    """
    Professional music file organization engine.
    
    Provides intelligent organization based on MixIn Key analysis,
    genre classification, and DJ best practices.
    """
    
    # Supported audio file extensions
    AUDIO_EXTENSIONS = {
        '.mp3', '.flac', '.wav', '.aiff', '.m4a', '.ogg', 
        '.wma', '.aac', '.opus', '.alac'
    }
    
    # DJ software playlist extensions to preserve
    PLAYLIST_EXTENSIONS = {
        '.m3u', '.m3u8', '.pls', '.cue', '.nml', '.xml'
    }
    
    def __init__(self):
        """Initialize the file organizer."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize analysis components
        self.mixinkey_integration = MixInKeyIntegration()
        self.genre_classifier = GenreClassifier()
        self.audio_analyzer = AudioAnalyzer()
        
        # Organization state
        self.tracks_database = {}
        self.organization_plan = None
        self.dry_run_mode = True
        
        self.logger.info("FileOrganizer initialized")
    
    def find_audio_files(self, library_path: str) -> List[str]:
        """
        Find all audio files in the given directory.
        
        Args:
            library_path: Path to search for audio files
            
        Returns:
            List of audio file paths
        """
        return self._find_audio_files(library_path)
    
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
        
        # Find all audio files
        audio_files = self._find_audio_files(library_path)
        self.logger.info(f"Found {len(audio_files)} audio files")
        
        # Load MixIn Key data if available
        mixinkey_tracks = {}
        if use_mixinkey:
            mixinkey_tracks = self.mixinkey_integration.scan_mixinkey_database(library_path)
            self.logger.info(f"Loaded {len(mixinkey_tracks)} tracks with MixIn Key data")
        
        # Process each audio file
        self.tracks_database = {}
        processed_count = 0
        
        for file_path in audio_files:
            # Get MixIn Key data if available
            mixinkey_data = mixinkey_tracks.get(file_path)
            
            # Perform audio analysis if no MixIn Key data
            if not mixinkey_data:
                try:
                    analysis_result = self.audio_analyzer.analyze_file(file_path)
                    if analysis_result.success:
                        # Convert to MixInKeyTrackData format
                        mixinkey_data = MixInKeyTrackData(
                            file_path=file_path,
                            filename=Path(file_path).name,
                            bpm=analysis_result.bpm,
                            key=analysis_result.key,
                            energy=int(analysis_result.energy_level * 10) if analysis_result.energy_level else None,
                            duration=analysis_result.duration,
                            analyzed_by_mixinkey=False
                        )
                except Exception as e:
                    self.logger.warning(f"Failed to analyze {file_path}: {e}")
                    continue
            
            # Perform genre classification
            if mixinkey_data:
                # Create AudioAnalysisResult from MixIn Key data
                analysis_result = AudioAnalysisResult(
                    file_path=file_path,
                    duration=mixinkey_data.duration or 0,
                    sample_rate=44100,  # Default
                    bpm=mixinkey_data.bpm,
                    key=mixinkey_data.key,
                    energy_level=mixinkey_data.energy / 10 if mixinkey_data.energy else None
                )
                
                genre_result = self.genre_classifier.classify_genre(analysis_result)
                
                # Store combined data
                self.tracks_database[file_path] = {
                    'mixinkey_data': mixinkey_data,
                    'genre_classification': genre_result,
                    'analysis_result': analysis_result
                }
                
                processed_count += 1
                
                if processed_count % 100 == 0:
                    self.logger.info(f"Processed {processed_count}/{len(audio_files)} files")
        
        scan_time = time.time() - start_time
        self.logger.info(f"Library scan completed in {scan_time:.2f}s")
        
        return {
            'total_files': len(audio_files),
            'processed_files': processed_count,
            'mixinkey_analyzed': len([t for t in self.tracks_database.values() 
                                   if t['mixinkey_data'].analyzed_by_mixinkey]),
            'scan_time': scan_time,
            'tracks_database': self.tracks_database
        }
    
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
        
        files_to_organize = []
        total_size = 0
        
        for file_path, track_data in self.tracks_database.items():
            mixinkey_data = track_data['mixinkey_data']
            genre_result = track_data['genre_classification']
            analysis_result = track_data['analysis_result']
            
            # Generate target path based on scheme
            target_path_segments = self._get_target_path(
                scheme, mixinkey_data, genre_result, analysis_result
            )
            
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
        
        self.organization_plan = plan
        self.logger.info(f"Organization plan created: {len(files_to_organize)} files")
        
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
            track_data = self.tracks_database.get(source_path, {})
            genre_result = track_data.get('genre_classification')
            mixinkey_data = track_data.get('mixinkey_data')
            
            if genre_result:
                genre_distribution[genre_result.primary_genre] += 1
            
            if mixinkey_data:
                if mixinkey_data.bpm:
                    bpm_range = f"{int(mixinkey_data.bpm // 10) * 10}-{int(mixinkey_data.bpm // 10) * 10 + 9}"
                    bpm_distribution[bpm_range] += 1
                
                if mixinkey_data.key:
                    key_distribution[mixinkey_data.key] += 1
        
        return {
            'folder_structure': dict(folder_structure),
            'total_folders': len(folder_structure),
            'genre_distribution': dict(genre_distribution),
            'bpm_distribution': dict(bpm_distribution),
            'key_distribution': dict(key_distribution),
            'estimated_size_mb': plan.estimated_size // (1024 * 1024),
            'total_files': plan.total_files
        }
    
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
        start_time = time.time()
        
        files_organized = 0
        files_failed = 0
        errors = []
        backup_location = None
        organization_summary = defaultdict(int)
        
        # Create backup if requested and not dry run
        if plan.create_backup and not dry_run:
            backup_location = self._create_backup(plan.source_directory)
        
        # Create target directory
        if not dry_run:
            Path(plan.target_directory).mkdir(parents=True, exist_ok=True)
        
        # Process each file
        for source_path, target_segments in plan.files_to_organize:
            try:
                # Build full target path
                target_path = Path(plan.target_directory) / Path(*target_segments)
                
                if not dry_run:
                    # Create target directory
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy or move file
                    if plan.preserve_structure:
                        shutil.copy2(source_path, target_path)
                    else:
                        shutil.move(source_path, target_path)
                
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
    
    def _find_audio_files(self, directory: str) -> List[str]:
        """Find all audio files in directory recursively."""
        audio_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in self.AUDIO_EXTENSIONS:
                    audio_files.append(os.path.join(root, file))
        
        return audio_files
    
    def _get_target_path(self, scheme: OrganizationScheme, 
                        mixinkey_data: MixInKeyTrackData,
                        genre_result: GenreClassificationResult,
                        analysis_result: AudioAnalysisResult) -> List[str]:
        """Generate target path segments based on organization scheme."""
        
        if scheme == OrganizationScheme.BY_GENRE:
            return self._get_genre_path(genre_result, analysis_result)
        
        elif scheme == OrganizationScheme.BY_BPM:
            return self._get_bpm_path(mixinkey_data)
        
        elif scheme == OrganizationScheme.BY_KEY:
            return self._get_key_path(mixinkey_data)
        
        elif scheme == OrganizationScheme.BY_ENERGY:
            return self._get_energy_path(mixinkey_data, genre_result)
        
        elif scheme == OrganizationScheme.BY_YEAR:
            return self._get_year_path(mixinkey_data)
        
        elif scheme == OrganizationScheme.DJ_WORKFLOW:
            return self._get_dj_workflow_path(mixinkey_data, genre_result, analysis_result)
        
        else:
            # Fallback
            return ["Other", mixinkey_data.filename]
    
    def _get_genre_path(self, genre_result: GenreClassificationResult, 
                       analysis_result: AudioAnalysisResult) -> List[str]:
        """Generate genre-based path."""
        path = self.genre_classifier.get_organization_path(genre_result, analysis_result)
        path.append(Path(analysis_result.file_path).name)
        return path
    
    def _get_bpm_path(self, mixinkey_data: MixInKeyTrackData) -> List[str]:
        """Generate BPM-based path."""
        if not mixinkey_data.bpm:
            return ["Unknown BPM", mixinkey_data.filename]
        
        bpm = int(mixinkey_data.bpm)
        bpm_range = f"{(bpm // 10) * 10}-{(bpm // 10) * 10 + 9} BPM"
        
        return ["By BPM", bpm_range, mixinkey_data.filename]
    
    def _get_key_path(self, mixinkey_data: MixInKeyTrackData) -> List[str]:
        """Generate key-based path."""
        if not mixinkey_data.key:
            return ["Unknown Key", mixinkey_data.filename]
        
        # Get note name from Camelot notation
        camelot_wheel = self.mixinkey_integration.CAMELOT_WHEEL
        note_info = camelot_wheel.get(mixinkey_data.key, {})
        note_name = note_info.get('note', 'Unknown')
        
        key_folder = f"{mixinkey_data.key} - {note_name}"
        
        return ["By Key", key_folder, mixinkey_data.filename]
    
    def _get_energy_path(self, mixinkey_data: MixInKeyTrackData, 
                        genre_result: GenreClassificationResult) -> List[str]:
        """Generate energy-based path."""
        energy_category = genre_result.energy_category if genre_result else "Medium Energy"
        return ["By Energy", energy_category, mixinkey_data.filename]
    
    def _get_year_path(self, mixinkey_data: MixInKeyTrackData) -> List[str]:
        """Generate year-based path."""
        year = mixinkey_data.year if mixinkey_data.year else "Unknown Year"
        return ["By Year", str(year), mixinkey_data.filename]
    
    def _get_dj_workflow_path(self, mixinkey_data: MixInKeyTrackData,
                            genre_result: GenreClassificationResult,
                            analysis_result: AudioAnalysisResult) -> List[str]:
        """Generate comprehensive DJ workflow path."""
        path = []
        
        # Primary genre organization
        if genre_result and genre_result.primary_genre:
            # Find main category
            main_category = None
            for category, genres in self.genre_classifier.GENRE_HIERARCHY.items():
                if genre_result.primary_genre in genres:
                    main_category = category
                    break
            
            if main_category:
                path.append(main_category)
                path.append(genre_result.primary_genre)
                
                # Add sub-genre if available
                if genre_result.sub_genre:
                    path.append(genre_result.sub_genre)
            else:
                path.extend(["Other", genre_result.primary_genre])
        else:
            path.append("Unclassified")
        
        # Add BPM range for electronic music
        if (len(path) > 0 and path[0] == "Electronic" and 
            mixinkey_data.bpm):
            bpm = int(mixinkey_data.bpm)
            bpm_range = f"{(bpm // 5) * 5}-{(bpm // 5) * 5 + 4} BPM"
            path.append(bpm_range)
        
        path.append(mixinkey_data.filename)
        return path
    
    def _create_backup(self, source_dir: str) -> str:
        """Create backup of source directory."""
        backup_name = f"backup_{int(time.time())}"
        backup_path = Path(source_dir).parent / backup_name
        
        self.logger.info(f"Creating backup: {backup_path}")
        shutil.copytree(source_dir, backup_path)
        
        return str(backup_path)
    
    def export_organization_report(self, result: OrganizationResult, 
                                 output_file: str) -> bool:
        """Export organization report to JSON file."""
        try:
            report = {
                'timestamp': time.time(),
                'success': result.success,
                'files_organized': result.files_organized,
                'files_failed': result.files_failed,
                'total_time': result.total_time,
                'errors': result.errors,
                'backup_location': result.backup_location,
                'organization_summary': result.organization_summary,
                'scheme_used': self.organization_plan.scheme.value if self.organization_plan else None
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Organization report exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the analyzed library."""
        if not self.tracks_database:
            return {}
        
        total_tracks = len(self.tracks_database)
        mixinkey_analyzed = len([t for t in self.tracks_database.values() 
                               if t['mixinkey_data'].analyzed_by_mixinkey])
        
        # Genre distribution
        genres = {}
        bpms = []
        keys = {}
        
        for track_data in self.tracks_database.values():
            genre_result = track_data.get('genre_classification')
            mixinkey_data = track_data.get('mixinkey_data')
            
            if genre_result and genre_result.primary_genre:
                genres[genre_result.primary_genre] = genres.get(genre_result.primary_genre, 0) + 1
            
            if mixinkey_data:
                if mixinkey_data.bpm:
                    bpms.append(mixinkey_data.bpm)
                if mixinkey_data.key:
                    keys[mixinkey_data.key] = keys.get(mixinkey_data.key, 0) + 1
        
        return {
            'total_tracks': total_tracks,
            'mixinkey_analyzed': mixinkey_analyzed,
            'genre_distribution': genres,
            'average_bpm': sum(bpms) / len(bpms) if bpms else 0,
            'key_distribution': keys,
            'most_common_genre': max(genres, key=genres.get) if genres else None,
            'most_common_key': max(keys, key=keys.get) if keys else None
        }