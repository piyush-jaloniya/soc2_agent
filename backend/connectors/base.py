"""
Base Connector Class
Defines the interface for all data source connectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseConnector(ABC):
    """
    Abstract base class for all connectors.
    Each connector integrates with a specific service (AWS, Okta, GitHub, etc.)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with configuration.
        
        Args:
            config: Connector configuration (credentials, endpoints, etc.)
        """
        self.config = config
        self.name = self.__class__.__name__
        self.last_sync = None
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the service.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from the service.
        
        Returns:
            Dictionary with collected data organized by resource type
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """
        Test if connector can reach the service.
        
        Returns:
            Tuple of (success, message)
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get connector status."""
        return {
            'name': self.name,
            'last_sync': self.last_sync,
            'config': {k: v for k, v in self.config.items() if k not in ['api_key', 'secret', 'password']}
        }
