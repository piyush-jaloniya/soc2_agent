"""
FastAPI REST API for SOC 2 Compliance Platform
Provides endpoints for controls, evaluations, evidence, and dashboards.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from datetime import datetime
import os

from backend.models import (
    Control, ControlEvaluation, Finding, Evidence,
    TSCCategory, Severity, ControlStatusResponse, 
    DashboardSummary, EvaluationRequest, EvidenceType
)
from backend.services.evaluation_engine import ControlEvaluationEngine
from backend.services.evidence_vault import EvidenceVault
from backend.connectors.aws_connector import AWSConnector
from backend.connectors.okta_connector import OktaConnector


# Initialize FastAPI app
app = FastAPI(
    title="SOC 2 AI Compliance Platform",
    description="Production-grade SOC 2 compliance automation with continuous control monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
evaluation_engine = ControlEvaluationEngine()
evidence_vault = EvidenceVault()

# In-memory storage for demo (use database in production)
evaluations_db = {}
findings_db = {}

# Initialize connectors (mock configs)
connectors = {
    'aws': AWSConnector({'region': 'us-east-1', 'account_id': '123456789012'}),
    'okta': OktaConnector({'domain': 'example.okta.com'})
}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard."""
    html_path = os.path.join(os.path.dirname(__file__), "../../frontend/templates/dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            return f.read()
    return HTMLResponse(content="<h1>SOC 2 Compliance Platform</h1><p>API is running. Visit /docs for API documentation.</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# === Control Endpoints ===

@app.get("/api/controls", response_model=List[Control])
async def list_controls(
    category: Optional[TSCCategory] = None,
    severity: Optional[Severity] = None,
    enabled_only: bool = True
):
    """List all controls with optional filters."""
    controls = evaluation_engine.list_controls(
        category=category,
        severity=severity,
        enabled_only=enabled_only
    )
    return controls


@app.get("/api/controls/{control_id}", response_model=Control)
async def get_control(control_id: str):
    """Get details of a specific control."""
    control = evaluation_engine.get_control(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control


@app.get("/api/controls/{control_id}/status", response_model=ControlStatusResponse)
async def get_control_status(control_id: str):
    """Get current status of a control including latest evaluation and findings."""
    control = evaluation_engine.get_control(control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Get latest evaluation
    control_evaluations = [e for e in evaluations_db.values() if e.control_id == control_id]
    latest_evaluation = max(control_evaluations, key=lambda e: e.evaluated_at) if control_evaluations else None
    
    # Get active findings
    active_findings = [
        f for f in findings_db.values() 
        if f.control_id == control_id and f.status == "open"
    ]
    
    # Calculate compliance rate (last 30 evaluations)
    recent_evals = sorted(control_evaluations, key=lambda e: e.evaluated_at, reverse=True)[:30]
    if recent_evals:
        passed = sum(1 for e in recent_evals if e.status == "pass")
        compliance_rate = (passed / len(recent_evals)) * 100
    else:
        compliance_rate = 0.0
    
    return ControlStatusResponse(
        control=control,
        latest_evaluation=latest_evaluation,
        active_findings=active_findings,
        compliance_rate=compliance_rate
    )


# === Evaluation Endpoints ===

@app.post("/api/evaluations/run")
async def run_evaluations(request: EvaluationRequest):
    """
    Run control evaluations.
    Collects data from connectors and evaluates controls.
    """
    # Collect data from all connectors
    data_context = {}
    for connector_name, connector in connectors.items():
        try:
            connector_data = connector.collect_data()
            data_context.update(connector_data)
            
            # Store snapshot as evidence
            evidence_vault.collect_snapshot(
                source=connector_name,
                data=connector_data,
                control_ids=None  # Will be associated when evaluating
            )
        except Exception as e:
            print(f"Error collecting data from {connector_name}: {e}")
    
    # Determine which controls to evaluate
    if request.control_ids:
        controls_to_eval = [evaluation_engine.get_control(cid) for cid in request.control_ids]
        controls_to_eval = [c for c in controls_to_eval if c]
    else:
        controls_to_eval = evaluation_engine.list_controls(enabled_only=True)
    
    results = []
    
    for control in controls_to_eval:
        try:
            evaluation, findings = evaluation_engine.evaluate_control(control.id, data_context)
            
            # Store evaluation
            evaluations_db[evaluation.id] = evaluation
            
            # Store findings
            for finding in findings:
                findings_db[finding.id] = finding
            
            results.append({
                'control_id': control.id,
                'evaluation_id': evaluation.id,
                'status': evaluation.status,
                'findings_count': len(findings)
            })
        except Exception as e:
            results.append({
                'control_id': control.id,
                'error': str(e)
            })
    
    return {
        'evaluated_at': datetime.utcnow(),
        'controls_evaluated': len(results),
        'results': results
    }


@app.get("/api/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """Get details of a specific evaluation."""
    if evaluation_id not in evaluations_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluations_db[evaluation_id]


@app.get("/api/evaluations", response_model=List[ControlEvaluation])
async def list_evaluations(
    control_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200)
):
    """List evaluations with optional filters."""
    evals = list(evaluations_db.values())
    
    if control_id:
        evals = [e for e in evals if e.control_id == control_id]
    
    if status:
        evals = [e for e in evals if e.status == status]
    
    # Sort by date (newest first)
    evals.sort(key=lambda e: e.evaluated_at, reverse=True)
    
    return evals[:limit]


# === Finding Endpoints ===

@app.get("/api/findings", response_model=List[Finding])
async def list_findings(
    control_id: Optional[str] = None,
    severity: Optional[Severity] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200)
):
    """List findings with optional filters."""
    findings = list(findings_db.values())
    
    if control_id:
        findings = [f for f in findings if f.control_id == control_id]
    
    if severity:
        findings = [f for f in findings if f.severity == severity]
    
    if status:
        findings = [f for f in findings if f.status == status]
    
    # Sort by severity and date
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    findings.sort(key=lambda f: (severity_order.get(f.severity.value, 5), f.discovered_at), reverse=True)
    
    return findings[:limit]


@app.get("/api/findings/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    """Get details of a specific finding."""
    if finding_id not in findings_db:
        raise HTTPException(status_code=404, detail="Finding not found")
    return findings_db[finding_id]


# === Evidence Endpoints ===

@app.get("/api/evidence", response_model=List[Evidence])
async def list_evidence(
    control_id: Optional[str] = None,
    evidence_type: Optional[EvidenceType] = None,
    source: Optional[str] = None,
    limit: int = Query(default=50, le=200)
):
    """List evidence with optional filters."""
    evidence = evidence_vault.list_evidence(
        control_id=control_id,
        evidence_type=evidence_type,
        source=source
    )
    return evidence[:limit]


@app.get("/api/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Get details and content of specific evidence."""
    result = evidence_vault.retrieve_evidence(evidence_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    evidence, content = result
    
    # Try to decode content as JSON
    try:
        import json
        content_json = json.loads(content.decode('utf-8'))
        return {
            'evidence': evidence,
            'content': content_json
        }
    except:
        return {
            'evidence': evidence,
            'content': content.decode('utf-8', errors='replace')
        }


# === Dashboard Endpoints ===

@app.get("/api/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    """Get high-level compliance dashboard summary."""
    controls = evaluation_engine.list_controls(enabled_only=True)
    total_controls = len(controls)
    
    # Get latest evaluation for each control
    control_statuses = {}
    for control in controls:
        control_evals = [e for e in evaluations_db.values() if e.control_id == control.id]
        if control_evals:
            latest = max(control_evals, key=lambda e: e.evaluated_at)
            control_statuses[control.id] = latest.status
    
    passing = sum(1 for s in control_statuses.values() if s == "pass")
    failing = sum(1 for s in control_statuses.values() if s == "fail")
    warning = sum(1 for s in control_statuses.values() if s == "warning")
    
    # Count findings by severity
    open_findings = [f for f in findings_db.values() if f.status == "open"]
    critical_findings = sum(1 for f in open_findings if f.severity == Severity.CRITICAL)
    high_findings = sum(1 for f in open_findings if f.severity == Severity.HIGH)
    
    # Calculate compliance score
    if total_controls > 0:
        compliance_score = (passing / total_controls) * 100
    else:
        compliance_score = 0.0
    
    # Get last evaluation time
    if evaluations_db:
        last_eval = max(evaluations_db.values(), key=lambda e: e.evaluated_at)
        last_evaluation = last_eval.evaluated_at
    else:
        last_evaluation = None
    
    return DashboardSummary(
        total_controls=total_controls,
        passing_controls=passing,
        failing_controls=failing,
        warning_controls=warning,
        total_findings=len(open_findings),
        critical_findings=critical_findings,
        high_findings=high_findings,
        compliance_score=compliance_score,
        last_evaluation=last_evaluation
    )


@app.get("/api/dashboard/by-category")
async def get_dashboard_by_category():
    """Get compliance status broken down by TSC category."""
    controls = evaluation_engine.list_controls(enabled_only=True)
    
    by_category = {}
    
    for control in controls:
        category = control.category.value
        if category not in by_category:
            by_category[category] = {
                'total': 0,
                'passing': 0,
                'failing': 0,
                'warning': 0,
                'not_evaluated': 0
            }
        
        by_category[category]['total'] += 1
        
        # Get latest evaluation
        control_evals = [e for e in evaluations_db.values() if e.control_id == control.id]
        if control_evals:
            latest = max(control_evals, key=lambda e: e.evaluated_at)
            status = latest.status.value
            by_category[category][status] += 1
        else:
            by_category[category]['not_evaluated'] += 1
    
    # Calculate compliance score for each category
    for category_data in by_category.values():
        total = category_data['total']
        if total > 0:
            category_data['compliance_score'] = (category_data['passing'] / total) * 100
        else:
            category_data['compliance_score'] = 0.0
    
    return by_category


# === Connector Endpoints ===

@app.get("/api/connectors")
async def list_connectors():
    """List all configured connectors and their status."""
    connector_status = []
    for name, connector in connectors.items():
        success, message = connector.test_connection()
        connector_status.append({
            'name': name,
            'status': 'connected' if success else 'disconnected',
            'message': message,
            'last_sync': connector.last_sync
        })
    return connector_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
