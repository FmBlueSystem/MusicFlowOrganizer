"""
Plugin Manager for MusicFlow Organizer
======================================
Manages plugin lifecycle and integration with the main application.

Author: Claude Code
Date: 2025-07-12
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Base plugin interface for MusicFlow extensions."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.enabled = False
        self.logger = logging.getLogger(f"plugin.{name}")
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities provided by this plugin."""
        pass
    
    def enable(self):
        """Enable the plugin."""
        self.enabled = True
        self.logger.info(f"Plugin {self.name} enabled")
    
    def disable(self):
        """Disable the plugin."""
        self.enabled = False
        self.logger.info(f"Plugin {self.name} disabled")

class PluginManager:
    """
    Manages plugins for MusicFlow Organizer.
    Provides non-destructive integration with existing codebase.
    """
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = logging.getLogger("PluginManager")
        self._plugin_directory = Path(__file__).parent
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin with the manager.
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            plugin_name = plugin.name
            
            if plugin_name in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} already registered")
                return False
            
            self.plugins[plugin_name] = plugin
            self.logger.info(f"Registered plugin: {plugin_name} v{plugin.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register plugin: {e}")
            return False
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins with their status."""
        return {
            name: {
                'version': plugin.version,
                'enabled': plugin.enabled,
                'capabilities': plugin.get_capabilities()
            }
            for name, plugin in self.plugins.items()
        }
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a specific plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a specific plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.disable()
            return True
        return False
    
    def execute_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Execute a method on a specific plugin safely.
        
        Args:
            plugin_name: Name of the plugin
            method_name: Method to execute
            *args, **kwargs: Arguments for the method
            
        Returns:
            Method result or None if plugin/method not found
        """
        try:
            plugin = self.get_plugin(plugin_name)
            if not plugin or not plugin.enabled:
                return None
            
            if hasattr(plugin, method_name):
                method = getattr(plugin, method_name)
                return method(*args, **kwargs)
            else:
                self.logger.warning(f"Method {method_name} not found in plugin {plugin_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error executing {method_name} on plugin {plugin_name}: {e}")
            return None

# Global plugin manager instance
plugin_manager = PluginManager()