"""
Extended Camelot Wheel Implementation
====================================
Professional DJ harmonic mixing with extended compatibility matrix.

References:
- Mixed In Key Camelot Wheel System
- Harmonic mixing theory (Circle of Fifths)
- Schweiger 2025 coherence metrics

Author: Claude Code
Date: 2025-07-12
"""

from typing import Dict, List, Optional, Tuple
import logging

class CamelotWheel:
    """
    Extended Camelot Wheel implementation for professional DJ harmonic mixing.
    
    Provides compatibility scoring for key transitions with extended relationships:
    - Perfect matches (same key)
    - Relative major/minor
    - Adjacent keys (±1 step)
    - Perfect fifth relationships
    - Third minor relationships
    - Submediant relationships
    """
    
    def __init__(self):
        self.logger = logging.getLogger("CamelotWheel")
        
        # Core Camelot Wheel mapping (12 major + 12 minor keys)
        self.camelot_keys = {
            # Major keys (B side)
            '1B': {'key': 'C', 'mode': 'major', 'position': 1},
            '2B': {'key': 'G', 'mode': 'major', 'position': 2},
            '3B': {'key': 'D', 'mode': 'major', 'position': 3},
            '4B': {'key': 'A', 'mode': 'major', 'position': 4},
            '5B': {'key': 'E', 'mode': 'major', 'position': 5},
            '6B': {'key': 'B', 'mode': 'major', 'position': 6},
            '7B': {'key': 'F#', 'mode': 'major', 'position': 7},
            '8B': {'key': 'Db', 'mode': 'major', 'position': 8},
            '9B': {'key': 'Ab', 'mode': 'major', 'position': 9},
            '10B': {'key': 'Eb', 'mode': 'major', 'position': 10},
            '11B': {'key': 'Bb', 'mode': 'major', 'position': 11},
            '12B': {'key': 'F', 'mode': 'major', 'position': 12},
            
            # Minor keys (A side)
            '1A': {'key': 'Am', 'mode': 'minor', 'position': 1},
            '2A': {'key': 'Em', 'mode': 'minor', 'position': 2},
            '3A': {'key': 'Bm', 'mode': 'minor', 'position': 3},
            '4A': {'key': 'F#m', 'mode': 'minor', 'position': 4},
            '5A': {'key': 'C#m', 'mode': 'minor', 'position': 5},
            '6A': {'key': 'G#m', 'mode': 'minor', 'position': 6},
            '7A': {'key': 'D#m', 'mode': 'minor', 'position': 7},
            '8A': {'key': 'Bbm', 'mode': 'minor', 'position': 8},
            '9A': {'key': 'Fm', 'mode': 'minor', 'position': 9},
            '10A': {'key': 'Cm', 'mode': 'minor', 'position': 10},
            '11A': {'key': 'Gm', 'mode': 'minor', 'position': 11},
            '12A': {'key': 'Dm', 'mode': 'minor', 'position': 12},
        }
        
        # Extended compatibility matrix with harmonic relationships
        self._build_compatibility_matrix()
    
    def _build_compatibility_matrix(self):
        """
        Build extended compatibility matrix with weighted harmonic relationships.
        
        Compatibility scores (0.0 to 1.0):
        - 1.0: Perfect match (same key)
        - 0.9: Relative major/minor
        - 0.8: Adjacent keys (±1 step)
        - 0.7: Perfect fifth
        - 0.6: Third minor
        - 0.5: Submediant
        - 0.3: Moderately compatible
        - 0.1: Weakly compatible
        - 0.0: Incompatible
        """
        self.compatibility_matrix = {}
        
        for key1 in self.camelot_keys:
            self.compatibility_matrix[key1] = {}
            
            for key2 in self.camelot_keys:
                score = self._calculate_compatibility_score(key1, key2)
                self.compatibility_matrix[key1][key2] = score
    
    def _calculate_compatibility_score(self, key1: str, key2: str) -> float:
        """
        Calculate harmonic compatibility score between two Camelot keys.
        
        Args:
            key1: Source Camelot key (e.g., '8A')
            key2: Target Camelot key (e.g., '8B')
            
        Returns:
            float: Compatibility score (0.0 to 1.0)
        """
        if key1 == key2:
            return 1.0  # Perfect match
        
        # Extract position and mode
        pos1 = self.camelot_keys[key1]['position']
        mode1 = self.camelot_keys[key1]['mode']
        pos2 = self.camelot_keys[key2]['position']
        mode2 = self.camelot_keys[key2]['mode']
        
        # Relative major/minor (same position, different mode)
        if pos1 == pos2 and mode1 != mode2:
            return 0.9
        
        # Adjacent keys (same mode, ±1 position)
        if mode1 == mode2:
            distance = min(abs(pos1 - pos2), 12 - abs(pos1 - pos2))
            if distance == 1:
                return 0.8  # Adjacent keys
            elif distance == 7:
                return 0.7  # Perfect fifth (7 semitones)
            elif distance == 3:
                return 0.6  # Third minor (3 semitones)
            elif distance == 4:
                return 0.5  # Submediant (4 semitones)
            elif distance <= 2:
                return 0.3  # Moderately compatible
            elif distance <= 3:
                return 0.1  # Weakly compatible
        
        # Cross-mode relationships (different modes, different positions)
        distance = min(abs(pos1 - pos2), 12 - abs(pos1 - pos2))
        if distance <= 1:
            return 0.4  # Close cross-mode
        elif distance <= 2:
            return 0.2  # Moderate cross-mode
        elif distance == 7:
            return 0.3  # Fifth cross-mode
        
        return 0.0  # Incompatible
    
    def get_compatibility_score(self, key1: str, key2: str) -> float:
        """
        Get compatibility score between two Camelot keys.
        
        Args:
            key1: Source Camelot key
            key2: Target Camelot key
            
        Returns:
            float: Compatibility score (0.0 to 1.0)
        """
        if key1 not in self.camelot_keys or key2 not in self.camelot_keys:
            self.logger.warning(f"Invalid Camelot key: {key1} or {key2}")
            return 0.0
        
        return self.compatibility_matrix[key1][key2]
    
    def get_compatible_keys(self, source_key: str, min_score: float = 0.5) -> List[Tuple[str, float]]:
        """
        Get all compatible keys for a source key above minimum score.
        
        Args:
            source_key: Source Camelot key
            min_score: Minimum compatibility score threshold
            
        Returns:
            List[Tuple[str, float]]: List of (key, score) tuples, sorted by score
        """
        if source_key not in self.camelot_keys:
            return []
        
        compatible = [
            (key, score)
            for key, score in self.compatibility_matrix[source_key].items()
            if score >= min_score
        ]
        
        # Sort by compatibility score (descending)
        return sorted(compatible, key=lambda x: x[1], reverse=True)
    
    def get_best_transitions(self, source_key: str, candidate_keys: List[str]) -> List[Tuple[str, float]]:
        """
        Get best transition keys from a list of candidates.
        
        Args:
            source_key: Current track's Camelot key
            candidate_keys: List of candidate keys to evaluate
            
        Returns:
            List[Tuple[str, float]]: Sorted list of (key, score) tuples
        """
        transitions = []
        
        for candidate_key in candidate_keys:
            score = self.get_compatibility_score(source_key, candidate_key)
            if score > 0.0:
                transitions.append((candidate_key, score))
        
        # Sort by compatibility score (descending)
        return sorted(transitions, key=lambda x: x[1], reverse=True)
    
    def validate_camelot_key(self, key: str) -> bool:
        """
        Validate if a string is a valid Camelot key.
        
        Args:
            key: Camelot key to validate
            
        Returns:
            bool: True if valid Camelot key
        """
        return key in self.camelot_keys
    
    def normalize_camelot_key(self, key: str) -> Optional[str]:
        """
        Normalize various key formats to standard Camelot notation.
        
        Args:
            key: Key in various formats (e.g., 'C major', 'Am', '1B')
            
        Returns:
            Optional[str]: Normalized Camelot key or None if unrecognizable
        """
        if not key:
            return None
        
        key = key.strip().upper()
        
        # Already in Camelot format
        if key in self.camelot_keys:
            return key
        
        # Common alternative formats
        key_mappings = {
            # Major keys
            'C MAJOR': '1B', 'C MAJ': '1B', 'C': '1B',
            'G MAJOR': '2B', 'G MAJ': '2B', 'G': '2B',
            'D MAJOR': '3B', 'D MAJ': '3B', 'D': '3B',
            'A MAJOR': '4B', 'A MAJ': '4B', 'A': '4B',
            'E MAJOR': '5B', 'E MAJ': '5B', 'E': '5B',
            'B MAJOR': '6B', 'B MAJ': '6B', 'B': '6B',
            'F# MAJOR': '7B', 'F# MAJ': '7B', 'F#': '7B', 'FS': '7B',
            'DB MAJOR': '8B', 'DB MAJ': '8B', 'DB': '8B', 'C#': '8B',
            'AB MAJOR': '9B', 'AB MAJ': '9B', 'AB': '9B',
            'EB MAJOR': '10B', 'EB MAJ': '10B', 'EB': '10B',
            'BB MAJOR': '11B', 'BB MAJ': '11B', 'BB': '11B',
            'F MAJOR': '12B', 'F MAJ': '12B', 'F': '12B',
            
            # Minor keys
            'A MINOR': '1A', 'A MIN': '1A', 'AM': '1A',
            'E MINOR': '2A', 'E MIN': '2A', 'EM': '2A',
            'B MINOR': '3A', 'B MIN': '3A', 'BM': '3A',
            'F# MINOR': '4A', 'F# MIN': '4A', 'F#M': '4A', 'FSM': '4A',
            'C# MINOR': '5A', 'C# MIN': '5A', 'C#M': '5A',
            'G# MINOR': '6A', 'G# MIN': '6A', 'G#M': '6A',
            'D# MINOR': '7A', 'D# MIN': '7A', 'D#M': '7A',
            'BB MINOR': '8A', 'BB MIN': '8A', 'BBM': '8A',
            'F MINOR': '9A', 'F MIN': '9A', 'FM': '9A',
            'C MINOR': '10A', 'C MIN': '10A', 'CM': '10A',
            'G MINOR': '11A', 'G MIN': '11A', 'GM': '11A',
            'D MINOR': '12A', 'D MIN': '12A', 'DM': '12A',
        }
        
        return key_mappings.get(key)
    
    def get_wheel_visualization(self) -> str:
        """
        Generate ASCII visualization of the Camelot Wheel.
        
        Returns:
            str: ASCII art representation of the wheel
        """
        return '''
        Camelot Wheel (Extended Compatibility)
        =====================================
        
              12A(Dm)    1A(Am)
           11A(Gm)         2A(Em)
        10A(Cm)              3A(Bm)
       9A(Fm)       🎵        4A(F#m)
        8A(Bbm)              5A(C#m)
           7A(D#m)         6A(G#m)
              
              12B(F)     1B(C)
           11B(Bb)         2B(G)
        10B(Eb)              3B(D)
       9B(Ab)       🎶        4B(A)
        8B(Db)               5B(E)
           7B(F#)          6B(B)
        
        Compatibility Scores:
        • 1.0 = Perfect match (same key)
        • 0.9 = Relative major/minor
        • 0.8 = Adjacent keys (±1)
        • 0.7 = Perfect fifth
        • 0.6 = Third minor
        • 0.5 = Submediant
        '''