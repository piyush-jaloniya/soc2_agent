"""
Evidence Vault Service
Manages collection, storage, and retrieval of compliance evidence.
"""

import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.models import Evidence, EvidenceType


class EvidenceVault:
    """
    Service for managing compliance evidence artifacts.
    Stores evidence in an immutable manner with integrity verification.
    """
    
    def __init__(self, vault_path: str = None):
        """Initialize the evidence vault with storage location."""
        if vault_path is None:
            vault_path = os.path.join(
                os.path.dirname(__file__),
                "../../evidence_vault"
            )
        
        self.vault_path = vault_path
        self.metadata_file = os.path.join(vault_path, "metadata.json")
        
        # Create vault directory if it doesn't exist
        Path(vault_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize or load metadata
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load evidence metadata from disk."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
    
    def _save_metadata(self):
        """Save evidence metadata to disk."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content for integrity verification."""
        return hashlib.sha256(content).hexdigest()
    
    def store_evidence(
        self,
        evidence_type: EvidenceType,
        source: str,
        content: Any,
        control_ids: List[str] = None,
        evaluation_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Evidence:
        """
        Store a piece of evidence in the vault.
        
        Args:
            evidence_type: Type of evidence
            source: Source system
            content: Evidence content (will be serialized)
            control_ids: Associated control IDs
            evaluation_id: Associated evaluation ID
            metadata: Additional metadata
        
        Returns:
            Evidence object with storage location
        """
        evidence_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Serialize content
        if isinstance(content, (dict, list)):
            content_bytes = json.dumps(content, indent=2, default=str).encode('utf-8')
            file_extension = 'json'
        elif isinstance(content, str):
            content_bytes = content.encode('utf-8')
            file_extension = 'txt'
        elif isinstance(content, bytes):
            content_bytes = content
            file_extension = 'bin'
        else:
            content_bytes = str(content).encode('utf-8')
            file_extension = 'txt'
        
        # Compute hash
        content_hash = self._compute_hash(content_bytes)
        
        # Generate storage path organized by date and type
        date_path = timestamp.strftime('%Y/%m/%d')
        storage_dir = os.path.join(self.vault_path, date_path, evidence_type.value)
        Path(storage_dir).mkdir(parents=True, exist_ok=True)
        
        # Store file
        filename = f"{evidence_id}.{file_extension}"
        filepath = os.path.join(storage_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(content_bytes)
        
        # Create evidence record
        relative_path = os.path.join(date_path, evidence_type.value, filename)
        
        evidence = Evidence(
            id=evidence_id,
            type=evidence_type,
            control_ids=control_ids or [],
            evaluation_id=evaluation_id,
            source=source,
            location=relative_path,
            metadata=metadata or {},
            collected_at=timestamp,
            hash=content_hash
        )
        
        # Save metadata
        self.metadata[evidence_id] = evidence.model_dump()
        self._save_metadata()
        
        return evidence
    
    def retrieve_evidence(self, evidence_id: str) -> Optional[tuple[Evidence, bytes]]:
        """
        Retrieve evidence by ID.
        
        Returns:
            Tuple of (Evidence, content_bytes) or None if not found
        """
        if evidence_id not in self.metadata:
            return None
        
        evidence_data = self.metadata[evidence_id]
        evidence = Evidence(**evidence_data)
        
        filepath = os.path.join(self.vault_path, evidence.location)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Verify integrity
        computed_hash = self._compute_hash(content)
        if computed_hash != evidence.hash:
            raise ValueError(f"Evidence integrity check failed for {evidence_id}")
        
        return evidence, content
    
    def list_evidence(
        self,
        control_id: Optional[str] = None,
        evaluation_id: Optional[str] = None,
        evidence_type: Optional[EvidenceType] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Evidence]:
        """
        List evidence with optional filters.
        """
        results = []
        
        for evidence_id, evidence_data in self.metadata.items():
            evidence = Evidence(**evidence_data)
            
            # Apply filters
            if control_id and control_id not in evidence.control_ids:
                continue
            
            if evaluation_id and evidence.evaluation_id != evaluation_id:
                continue
            
            if evidence_type and evidence.type != evidence_type:
                continue
            
            if source and evidence.source != source:
                continue
            
            if start_date and evidence.collected_at < start_date:
                continue
            
            if end_date and evidence.collected_at > end_date:
                continue
            
            results.append(evidence)
        
        # Sort by collection time (newest first)
        results.sort(key=lambda e: e.collected_at, reverse=True)
        
        return results
    
    def collect_snapshot(
        self,
        source: str,
        data: Dict[str, Any],
        control_ids: List[str] = None
    ) -> Evidence:
        """
        Collect a configuration or data snapshot as evidence.
        """
        return self.store_evidence(
            evidence_type=EvidenceType.CONFIG,
            source=source,
            content=data,
            control_ids=control_ids,
            metadata={
                'snapshot_type': 'configuration',
                'source': source
            }
        )
    
    def collect_log(
        self,
        source: str,
        log_data: Any,
        control_ids: List[str] = None
    ) -> Evidence:
        """
        Collect log data as evidence.
        """
        return self.store_evidence(
            evidence_type=EvidenceType.LOG,
            source=source,
            content=log_data,
            control_ids=control_ids,
            metadata={
                'log_type': 'audit',
                'source': source
            }
        )
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about stored evidence.
        """
        total_evidence = len(self.metadata)
        
        by_type = {}
        by_source = {}
        
        for evidence_data in self.metadata.values():
            evidence = Evidence(**evidence_data)
            
            # Count by type
            type_name = evidence.type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # Count by source
            source_name = evidence.source
            by_source[source_name] = by_source.get(source_name, 0) + 1
        
        return {
            'total_evidence': total_evidence,
            'by_type': by_type,
            'by_source': by_source
        }
