"""
Result Cache System - Performance Optimization Component
=======================================================

Advanced caching system for music analysis results, organization plans,
and filter operations with intelligent memory management.

Features:
- LRU cache with TTL (Time To Live)
- Memory usage monitoring
- Persistent cache for expensive operations
- Compression for large datasets
- Cache warming strategies

Developed by BlueSystemIO
"""

import logging
import time
import pickle
import gzip
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref
import sys


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    compressed: bool = False
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def update_access(self):
        """Update access tracking."""
        self.last_accessed = time.time()
        self.access_count += 1


class MemoryManager:
    """Monitors and manages memory usage for cache."""
    
    def __init__(self, max_memory_mb: int = 500):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0
        self.logger = logging.getLogger(__name__)
    
    def can_add_entry(self, size_bytes: int) -> bool:
        """Check if new entry can be added without exceeding memory limit."""
        return self.current_memory_bytes + size_bytes <= self.max_memory_bytes
    
    def add_entry(self, size_bytes: int):
        """Add entry size to memory tracking."""
        self.current_memory_bytes += size_bytes
    
    def remove_entry(self, size_bytes: int):
        """Remove entry size from memory tracking."""
        self.current_memory_bytes = max(0, self.current_memory_bytes - size_bytes)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        return {
            'current_mb': self.current_memory_bytes / (1024 * 1024),
            'max_mb': self.max_memory_bytes / (1024 * 1024),
            'utilization': self.current_memory_bytes / self.max_memory_bytes,
            'available_mb': (self.max_memory_bytes - self.current_memory_bytes) / (1024 * 1024)
        }


class PersistentCache:
    """Persistent cache for expensive operations that survive app restarts."""
    
    def __init__(self, cache_dir: str = "~/.musicflow_cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.index_file = self.cache_dir / "cache_index.pkl"
        self.index: Dict[str, Dict[str, Any]] = self._load_index()
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load cache index from disk."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load cache index: {e}")
        return {}
    
    def _save_index(self):
        """Save cache index to disk."""
        try:
            with open(self.index_file, 'wb') as f:
                pickle.dump(self.index, f)
        except Exception as e:
            self.logger.error(f"Failed to save cache index: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from persistent cache."""
        if key not in self.index:
            return None
        
        entry_info = self.index[key]
        
        # Check TTL
        if 'ttl' in entry_info and entry_info['ttl'] is not None:
            if time.time() - entry_info['created_at'] > entry_info['ttl']:
                self.remove(key)
                return None
        
        try:
            cache_file = self.cache_dir / f"{key}.cache"
            if not cache_file.exists():
                # Clean up stale index entry
                del self.index[key]
                return None
            
            with open(cache_file, 'rb') as f:
                if entry_info.get('compressed', False):
                    data = gzip.decompress(f.read())
                    return pickle.loads(data)
                else:
                    return pickle.load(f)
                    
        except Exception as e:
            self.logger.warning(f"Failed to load cached value for {key}: {e}")
            self.remove(key)
            return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, 
            compress: bool = True):
        """Store value in persistent cache."""
        try:
            cache_file = self.cache_dir / f"{key}.cache"
            
            # Serialize and optionally compress
            if compress:
                data = pickle.dumps(value)
                compressed_data = gzip.compress(data)
                
                with open(cache_file, 'wb') as f:
                    f.write(compressed_data)
                
                size_bytes = len(compressed_data)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
                
                size_bytes = cache_file.stat().st_size
            
            # Update index
            self.index[key] = {
                'created_at': time.time(),
                'ttl': ttl,
                'compressed': compress,
                'size_bytes': size_bytes
            }
            
            self._save_index()
            
        except Exception as e:
            self.logger.error(f"Failed to cache value for {key}: {e}")
    
    def remove(self, key: str):
        """Remove entry from persistent cache."""
        try:
            cache_file = self.cache_dir / f"{key}.cache"
            if cache_file.exists():
                cache_file.unlink()
            
            if key in self.index:
                del self.index[key]
                self._save_index()
                
        except Exception as e:
            self.logger.warning(f"Failed to remove cached entry {key}: {e}")
    
    def clear(self):
        """Clear all persistent cache entries."""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.index.clear()
            self._save_index()
            
        except Exception as e:
            self.logger.error(f"Failed to clear persistent cache: {e}")
    
    def cleanup_expired(self):
        """Remove expired entries from persistent cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry_info in self.index.items():
            if 'ttl' in entry_info and entry_info['ttl'] is not None:
                if current_time - entry_info['created_at'] > entry_info['ttl']:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.remove(key)
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get persistent cache statistics."""
        total_size = sum(entry.get('size_bytes', 0) for entry in self.index.values())
        
        return {
            'total_entries': len(self.index),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'index_size': len(self.index)
        }


