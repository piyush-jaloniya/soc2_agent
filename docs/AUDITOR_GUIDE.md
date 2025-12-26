# Auditor Guide - SOC 2 Compliance Platform

## Overview for Auditors

This platform automates SOC 2 compliance monitoring and evidence collection, providing:

- **Continuous Control Monitoring**: Controls are evaluated automatically at defined frequencies
- **Immutable Evidence**: All evidence is stored with SHA-256 integrity verification
- **Audit Trail**: Complete history of evaluations, findings, and remediation
- **Evidence Packages**: Easy export of evidence for specific controls and time periods

## Platform Capabilities

### What the Platform Provides

1. **Control Documentation**
   - Complete control catalog mapped to TSC
   - Control descriptions and evaluation logic
   - Evidence requirements for each control

2. **Automated Evidence Collection**
   - Configuration snapshots from cloud providers
   - Authentication logs from identity providers
   - Change management records from GitHub
   - System logs and metrics

3. **Continuous Evaluation**
   - Controls evaluated per defined schedule (hourly to weekly)
   - Findings generated for non-compliant items
   - Status tracking and trending

4. **Reporting**
   - Real-time compliance dashboard
   - Control status by TSC category
   - Finding severity and remediation status

### What Auditors Still Need to Do

1. **Validate Control Design**
   - Review control descriptions
   - Assess if controls address TSC requirements
   - Evaluate control effectiveness

2. **Sample Testing**
   - Select samples from automated evidence
   - Verify remediation of findings
   - Test manual controls

3. **Interview Key Personnel**
   - Confirm understanding of controls
   - Validate process adherence
   - Assess governance

4. **Review Documentation**
   - Policies and procedures
   - System descriptions
   - Risk assessments

## Accessing the Platform

### Read-Only Access

Auditors are provided read-only access to:
- Control catalog and evaluations
- Findings and remediation status
- Evidence vault
- Dashboard and reports

### Login

```
URL: https://soc2-platform.example.com/auditor
Username: auditor@auditfirm.com
Password: [Provided separately]
```

## Using the Platform for Audit

### 1. Understanding Controls

**Navigate to**: Controls Tab

Each control displays:
- **Control ID**: Unique identifier (e.g., CC6.1-IAM-MFA)
- **TSC Reference**: Maps to Trust Services Criteria
- **Description**: What the control checks
- **Category**: Security, Availability, etc.
- **Type**: Administrative, Technical, Physical
- **Severity**: Critical, High, Medium, Low
- **Frequency**: How often evaluated

**For Audit**:
- Review control descriptions against TSC requirements
- Verify control coverage is complete
- Document any gaps in control design

### 2. Reviewing Control Evaluations

**Navigate to**: API endpoint `/api/evaluations`

Each evaluation includes:
- **Timestamp**: When control was evaluated
- **Status**: Pass, Fail, Warning, Not Evaluated
- **Details**: Specific findings
- **Evidence IDs**: Links to supporting evidence

**For Audit**:
- Select sample evaluation dates
- Review evaluation results
- Verify findings are accurate

### 3. Examining Findings

**Navigate to**: Findings Tab

Findings represent control failures or warnings:
- **Severity**: Critical to Info
- **Description**: What failed
- **Resource**: Affected system/user
- **Remediation**: Recommended fix
- **Status**: Open, In Progress, Resolved
- **Timeline**: Discovered → Resolved

**For Audit**:
- Review critical and high findings
- Verify timely remediation
- Sample test resolved findings

### 4. Evidence Review

**Navigate to**: Evidence Tab or `/api/evidence`

Evidence types:
- **Config**: System configurations (JSON snapshots)
- **Log**: Audit and access logs
- **Policy**: Policy documents
- **Ticket**: Incident and change tickets
- **Report**: Backup reports, DR tests

