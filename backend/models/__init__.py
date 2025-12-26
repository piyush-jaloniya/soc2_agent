"""
Core data models for SOC 2 compliance platform.
Defines the foundational entities for controls, evidence, and evaluations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TSCCategory(str, Enum):
    """Trust Services Criteria categories"""
    SECURITY = "Security"
    AVAILABILITY = "Availability"
    CONFIDENTIALITY = "Confidentiality"
    PROCESSING_INTEGRITY = "Processing Integrity"
    PRIVACY = "Privacy"


class ControlType(str, Enum):
    """Types of controls"""
    ADMINISTRATIVE = "Administrative"
    TECHNICAL = "Technical"
    PHYSICAL = "Physical"


class EvaluationStatus(str, Enum):
    """Control evaluation status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_EVALUATED = "not_evaluated"


class Severity(str, Enum):
    """Finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EvidenceType(str, Enum):
    """Types of evidence"""
    LOG = "log"
    CONFIG = "config"
    POLICY = "policy"
    TICKET = "ticket"
    SCREENSHOT = "screenshot"
    REPORT = "report"


# === Control Models ===

class Control(BaseModel):
    """
    Represents a SOC 2 control with its definition and evaluation logic.
    """
    id: str = Field(..., description="Unique control identifier (e.g., CC6.1-IAM-MFA)")
    name: str = Field(..., description="Human-readable control name")
    description: str = Field(..., description="Detailed control description")
    tsc_reference: str = Field(..., description="Trust Services Criteria reference (e.g., CC6.1)")
    category: TSCCategory = Field(..., description="TSC category")
    control_type: ControlType = Field(..., description="Type of control")
    sources: List[str] = Field(default_factory=list, description="Data sources required")
    logic: Dict[str, Any] = Field(..., description="Evaluation logic (rules or queries)")
    severity: Severity = Field(..., description="Control severity")
    evaluation_frequency: str = Field(..., description="How often to evaluate (e.g., '1h', '24h')")
    enabled: bool = Field(default=True, description="Whether control is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ControlEvaluation(BaseModel):
    """
    Records the result of a control evaluation at a specific point in time.
    """
    id: str = Field(..., description="Unique evaluation ID")
    control_id: str = Field(..., description="Associated control ID")
    status: EvaluationStatus = Field(..., description="Evaluation result")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict, description="Evaluation details")
    findings: List[str] = Field(default_factory=list, description="List of finding IDs")
    evidence_ids: List[str] = Field(default_factory=list, description="Associated evidence")
    evaluator: str = Field(default="system", description="Who/what performed evaluation")


class Finding(BaseModel):
    """
    Represents a compliance issue discovered during control evaluation.
    """
    id: str = Field(..., description="Unique finding ID")
    control_id: str = Field(..., description="Associated control")
    evaluation_id: str = Field(..., description="Evaluation that discovered this finding")
    title: str = Field(..., description="Short finding title")
    description: str = Field(..., description="Detailed finding description")
    severity: Severity = Field(..., description="Finding severity")
    status: str = Field(default="open", description="Finding status (open, in_progress, resolved)")
    resource_id: Optional[str] = Field(None, description="Affected resource identifier")
    remediation: Optional[str] = Field(None, description="Recommended remediation steps")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None


# === Evidence Models ===

class Evidence(BaseModel):
    """
    Represents a piece of evidence supporting control compliance.
    """
    id: str = Field(..., description="Unique evidence ID")
    type: EvidenceType = Field(..., description="Type of evidence")
    control_ids: List[str] = Field(default_factory=list, description="Associated controls")
    evaluation_id: Optional[str] = Field(None, description="Associated evaluation")
    source: str = Field(..., description="Source system (e.g., 'aws', 'okta')")
    location: str = Field(..., description="Storage location/path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    hash: Optional[str] = Field(None, description="Content hash for integrity")


# === Identity & Access Models ===

class User(BaseModel):
    """
    Represents a user identity across connected systems.
    """
    id: str = Field(..., description="Unique user ID")
    email: str = Field(..., description="Primary email")
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Primary role")
    is_admin: bool = Field(default=False)
    mfa_enabled: bool = Field(default=False)
    active: bool = Field(default=True)
    source_system: str = Field(..., description="Origin system (okta, azure_ad, etc.)")
    external_id: str = Field(..., description="ID in source system")
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Resource(BaseModel):
    """
    Represents a cloud or application resource (DB, bucket, VM, etc.).
    """
    id: str = Field(..., description="Unique resource ID")
    resource_type: str = Field(..., description="Type (s3_bucket, rds_instance, vm, etc.)")
    name: str = Field(..., description="Resource name")
    provider: str = Field(..., description="Provider (aws, gcp, azure)")
    region: Optional[str] = None
    encryption_enabled: bool = Field(default=False)
    public_access: bool = Field(default=False)
    tags: Dict[str, str] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=datetime.utcnow)


class Event(BaseModel):
    """
    Represents a security or audit event.
    """
    id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Type of event")
    source: str = Field(..., description="Source system")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    severity: Optional[Severity] = None


# === Policy & Documentation Models ===

class Policy(BaseModel):
    """
    Represents a compliance policy document.
    """
    id: str = Field(..., description="Unique policy ID")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    content: str = Field(..., description="Policy content (markdown)")
    version: str = Field(..., description="Version number")
    category: str = Field(..., description="Policy category")
    owner: str = Field(..., description="Policy owner")
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    review_date: Optional[datetime] = None
    controls: List[str] = Field(default_factory=list, description="Associated control IDs")


# === Request/Response Models ===

class ControlStatusResponse(BaseModel):
    """Response model for control status"""
    control: Control
    latest_evaluation: Optional[ControlEvaluation] = None
    active_findings: List[Finding] = Field(default_factory=list)
    compliance_rate: float = Field(default=0.0)


class DashboardSummary(BaseModel):
    """Summary statistics for dashboard"""
    total_controls: int = 0
    passing_controls: int = 0
    failing_controls: int = 0
    warning_controls: int = 0
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    compliance_score: float = 0.0
    last_evaluation: Optional[datetime] = None


class EvaluationRequest(BaseModel):
    """Request to evaluate controls"""
    control_ids: Optional[List[str]] = None
    force: bool = False