class LRUCache:
    """Memory-efficient LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.memory_manager = MemoryManager()
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.update_access()
            
            self.hits += 1
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, 
            compress: bool = False) -> bool:
        """Store value in cache."""
        with self.lock:
            # Calculate size
            try:
                size_bytes = sys.getsizeof(value)
                if hasattr(value, '__len__'):
                    size_bytes += sum(sys.getsizeof(item) for item in value if hasattr(item, '__sizeof__'))
            except:
                size_bytes = sys.getsizeof(value)
            
            # Check if we can add this entry
            if not self.memory_manager.can_add_entry(size_bytes):
                # Try to make room by evicting LRU entries
                if not self._make_room(size_bytes):
                    self.logger.warning(f"Cannot cache entry {key}: insufficient memory")
                    return False
            
            # Remove existing entry if it exists
            if key in self.cache:
                self._remove_entry(key)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl or self.default_ttl,
                compressed=compress,
                size_bytes=size_bytes
            )
            
            self.cache[key] = entry
            self.memory_manager.add_entry(size_bytes)
            
            # Ensure we don't exceed max size
            while len(self.cache) > self.max_size:
                self._evict_lru()
            
            return True
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache."""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.memory_manager.current_memory_bytes = 0
    
    def cleanup_expired(self):
        """Remove expired entries."""
        with self.lock:
            expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _remove_entry(self, key: str):
        """Remove entry and update memory tracking."""
        if key in self.cache:
            entry = self.cache[key]
            self.memory_manager.remove_entry(entry.size_bytes)
            del self.cache[key]
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if self.cache:
            lru_key = next(iter(self.cache))
            self._remove_entry(lru_key)
            self.evictions += 1
    
    def _make_room(self, needed_bytes: int) -> bool:
        """Make room for new entry by evicting LRU entries."""
        evicted_bytes = 0
        
        while (evicted_bytes < needed_bytes and 
               self.cache and 
               not self.memory_manager.can_add_entry(needed_bytes - evicted_bytes)):
            
            lru_key = next(iter(self.cache))
            entry = self.cache[lru_key]
            evicted_bytes += entry.size_bytes
            self._remove_entry(lru_key)
            self.evictions += 1
        
        return self.memory_manager.can_add_entry(needed_bytes)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'evictions': self.evictions,
                'memory_usage': self.memory_manager.get_memory_usage()
            }


class ResultCache:
    """Unified cache system combining memory and persistent caching."""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 memory_limit_mb: int = 500,
                 persistent_cache_dir: str = "~/.musicflow_cache",
                 default_ttl: Optional[float] = 3600):  # 1 hour default TTL
        
        self.memory_cache = LRUCache(memory_cache_size, default_ttl)
        self.persistent_cache = PersistentCache(persistent_cache_dir)
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)
        
        # Configure memory manager
        self.memory_cache.memory_manager.max_memory_bytes = memory_limit_mb * 1024 * 1024
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then persistent)."""
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try persistent cache
        value = self.persistent_cache.get(key)
        if value is not None:
            # Promote to memory cache
            self.memory_cache.put(key, value)
            return value
        
        return None
    
    def put(self, key: str, value: Any, 
           ttl: Optional[float] = None,
           persist: bool = False,
           compress: bool = True) -> bool:
        """Store value in cache."""
        effective_ttl = ttl or self.default_ttl
        
        # Always try to store in memory cache
        memory_success = self.memory_cache.put(key, value, effective_ttl)
        
        # Store in persistent cache if requested or if memory cache failed
        if persist or not memory_success:
            self.persistent_cache.put(key, value, effective_ttl, compress)
        
        return memory_success
    
    def remove(self, key: str):
        """Remove entry from both caches."""
        self.memory_cache.remove(key)
        self.persistent_cache.remove(key)
    
    def clear(self):
        """Clear both caches."""
        self.memory_cache.clear()
        self.persistent_cache.clear()
    
    def cleanup_expired(self):
        """Clean up expired entries from both caches."""
        self.memory_cache.cleanup_expired()
        self.persistent_cache.cleanup_expired()
    
    def warm_cache(self, warm_func: Callable[[str], Tuple[str, Any]], 
                  keys: List[str]):
        """Warm cache with commonly accessed data."""
        self.logger.info(f"Warming cache with {len(keys)} entries")
        
        for key in keys:
            if self.get(key) is None:  # Only warm if not already cached
                try:
                    cache_key, value = warm_func(key)
                    self.put(cache_key, value, persist=True)
                except Exception as e:
                    self.logger.warning(f"Failed to warm cache for {key}: {e}")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from both cache layers."""
        return {
            'memory_cache': self.memory_cache.get_stats(),
            'persistent_cache': self.persistent_cache.get_stats(),
            'cache_layers': 2
        }
