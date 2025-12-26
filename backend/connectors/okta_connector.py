"""
Mock Okta Connector
Simulates Okta/IdP data collection for demonstration purposes.
"""

from typing import Dict, Any
from datetime import datetime

from backend.connectors.base import BaseConnector


class OktaConnector(BaseConnector):
    """
    Okta connector for collecting user, group, and authentication data.
    This is a mock implementation for demonstration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.domain = config.get('domain', 'example.okta.com')
    
    def connect(self) -> bool:
        """Simulate Okta connection."""
        # In production, use Okta API client
        return True
    
    def test_connection(self) -> tuple[bool, str]:
        """Test Okta connectivity."""
        try:
            # In production, call Okta API to verify credentials
            return True, "Okta connection successful"
        except Exception as e:
            return False, f"Okta connection failed: {str(e)}"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect Okta data.
        In production, this would use Okta API.
        """
        self.last_sync = datetime.utcnow()
        
        return {
            'users': self._collect_users(),
            'hr_employees': self._collect_hr_data()
        }
    
    def _collect_users(self) -> list:
        """Simulate Okta user collection."""
        return [
            {
                'id': 'okta-user-1',
                'email': 'admin@example.com',
                'name': 'Admin User',
                'role': 'admin',
                'is_admin': True,
                'mfa_enabled': True,
                'active': True,
                'source_system': 'okta',
                'external_id': 'okta123456',
                'last_login': datetime.utcnow()
            },
            {
                'id': 'okta-user-2',
                'email': 'security@example.com',
                'name': 'Security Lead',
                'role': 'security',
                'is_admin': True,
                'mfa_enabled': False,  # Violation!
                'active': True,
                'source_system': 'okta',
                'external_id': 'okta234567',
                'last_login': datetime.utcnow()
            },
            {
                'id': 'okta-user-3',
                'email': 'former.employee@example.com',
                'name': 'Former Employee',
                'role': 'developer',
                'is_admin': False,
                'mfa_enabled': True,
                'active': True,  # Still active but not in HR!
                'source_system': 'okta',
                'external_id': 'okta345678',
                'last_login': None
            },
            {
                'id': 'okta-user-4',
                'email': 'developer@example.com',
                'name': 'Developer',
                'role': 'developer',
                'is_admin': False,
                'mfa_enabled': True,
                'active': True,
                'source_system': 'okta',
                'external_id': 'okta456789',
                'last_login': datetime.utcnow()
            }
        ]
    
    def _collect_hr_data(self) -> list:
        """
        Simulate HR employee data.
        Used to detect orphaned accounts.
        """
        return [
            {
                'employee_id': 'emp-1',
                'email': 'admin@example.com',
                'name': 'Admin User',
                'status': 'active',
                'department': 'IT'
            },
            {
                'employee_id': 'emp-2',
                'email': 'security@example.com',
                'name': 'Security Lead',
                'status': 'active',
                'department': 'Security'
            },
            {
                'employee_id': 'emp-4',
                'email': 'developer@example.com',
                'name': 'Developer',
                'status': 'active',
                'department': 'Engineering'
            }
            # Note: former.employee@example.com is NOT in HR data - orphaned account!
        ]