Each evidence item includes:
- **Source**: Where it came from (AWS, Okta, etc.)
- **Collection Date**: When captured
- **Hash**: SHA-256 for integrity
- **Associated Controls**: Which controls use this evidence

**For Audit**:
- Download evidence samples
- Verify integrity with hash
- Cross-reference with findings

## Audit Procedures

### Type I (Point in Time)

**Objective**: Evaluate control design at a specific date

**Procedure**:
1. Review control catalog effective at audit date
2. Verify controls map to all applicable TSC
3. Assess if controls are appropriately designed
4. Review evidence collection methods
5. Document any design deficiencies

**Platform Support**:
- Control catalog with full descriptions
- Design documentation
- Evidence collection process

### Type II (Operating Effectiveness)

**Objective**: Test if controls operated effectively over the audit period

**Procedure**:
1. Define audit period (e.g., 6 months)
2. Select controls for testing
3. For each control:
   - Determine sample size (25-40 items typical)
   - Request evidence samples
   - Test samples for compliance
   - Document exceptions
4. Evaluate findings and remediation
5. Assess overall control effectiveness

**Platform Support**:
- Historical evaluations for entire period
- Evidence time-stamped and organized
- Finding lifecycle tracking
- Remediation verification

### Sample Selection

The platform supports various sampling methods:

#### Random Sampling
```bash
# Get 25 random evaluations for a control over audit period
GET /api/evaluations?control_id=CC6.1-IAM-MFA&limit=25&random=true
```

#### Date-Based Sampling
```bash
# Get evaluations from specific dates
GET /api/evaluations?control_id=CC6.1-IAM-MFA&dates=2024-01-15,2024-02-20,...
```

#### Event-Based Sampling
```bash
# Get all failing evaluations
GET /api/evaluations?control_id=CC6.1-IAM-MFA&status=fail
```

### Testing Examples

#### Example 1: MFA Enforcement

**Control**: CC6.1-IAM-MFA

**Test Objective**: Verify all privileged users have MFA enabled

**Procedure**:
1. Get list of all admin users from latest evaluation
2. Sample 25 users randomly
3. For each user:
   - Verify MFA is enabled in evidence
   - Check no exceptions granted
4. Document any users without MFA

**Platform Query**:
```bash
GET /api/controls/CC6.1-IAM-MFA/status
GET /api/evidence?control_id=CC6.1-IAM-MFA&type=config
```

#### Example 2: Encryption at Rest

**Control**: CC6.1-ENCRYPTION-AT-REST

**Test Objective**: Verify production databases are encrypted

**Procedure**:
1. Get list of production databases
2. Sample 20 databases
3. For each database:
   - Verify encryption enabled in config
   - Confirm encryption type (AES-256 or KMS)
4. Document unencrypted databases

**Platform Query**:
```bash
GET /api/findings?control_id=CC6.1-ENCRYPTION-AT-REST&severity=critical
GET /api/evidence?control_id=CC6.1-ENCRYPTION-AT-REST&source=aws_rds
```

#### Example 3: Change Management

**Control**: CC8.1-CHANGE-PR-REVIEW

**Test Objective**: Verify code changes are reviewed before production deployment

**Procedure**:
1. Get all merged PRs to main branch during audit period
2. Sample 40 PRs
3. For each PR:
   - Verify at least one approval
   - Confirm approval before merge
   - Check approver is authorized
4. Document PRs merged without review

**Platform Query**:
```bash
GET /api/evaluations?control_id=CC8.1-CHANGE-PR-REVIEW
GET /api/evidence?control_id=CC8.1-CHANGE-PR-REVIEW&source=github
```

## Evidence Export

### Exporting Evidence for Testing

**Option 1: API Export**
```bash
# Get specific evidence
GET /api/evidence/{evidence_id}

# Download evidence for control
GET /api/evidence?control_id=CC6.1-IAM-MFA&format=zip
```

**Option 2: Manual Download**
Evidence files are stored in:
```
evidence_vault/
  YYYY/MM/DD/
    evidence_type/
      {evidence_id}.json
```

