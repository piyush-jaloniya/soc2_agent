"""
Control Evaluation Engine
Executes control checks and generates findings based on control definitions.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import yaml
import os

from backend.models import (
    Control, ControlEvaluation, Finding, Evidence,
    EvaluationStatus, Severity, TSCCategory, ControlType
)


class ControlEvaluationEngine:
    """
    Core engine for evaluating SOC 2 controls.
    Loads control definitions and executes evaluation logic.
    """
    
    def __init__(self, control_catalog_path: str = None):
        """Initialize the evaluation engine with control catalog."""
        if control_catalog_path is None:
            control_catalog_path = os.path.join(
                os.path.dirname(__file__), 
                "../../control_catalog"
            )
        
        self.control_catalog_path = control_catalog_path
        self.controls: Dict[str, Control] = {}
        self.load_controls()
    
    def load_controls(self):
        """Load control definitions from YAML files."""
        catalog_files = [
            "security_controls.yaml"
            # Can add: availability_controls.yaml, confidentiality_controls.yaml, etc.
        ]
        
        for filename in catalog_files:
            filepath = os.path.join(self.control_catalog_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'controls' in data:
                        for control_data in data['controls']:
                            control = self._parse_control(control_data)
                            self.controls[control.id] = control
    
    def _parse_control(self, control_data: Dict[str, Any]) -> Control:
        """Parse control data from YAML into Control model."""
        return Control(
            id=control_data['id'],
            name=control_data['name'],
            description=control_data['description'],
            tsc_reference=control_data['tsc_reference'],
            category=TSCCategory(control_data['category']),
            control_type=ControlType(control_data['control_type']),
            sources=control_data.get('sources', []),
            logic=control_data.get('logic', {}),
            severity=Severity(control_data['severity']),
            evaluation_frequency=control_data['evaluation_frequency'],
            enabled=control_data.get('enabled', True)
        )
    
    def get_control(self, control_id: str) -> Optional[Control]:
        """Retrieve a control by ID."""
        return self.controls.get(control_id)
    
    def list_controls(
        self, 
        category: Optional[TSCCategory] = None,
        severity: Optional[Severity] = None,
        enabled_only: bool = True
    ) -> List[Control]:
        """List controls with optional filters."""
        controls = list(self.controls.values())
        
        if enabled_only:
            controls = [c for c in controls if c.enabled]
        
        if category:
            controls = [c for c in controls if c.category == category]
        
        if severity:
            controls = [c for c in controls if c.severity == severity]
        
        return controls
    
    def evaluate_control(
        self, 
        control_id: str, 
        data_context: Dict[str, Any]
    ) -> ControlEvaluation:
        """
        Evaluate a single control against current data.
        
        Args:
            control_id: ID of control to evaluate
            data_context: Dictionary containing data from connected sources
        
        Returns:
            ControlEvaluation with results
        """
        control = self.get_control(control_id)
        if not control:
            raise ValueError(f"Control {control_id} not found")
        
        evaluation_id = str(uuid.uuid4())
        
        # Execute evaluation logic based on control type
        logic = control.logic
        logic_type = logic.get('type', 'boolean_check')
        
        if logic_type == 'boolean_check':
            status, details, findings = self._evaluate_boolean_check(
                control, data_context, evaluation_id
            )
        elif logic_type == 'manual_review':
            status, details, findings = self._evaluate_manual_review(
                control, data_context, evaluation_id
            )
        else:
            status = EvaluationStatus.NOT_EVALUATED
            details = {'error': f'Unknown logic type: {logic_type}'}
            findings = []
        
        evaluation = ControlEvaluation(
            id=evaluation_id,
            control_id=control_id,
            status=status,
            evaluated_at=datetime.utcnow(),
            details=details,
            findings=[f.id for f in findings],
            evidence_ids=[]
        )
        
        return evaluation, findings
    
    def _evaluate_boolean_check(
        self, 
        control: Control, 
        data_context: Dict[str, Any],
        evaluation_id: str
    ) -> tuple[EvaluationStatus, Dict[str, Any], List[Finding]]:
        """
        Evaluate a boolean check control.
        Simulates SQL query execution against data context.
        """
        logic = control.logic
        query = logic.get('query', '')
        success_condition = logic.get('success_condition', 'row_count = 0')
        threshold = logic.get('threshold', 0)
        
        # In a real implementation, this would:
        # 1. Parse the query
        # 2. Execute against a database or data context
        # 3. Evaluate the success condition
        
        # For MVP, we'll simulate evaluation based on data_context
        violations = self._simulate_query_execution(control.id, data_context)
        
        violation_count = len(violations)
        
        # Evaluate success condition
        if 'row_count = 0' in success_condition:
            passed = violation_count == 0
        elif 'row_count <= threshold' in success_condition:
            passed = violation_count <= threshold
        else:
            passed = violation_count == 0  # Default
        
        status = EvaluationStatus.PASS if passed else EvaluationStatus.FAIL
        
        details = {
            'violation_count': violation_count,
            'violations': violations,
            'query': query,
            'success_condition': success_condition
        }
        
        # Create findings for violations
        findings = []
        if not passed:
            failure_message = logic.get('failure_message', 'Control check failed')
            failure_message = failure_message.format(count=violation_count)
            
            for i, violation in enumerate(violations[:10]):  # Limit to 10 findings
                finding = Finding(
                    id=str(uuid.uuid4()),
                    control_id=control.id,
                    evaluation_id=evaluation_id,
                    title=f"{control.name} - Violation {i+1}",
                    description=f"{failure_message}\n\nDetails: {violation}",
                    severity=control.severity,
                    status="open",
                    resource_id=violation.get('resource_id'),
                    remediation=control.logic.get('remediation', 'See control description'),
                    discovered_at=datetime.utcnow()
                )
                findings.append(finding)
        
        return status, details, findings
    
    def _evaluate_manual_review(
        self, 
        control: Control, 
        data_context: Dict[str, Any],
        evaluation_id: str
    ) -> tuple[EvaluationStatus, Dict[str, Any], List[Finding]]:
        """
        Evaluate a manual review control.
        These controls require human verification but we can flag items needing review.
        """
        logic = control.logic
        query = logic.get('query', '')
        
        # Simulate finding items that need review
        items_needing_review = self._simulate_query_execution(control.id, data_context)
        
        status = EvaluationStatus.WARNING if len(items_needing_review) > 0 else EvaluationStatus.PASS
        
        details = {
            'items_needing_review': len(items_needing_review),
            'items': items_needing_review,
            'requires_manual_review': True
        }
        
        findings = []
        if items_needing_review:
            for i, item in enumerate(items_needing_review[:5]):
                finding = Finding(
                    id=str(uuid.uuid4()),
                    control_id=control.id,
                    evaluation_id=evaluation_id,
                    title=f"{control.name} - Review Required {i+1}",
                    description=f"Manual review required for: {item}",
                    severity=Severity.INFO,
                    status="open",
                    resource_id=item.get('resource_id'),
                    discovered_at=datetime.utcnow()
                )
                findings.append(finding)
        
        return status, details, findings
    
    def _simulate_query_execution(
        self, 
        control_id: str, 
        data_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Simulate query execution for demo purposes.
        In production, this would execute actual queries against databases.
        """
        # Simulate different control results based on control ID
        
        if 'MFA' in control_id:
            # Simulate MFA check
            users = data_context.get('users', [])
            return [
                {
                    'user_id': u.get('id', u.get('email')),
                    'email': u.get('email'),
                    'role': u.get('role'),
                    'resource_id': u.get('id', u.get('email'))
                }
                for u in users
                if u.get('is_admin', False) and not u.get('mfa_enabled', False)
            ]
        
        elif 'ORPHANED' in control_id:
            # Simulate orphaned account check
            users = data_context.get('users', [])
            hr_emails = {emp.get('email') for emp in data_context.get('hr_employees', [])}
            return [
                {
                    'user_id': u.get('id', u.get('email')),
                    'email': u.get('email'),
                    'name': u.get('name'),
                    'resource_id': u.get('id', u.get('email'))
                }
                for u in users
                if u.get('active', True) and u.get('email') not in hr_emails
            ]
        
        elif 'ENCRYPTION' in control_id:
            # Simulate encryption check
            resources = data_context.get('resources', [])
            return [
                {
                    'resource_id': r.get('id'),
                    'name': r.get('name'),
                    'type': r.get('resource_type')
                }
                for r in resources
                if not r.get('encryption_enabled', False)
            ]
        
        elif 'PUBLIC-ACCESS' in control_id:
            # Simulate public access check
            resources = data_context.get('resources', [])
            return [
                {
                    'resource_id': r.get('id'),
                    'name': r.get('name'),
                    'type': r.get('resource_type')
                }
                for r in resources
                if r.get('public_access', False) and r.get('resource_type') == 's3_bucket'
            ]
        
        elif 'CLOUDTRAIL' in control_id:
            # Simulate CloudTrail check
            trails = data_context.get('cloudtrail_status', [])
            return [
                {
                    'account_id': t.get('account_id'),
                    'region': t.get('region'),
                    'resource_id': f"{t.get('account_id')}-{t.get('region')}"
                }
                for t in trails
                if not t.get('is_logging', False) or not t.get('is_multi_region', False)
            ]
        
        elif 'BACKUP' in control_id:
            # Simulate backup check
            databases = data_context.get('databases', [])
            return [
                {
                    'resource_id': db.get('id'),
                    'name': db.get('name'),
                    'backup_retention': db.get('backup_retention_period', 0)
                }
                for db in databases
                if db.get('backup_retention_period', 0) < 7
            ]
        
        # Default: no violations
        return []
    
    def evaluate_all_controls(
        self, 
        data_context: Dict[str, Any],
        category: Optional[TSCCategory] = None
    ) -> Dict[str, tuple[ControlEvaluation, List[Finding]]]:
        """
        Evaluate all enabled controls.
        
        Returns:
            Dictionary mapping control_id to (evaluation, findings)
        """
        controls_to_evaluate = self.list_controls(category=category, enabled_only=True)
        results = {}
        
        for control in controls_to_evaluate:
            try:
                evaluation, findings = self.evaluate_control(control.id, data_context)
                results[control.id] = (evaluation, findings)
            except Exception as e:
                # Log error and continue
                print(f"Error evaluating control {control.id}: {e}")
                continue
        
        return results
