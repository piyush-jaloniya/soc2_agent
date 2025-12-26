"""
Mock AWS Connector
Simulates AWS data collection for demonstration purposes.
"""

from typing import Dict, Any
from datetime import datetime
import uuid

from backend.connectors.base import BaseConnector


class AWSConnector(BaseConnector):
    """
    AWS connector for collecting IAM, RDS, S3, CloudTrail data.
    This is a mock implementation for demonstration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.region = config.get('region', 'us-east-1')
        self.account_id = config.get('account_id', '123456789012')
    
    def connect(self) -> bool:
        """Simulate AWS connection."""
        # In production, use boto3 to establish connection
        return True
    
    def test_connection(self) -> tuple[bool, str]:
        """Test AWS connectivity."""
        try:
            # In production, call boto3 STS get_caller_identity
            return True, "AWS connection successful"
        except Exception as e:
            return False, f"AWS connection failed: {str(e)}"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect AWS data.
        In production, this would use boto3 to query AWS APIs.
        """
        self.last_sync = datetime.utcnow()
        
        return {
            'users': self._collect_iam_users(),
            'resources': self._collect_resources(),
            'cloudtrail_status': self._collect_cloudtrail_status(),
            'databases': self._collect_rds_instances()
        }
    
    def _collect_iam_users(self) -> list:
        """Simulate IAM user collection."""
        # Mock data - in production, use boto3.client('iam').list_users()
        return [
            {
                'id': 'user-1',
                'email': 'admin@example.com',
                'name': 'Admin User',
                'role': 'admin',
                'is_admin': True,
                'mfa_enabled': True,
                'active': True,
                'source_system': 'aws_iam',
                'external_id': 'AIDAI123456'
            },
            {
                'id': 'user-2',
                'email': 'devops@example.com',
                'name': 'DevOps User',
                'role': 'devops',
                'is_admin': True,
                'mfa_enabled': False,  # Violation!
                'active': True,
                'source_system': 'aws_iam',
                'external_id': 'AIDAI234567'
            },
            {
                'id': 'user-3',
                'email': 'developer@example.com',
                'name': 'Developer',
                'role': 'developer',
                'is_admin': False,
                'mfa_enabled': True,
                'active': True,
                'source_system': 'aws_iam',
                'external_id': 'AIDAI345678'
            }
        ]
    
    def _collect_resources(self) -> list:
        """Simulate resource collection (RDS, S3, etc.)."""
        return [
            {
                'id': 'rds-prod-1',
                'resource_type': 'rds_instance',
                'name': 'production-db',
                'provider': 'aws',
                'region': 'us-east-1',
                'encryption_enabled': True,
                'public_access': False,
                'tags': {'Environment': 'production'}
            },
            {
                'id': 'rds-dev-1',
                'resource_type': 'rds_instance',
                'name': 'development-db',
                'provider': 'aws',
                'region': 'us-east-1',
                'encryption_enabled': False,  # Violation!
                'public_access': False,
                'tags': {'Environment': 'development'}
            },
            {
                'id': 's3-public-1',
                'resource_type': 's3_bucket',
                'name': 'public-assets-bucket',
                'provider': 'aws',
                'region': 'us-east-1',
                'encryption_enabled': True,
                'public_access': True,  # Potential violation
                'tags': {}
            },
            {
                'id': 's3-private-1',
                'resource_type': 's3_bucket',
                'name': 'confidential-data',
                'provider': 'aws',
                'region': 'us-east-1',
                'encryption_enabled': True,
                'public_access': False,
                'tags': {'Confidential': 'true'}
            }
        ]
    
    def _collect_cloudtrail_status(self) -> list:
        """Simulate CloudTrail status collection."""
        return [
            {
                'account_id': self.account_id,
                'region': 'us-east-1',
                'trail_name': 'main-trail',
                'is_multi_region': True,
                'is_logging': True
            },
            {
                'account_id': self.account_id,
                'region': 'us-west-2',
                'trail_name': None,
                'is_multi_region': False,
                'is_logging': False  # Violation!
            }
        ]
    
    def _collect_rds_instances(self) -> list:
        """Simulate RDS instance details collection."""
        return [
            {
                'id': 'rds-prod-1',
                'name': 'production-db',
                'environment': 'production',
                'encrypted': True,
                'backup_retention_period': 14
            },
            {
                'id': 'rds-dev-1',
                'name': 'development-db',
                'environment': 'development',
                'encrypted': False,
                'backup_retention_period': 3  # Violation if this was production
            },
            {
                'id': 'rds-test-1',
                'name': 'test-db',
                'environment': 'production',
                'encrypted': True,
                'backup_retention_period': 5  # Violation! Less than 7 days
            }
        ]