### Evidence Package for Auditor

The platform can generate a complete evidence package:

```bash
POST /api/audit/evidence-package
{
  "audit_period_start": "2024-01-01",
  "audit_period_end": "2024-06-30",
  "controls": ["CC6.1-IAM-MFA", "CC6.1-ENCRYPTION-AT-REST", ...],
  "include_findings": true,
  "include_remediation": true
}
```

**Package Contents**:
- Control definitions
- All evaluations during period
- Associated evidence files
- Findings and remediation records
- Summary report

## Common Audit Questions

### Q: How do I verify evidence hasn't been tampered with?

**A**: Each evidence item has a SHA-256 hash. To verify:
1. Download the evidence file
2. Compute SHA-256 hash: `sha256sum evidence.json`
3. Compare with hash in metadata
4. Mismatch indicates tampering

### Q: How often are controls evaluated?

**A**: Each control has a defined frequency:
- Critical controls: Hourly
- High-severity: Every 24 hours
- Medium-severity: Every 24 hours
- Low-severity: Weekly

See individual control definitions for specifics.

### Q: What if a control fails?

**A**: When a control fails:
1. A finding is automatically created
2. Finding is assigned severity based on control
3. Remediation guidance is provided
4. Finding status is tracked until resolved

Auditors should review:
- Time to remediation
- Root cause
- Corrective actions taken

### Q: Can I see historical trends?

**A**: Yes. The dashboard shows:
- Compliance score over time
- Finding trends by severity
- Control pass rates

API also provides:
```bash
GET /api/dashboard/trends?start=2024-01-01&end=2024-06-30
```

### Q: Are manual controls supported?

**A**: Yes. Controls marked as `manual_review` require human verification. The platform:
- Identifies items needing review
- Creates review tasks
- Tracks completion

Auditors should test manual control execution through:
- Review of completed tasks
- Interviews with control owners
- Examination of supporting documentation

## Limitations and Considerations

### What the Platform Does Well

✅ Automates technical control monitoring
✅ Collects and organizes evidence
✅ Provides real-time visibility
✅ Ensures evidence integrity
✅ Tracks findings and remediation

### What Requires Auditor Judgment

⚠️ Control design effectiveness
⚠️ Appropriateness of evidence
⚠️ Adequacy of remediation
⚠️ Manual control testing
⚠️ Policy content review
⚠️ Management interview assessment
⚠️ Overall risk evaluation

## Reporting Audit Results

### Audit Findings Template

```
Control ID: CC6.1-IAM-MFA
Test Objective: Verify MFA enforcement for privileged users
Sample Size: 25 users
Exceptions: 2 users without MFA
Severity: High
Management Response: MFA enabled within 24 hours
Auditor Conclusion: Control operating effectively with minor exception
```

### Audit Report Sections

The platform supports audit report generation with:

1. **Executive Summary**
   - Overall compliance score
   - Key findings
   - Significant changes during period

2. **Control Testing Results**
   - Per-control test results
   - Sample sizes and methods
   - Exceptions noted

3. **Evidence Summary**
   - Evidence collected
   - Gaps identified
   - Recommendations

4. **Management Response**
   - Remediation plans
   - Timeline for resolution

## Support During Audit

### Technical Questions

**Platform Administrator**: admin@company.com
**Response Time**: Within 24 hours

### Evidence Requests

**Email**: compliance@company.com
**Include**:
- Control ID
- Evaluation date(s)
- Specific evidence needed
- Delivery format preference

### Access Issues

**IT Support**: support@company.com
**Available**: 24/7

## Additional Resources

- **Control Catalog Documentation**: `docs/CONTROL_CATALOG.md`
- **Setup Guide**: `docs/SETUP.md`
- **API Documentation**: https://soc2-platform.example.com/docs
- **AICPA TSC**: https://www.aicpa.org/soc2
