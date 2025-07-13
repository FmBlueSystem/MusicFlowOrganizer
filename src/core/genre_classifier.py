"""
Advanced Genre Classification System for MusicFlow Organizer
===========================================================

Professional genre classification based on:
- Audio feature analysis (MFCC, spectral features, rhythm)
- BPM and tempo patterns
- Energy levels and dynamics
- DJ mixing compatibility rules
- Machine learning models for accuracy

Built following professional DJ best practices and genre mixing guidelines.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - using rule-based classification")

from .audio_analyzer import AudioAnalysisResult


@dataclass
class GenreClassificationResult:
    """Result of genre classification analysis."""
    
    primary_genre: str
    confidence: float
    sub_genre: Optional[str] = None
    similar_genres: List[str] = None
    energy_category: str = "Medium Energy"
    mixable_genres: List[str] = None
    bpm_category: str = "Unknown"
    mood_tags: List[str] = None
    
    def __post_init__(self):
        if self.similar_genres is None:
            self.similar_genres = []
        if self.mixable_genres is None:
            self.mixable_genres = []
        if self.mood_tags is None:
            self.mood_tags = []


class GenreClassifier:
    """
    Professional genre classification system for DJ applications.
    
    Combines audio analysis with DJ mixing knowledge to provide
    accurate genre classification and compatibility recommendations.
    """
    
    # Professional DJ genre hierarchy based on mixing compatibility
    GENRE_HIERARCHY = {
        "Electronic": {
            "House": {
                "subgenres": ["Deep House", "Tech House", "Progressive House", 
                             "Future House", "Tropical House", "Afro House"],
                "bpm_range": (120, 132),
                "energy_range": (0.4, 0.8),
                "mixable_with": ["Techno", "Trance", "Disco"]
            },
            "Techno": {
                "subgenres": ["Minimal Techno", "Hard Techno", "Dub Techno", 
                             "Industrial Techno", "Acid Techno", "Detroit Techno"],
                "bpm_range": (125, 150),
                "energy_range": (0.6, 1.0),
                "mixable_with": ["House", "Hardcore", "Industrial"]
            },
            "Trance": {
                "subgenres": ["Progressive Trance", "Uplifting Trance", "Psytrance", 
                             "Tech Trance", "Vocal Trance", "Balearic Trance"],
                "bpm_range": (128, 138),
                "energy_range": (0.5, 0.9),
                "mixable_with": ["House", "Progressive"]
            },
            "Drum & Bass": {
                "subgenres": ["Liquid DnB", "Neurofunk", "Jump Up", 
                             "Hardcore DnB", "Jungle", "Breakbeat"],
                "bpm_range": (160, 180),
                "energy_range": (0.7, 1.0),
                "mixable_with": ["Jungle", "Hardcore", "Breakbeat"]
            },
            "Dubstep": {
                "subgenres": ["Brostep", "Future Bass", "Melodic Dubstep", 
                             "Riddim", "Deep Dubstep"],
                "bpm_range": (140, 150),
                "energy_range": (0.6, 1.0),
                "mixable_with": ["Bass Music", "Trap", "Future Bass"]
            }
        },
        "Hip Hop": {
            "Rap": {
                "subgenres": ["Trap", "Boom Bap", "Conscious Rap", 
                             "Gangsta Rap", "Alternative Hip Hop"],
                "bpm_range": (70, 140),
                "energy_range": (0.3, 0.8),
                "mixable_with": ["R&B", "Trap", "Electronic"]
            },
            "Trap": {
                "subgenres": ["Hard Trap", "Melodic Trap", "Future Trap"],
                "bpm_range": (130, 160),
                "energy_range": (0.6, 0.9),
                "mixable_with": ["Hip Hop", "Electronic", "Bass Music"]
            }
        },
        "Rock": {
            "Alternative": {
                "subgenres": ["Indie Rock", "Art Rock", "Post Rock"],
                "bpm_range": (100, 140),
                "energy_range": (0.4, 0.8),
                "mixable_with": ["Pop", "Electronic Rock"]
            },
            "Hard Rock": {
                "subgenres": ["Metal", "Punk", "Grunge"],
                "bpm_range": (120, 160),
                "energy_range": (0.7, 1.0),
                "mixable_with": ["Metal", "Industrial"]
            }
        },
        "Pop": {
            "Commercial Pop": {
                "subgenres": ["Dance Pop", "Electro Pop", "Indie Pop"],
                "bpm_range": (100, 130),
                "energy_range": (0.4, 0.7),
                "mixable_with": ["House", "Electronic", "R&B"]
            }
        },
        "Ambient": {
            "Chill": {
                "subgenres": ["Chillout", "Downtempo", "Lo-Fi"],
                "bpm_range": (60, 100),
                "energy_range": (0.1, 0.4),
                "mixable_with": ["Deep House", "Ambient"]
            }
        }
    }
    
    # BPM-based genre hints
    BPM_GENRE_HINTS = {
        (60, 100): ["Ambient", "Chill", "Downtempo"],
        (100, 115): ["Hip Hop", "R&B", "Pop"],
        (115, 125): ["Deep House", "Disco", "Funk"],
        (125, 132): ["House", "Tech House", "Progressive House"],
        (132, 140): ["Trance", "Progressive Trance", "Techno"],
        (140, 150): ["Hard Techno", "Dubstep", "Hardstyle"],
        (150, 180): ["Drum & Bass", "Hardcore", "Jungle"],
        (180, 200): ["Speedcore", "Happy Hardcore"]
    }
    
    # Audio feature patterns for genre recognition
    GENRE_AUDIO_PATTERNS = {
        "House": {
            "spectral_centroid_range": (1000, 4000),
            "energy_range": (0.4, 0.8),
            "rhythm_pattern": "four_on_floor"
        },
        "Techno": {
            "spectral_centroid_range": (1500, 5000),
            "energy_range": (0.6, 1.0),
            "rhythm_pattern": "industrial"
        },
        "Hip Hop": {
            "spectral_centroid_range": (800, 3000),
            "energy_range": (0.3, 0.7),
            "rhythm_pattern": "syncopated"
        },
        "Ambient": {
            "spectral_centroid_range": (500, 2000),
            "energy_range": (0.1, 0.3),
            "rhythm_pattern": "minimal"
        }
    }
    
    def __init__(self):
        """Initialize the genre classifier."""
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.ml_model = None
        
        # Load or create similarity matrix
        self.similarity_matrix = self._build_similarity_matrix()
        
        self.logger.info("GenreClassifier initialized")
    
    def classify_genre(self, analysis_result: AudioAnalysisResult) -> GenreClassificationResult:
        """
        Classify genre based on comprehensive audio analysis.
        
        Args:
            analysis_result: Result from AudioAnalyzer
            
        Returns:
            GenreClassificationResult with primary genre and recommendations
        """
        try:
            # Start with rule-based classification
            primary_genre, confidence = self._rule_based_classification(analysis_result)
            
            # Get sub-genre based on audio features
            sub_genre = self._classify_subgenre(primary_genre, analysis_result)
            
            # Find similar and mixable genres
            similar_genres = self._find_similar_genres(primary_genre, analysis_result)
            mixable_genres = self._find_mixable_genres(primary_genre, analysis_result)
            
            # Categorize energy and BPM
            energy_category = self._categorize_energy(analysis_result.energy_level)
            bpm_category = self._categorize_bpm(analysis_result.bpm)
            
            # Extract mood tags
            mood_tags = self._extract_mood_tags(analysis_result)
            
            return GenreClassificationResult(
                primary_genre=primary_genre,
                confidence=confidence,
                sub_genre=sub_genre,
                similar_genres=similar_genres,
                energy_category=energy_category,
                mixable_genres=mixable_genres,
                bpm_category=bpm_category,
                mood_tags=mood_tags
            )
            
        except Exception as e:
            self.logger.error(f"Genre classification failed: {e}")
            return GenreClassificationResult(
                primary_genre="Unknown",
                confidence=0.0
            )
    
    def _rule_based_classification(self, analysis: AudioAnalysisResult) -> Tuple[str, float]:
        """Classify genre using rule-based approach."""
        scores = {}
        
        # BPM-based scoring
        if analysis.bpm:
            for bpm_range, genres in self.BPM_GENRE_HINTS.items():
                if bpm_range[0] <= analysis.bpm <= bpm_range[1]:
                    for genre in genres:
                        scores[genre] = scores.get(genre, 0) + 0.3
        
        # Energy-based scoring
        if analysis.energy_level is not None:
            for main_genre, subgenres in self.GENRE_HIERARCHY.items():
                for genre, info in subgenres.items():
                    energy_range = info.get("energy_range", (0, 1))
                    if energy_range[0] <= analysis.energy_level <= energy_range[1]:
                        scores[genre] = scores.get(genre, 0) + 0.25
        
        # Spectral feature scoring
        if analysis.spectral_centroid:
            for genre, pattern in self.GENRE_AUDIO_PATTERNS.items():
                centroid_range = pattern.get("spectral_centroid_range", (0, 10000))
                if centroid_range[0] <= analysis.spectral_centroid <= centroid_range[1]:
                    scores[genre] = scores.get(genre, 0) + 0.2
        
        # Mood-based hints
        if analysis.mood:
            mood_genre_hints = {
                "aggressive": ["Hard Techno", "Metal", "Hardcore"],
                "energetic": ["House", "Techno", "Trance"],
                "upbeat": ["Pop", "Dance Pop", "Commercial Pop"],
                "mellow": ["Deep House", "Ambient", "Chill"],
                "chill": ["Ambient", "Downtempo", "Lo-Fi"]
            }
            
            for genre in mood_genre_hints.get(analysis.mood, []):
                scores[genre] = scores.get(genre, 0) + 0.15
        
        # MFCC-based classification (if available)
        if analysis.mfcc_features and SKLEARN_AVAILABLE:
            ml_genre, ml_confidence = self._ml_classification(analysis.mfcc_features)
            if ml_genre:
                scores[ml_genre] = scores.get(ml_genre, 0) + ml_confidence * 0.1
        
        # Find best match
        if scores:
            best_genre = max(scores, key=scores.get)
            confidence = min(scores[best_genre], 1.0)
            return best_genre, confidence
        
        # Fallback based on BPM
        if analysis.bpm:
            if analysis.bpm < 100:
                return "Ambient", 0.5
            elif analysis.bpm < 120:
                return "Hip Hop", 0.5
            elif analysis.bpm < 135:
                return "House", 0.5
            elif analysis.bpm < 150:
                return "Techno", 0.5
            else:
                return "Drum & Bass", 0.5
        
        return "Unknown", 0.0
    
    def _classify_subgenre(self, primary_genre: str, analysis: AudioAnalysisResult) -> Optional[str]:
        """Classify sub-genre within the primary genre."""
        # Find the main category for this genre
        for main_category, genres in self.GENRE_HIERARCHY.items():
            if primary_genre in genres:
                genre_info = genres[primary_genre]
                subgenres = genre_info.get("subgenres", [])
                
                if not subgenres:
                    return None
                
                # Use energy level and BPM to pick sub-genre
                if analysis.energy_level is not None and analysis.bpm:
                    # Simple heuristic: higher energy = more intense sub-genre
                    if analysis.energy_level > 0.7:
                        # Pick more intense sub-genres
                        intense_subgenres = [s for s in subgenres if any(
                            word in s.lower() for word in ["hard", "industrial", "acid", "hardcore"]
                        )]
                        if intense_subgenres:
                            return intense_subgenres[0]
                    
                    elif analysis.energy_level < 0.4:
                        # Pick mellower sub-genres
                        mellow_subgenres = [s for s in subgenres if any(
                            word in s.lower() for word in ["deep", "minimal", "ambient", "chill"]
                        )]
                        if mellow_subgenres:
                            return mellow_subgenres[0]
                
                # Default to first sub-genre
                return subgenres[0] if subgenres else None
        
        return None
    
    def _find_similar_genres(self, primary_genre: str, analysis: AudioAnalysisResult) -> List[str]:
        """Find genres similar to the primary genre."""
        similar = []
        
        # Use similarity matrix
        if primary_genre in self.similarity_matrix:
            similar.extend(self.similarity_matrix[primary_genre][:3])  # Top 3 similar
        
        # BPM-based similarity
        if analysis.bpm:
            tolerance = 10
            for bpm_range, genres in self.BPM_GENRE_HINTS.items():
                if (bpm_range[0] - tolerance <= analysis.bpm <= bpm_range[1] + tolerance):
                    similar.extend([g for g in genres if g != primary_genre])
        
        # Remove duplicates and limit
        return list(dict.fromkeys(similar))[:5]
    
    def _find_mixable_genres(self, primary_genre: str, analysis: AudioAnalysisResult) -> List[str]:
        """Find genres that mix well with the primary genre."""
        mixable = []
        
        # Look up mixable genres from hierarchy
        for main_category, genres in self.GENRE_HIERARCHY.items():
            if primary_genre in genres:
                genre_info = genres[primary_genre]
                mixable.extend(genre_info.get("mixable_with", []))
        
        # BPM compatibility
        if analysis.bpm:
            for bpm_range, genres in self.BPM_GENRE_HINTS.items():
                # Check if BPMs are mixable (within 6 BPM or double/half tempo)
                for test_bpm in [bpm_range[0], bpm_range[1]]:
                    if (abs(analysis.bpm - test_bpm) <= 6 or 
                        abs(analysis.bpm - test_bpm * 2) <= 6 or 
                        abs(analysis.bpm * 2 - test_bpm) <= 6):
                        mixable.extend([g for g in genres if g != primary_genre])
        
        # Remove duplicates
        return list(dict.fromkeys(mixable))[:5]
    
    def _categorize_energy(self, energy_level: Optional[float]) -> str:
        """Categorize energy level."""
        if energy_level is None:
            return "Unknown Energy"
        
        if energy_level >= 0.8:
            return "High Energy"
        elif energy_level >= 0.5:
            return "Medium Energy"
        else:
            return "Low Energy"
    
    def _categorize_bpm(self, bpm: Optional[float]) -> str:
        """Categorize BPM range."""
        if bpm is None:
            return "Unknown BPM"
        
        if bpm < 100:
            return "Slow (< 100 BPM)"
        elif bpm < 120:
            return "Medium (100-120 BPM)"
        elif bpm < 140:
            return "Fast (120-140 BPM)"
        else:
            return "Very Fast (140+ BPM)"
    
    def _extract_mood_tags(self, analysis: AudioAnalysisResult) -> List[str]:
        """Extract mood tags from analysis."""
        tags = []
        
        # Energy-based tags
        if analysis.energy_level is not None:
            if analysis.energy_level > 0.8:
                tags.extend(["energetic", "intense", "powerful"])
            elif analysis.energy_level > 0.5:
                tags.extend(["upbeat", "driving", "dynamic"])
            else:
                tags.extend(["chill", "relaxed", "mellow"])
        
        # BPM-based tags
        if analysis.bpm:
            if analysis.bpm > 140:
                tags.append("fast")
            elif analysis.bpm < 100:
                tags.append("slow")
        
        # Mood from analysis
        if analysis.mood:
            tags.append(analysis.mood)
        
        return list(set(tags))  # Remove duplicates
    
    def _ml_classification(self, mfcc_features: List[float]) -> Tuple[Optional[str], float]:
        """Classify using machine learning model (if available)."""
        if not SKLEARN_AVAILABLE or not self.ml_model:
            return None, 0.0
        
        try:
            # This would use a pre-trained model
            # For now, return placeholder
            return None, 0.0
        except Exception:
            return None, 0.0
    
    def _build_similarity_matrix(self) -> Dict[str, List[str]]:
        """Build genre similarity matrix based on DJ mixing knowledge."""
        return {
            "House": ["Tech House", "Deep House", "Progressive House", "Techno", "Disco"],
            "Techno": ["Tech House", "Minimal Techno", "Industrial", "Hard Techno", "House"],
            "Trance": ["Progressive Trance", "House", "Progressive House", "Uplifting Trance"],
            "Hip Hop": ["Trap", "R&B", "Rap", "Alternative Hip Hop"],
            "Trap": ["Hip Hop", "Future Bass", "Electronic", "Bass Music"],
            "Drum & Bass": ["Jungle", "Breakbeat", "Hardcore", "Neurofunk"],
            "Dubstep": ["Future Bass", "Trap", "Bass Music", "Electronic"],
            "Ambient": ["Chill", "Downtempo", "Deep House", "Minimal"],
            "Pop": ["Dance Pop", "Electronic", "House", "Commercial Pop"],
            "Rock": ["Alternative", "Electronic Rock", "Industrial"],
        }
    
    def get_organization_path(self, classification: GenreClassificationResult, 
                            analysis: AudioAnalysisResult) -> List[str]:
        """
        Get the folder path for organizing this track.
        
        Returns:
            List of folder names from root to final location
        """
        path = []
        
        # Find main category
        main_category = None
        for category, genres in self.GENRE_HIERARCHY.items():
            if classification.primary_genre in genres:
                main_category = category
                break
        
        if main_category:
            path.append(main_category)
            path.append(classification.primary_genre)
            
            # Add sub-genre if available
            if classification.sub_genre:
                path.append(classification.sub_genre)
            
            # Add BPM range for dance music
            if main_category == "Electronic" and analysis.bpm:
                bpm_folder = f"{int(analysis.bpm)}BPM"
                path.append(bpm_folder)
        else:
            # Fallback organization
            path = ["Other", classification.primary_genre or "Unknown"]
        
        return path
    
    def get_energy_organization_path(self, classification: GenreClassificationResult) -> List[str]:
        """Get organization path based on energy level."""
        return ["By Energy", classification.energy_category]
    
    def get_bpm_organization_path(self, analysis: AudioAnalysisResult) -> List[str]:
        """Get organization path based on BPM."""
        if not analysis.bpm:
            return ["By BPM", "Unknown BPM"]
        
        # Create BPM ranges
        bpm = int(analysis.bpm)
        bpm_range = f"{(bpm // 10) * 10}-{(bpm // 10) * 10 + 9} BPM"
        
        return ["By BPM", bpm_range]