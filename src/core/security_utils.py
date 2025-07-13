"""
Security utilities for MusicFlow Organizer
==========================================

Provides security validation functions for file paths, input sanitization,
and other security-critical operations.

Developed by BlueSystemIO
"""

import os
import re
from pathlib import Path
from typing import Union, List


class SecurityError(Exception):
    """Exception raised for security violations."""
    pass


def validate_file_path(file_path: Union[str, Path], allowed_base_paths: List[str] = None) -> Path:
    """
    Validate and sanitize file paths to prevent path traversal attacks.
    
    Args:
        file_path: Path to validate
        allowed_base_paths: List of allowed base directories (optional)
        
    Returns:
        Sanitized Path object
        
    Raises:
        SecurityError: If path is invalid or contains security risks
    """
    if not file_path:
        raise SecurityError("Empty file path provided")
    
    # Convert to Path object
    try:
        path = Path(file_path)
    except (TypeError, ValueError) as e:
        raise SecurityError(f"Invalid path format: {e}")
    
    # Check for null bytes (common in path traversal attacks)
    if '\0' in str(file_path):
        raise SecurityError("Path contains null bytes")
    
    # Check for dangerous characters
    dangerous_chars = ['|', ';', '&', '$', '>', '<', '`']
    if any(char in str(file_path) for char in dangerous_chars):
        raise SecurityError(f"Path contains dangerous characters: {file_path}")
    
    # Resolve path to handle .. and . components
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError) as e:
        raise SecurityError(f"Cannot resolve path: {e}")
    
    # Check for path traversal attempts
    if '..' in path.parts:
        raise SecurityError("Path traversal detected (..) in path")
    
    # If allowed base paths are specified, ensure path is within them
    if allowed_base_paths:
        path_str = str(resolved_path)
        allowed = False
        for base_path in allowed_base_paths:
            try:
                base_resolved = Path(base_path).resolve()
                if path_str.startswith(str(base_resolved)):
                    allowed = True
                    break
            except (OSError, RuntimeError):
                continue
        
        if not allowed:
            raise SecurityError(f"Path outside allowed directories: {file_path}")
    
    return resolved_path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        raise SecurityError("Empty filename provided")
    
    # Remove or replace dangerous characters
    # Keep alphanumeric, spaces, dots, hyphens, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s\.\-_]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty after sanitization
    if not sanitized:
        raise SecurityError("Filename becomes empty after sanitization")
    
    # Check for reserved Windows filenames
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if sanitized.upper() in reserved_names:
        sanitized = f"_{sanitized}"
    
    return sanitized


def validate_database_query_params(params: tuple) -> tuple:
    """
    Validate parameters for database queries to prevent injection.
    
    Args:
        params: Query parameters tuple
        
    Returns:
        Validated parameters
        
    Raises:
        SecurityError: If parameters contain dangerous content
    """
    if not isinstance(params, (tuple, list)):
        raise SecurityError("Query parameters must be tuple or list")
    
    validated_params = []
    for param in params:
        if param is None:
            validated_params.append(None)
        elif isinstance(param, (str, int, float, bool)):
            # Check string parameters for SQL injection patterns
            if isinstance(param, str):
                # Basic SQL injection detection
                dangerous_patterns = [
                    r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bCREATE\b)",
                    r"(--|#|/\*|\*/)",
                    r"(\bOR\b|\bAND\b).*?=.*?=",
                    r"['\"];?\s*(\bDROP\b|\bDELETE\b|\bUNION\b)"
                ]
                
                param_upper = param.upper()
                for pattern in dangerous_patterns:
                    if re.search(pattern, param_upper, re.IGNORECASE):
                        raise SecurityError(f"Potential SQL injection detected in parameter: {param}")
            
            validated_params.append(param)
        else:
            raise SecurityError(f"Unsupported parameter type: {type(param)}")
    
    return tuple(validated_params)


def is_safe_file_operation(source_path: Union[str, Path], target_path: Union[str, Path]) -> bool:
    """
    Check if file operation between source and target is safe.
    
    Args:
        source_path: Source file path
        target_path: Target file path
        
    Returns:
        True if operation is safe
        
    Raises:
        SecurityError: If operation is unsafe
    """
    try:
        # Validate both paths
        safe_source = validate_file_path(source_path)
        safe_target = validate_file_path(target_path)
        
        # Check that we're not overwriting system files
        system_paths = ['/bin', '/sbin', '/usr/bin', '/usr/sbin', '/system', '/windows']
        target_str = str(safe_target).lower()
        
        for sys_path in system_paths:
            if target_str.startswith(sys_path.lower()):
                raise SecurityError(f"Cannot write to system directory: {target_path}")
        
        # Check that source and target are not the same
        if safe_source == safe_target:
            raise SecurityError("Source and target paths are identical")
        
        return True
        
    except SecurityError:
        raise
    except Exception as e:
        raise SecurityError(f"Error validating file operation: {e}")


def get_safe_temp_dir() -> Path:
    """
    Get a safe temporary directory for file operations.
    
    Returns:
        Path to safe temporary directory
    """
    import tempfile
    
    try:
        temp_dir = Path(tempfile.gettempdir()) / "musicflow_safe"
        temp_dir.mkdir(exist_ok=True, mode=0o700)  # Only user access
        return temp_dir
    except Exception as e:
        raise SecurityError(f"Cannot create safe temporary directory: {e}")