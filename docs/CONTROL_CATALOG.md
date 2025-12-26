# Control Catalog Documentation

## Overview

The control catalog is the foundation of the SOC 2 compliance platform. It defines:

- **What** controls need to be evaluated
- **How** to evaluate them (logic and queries)
- **When** to evaluate them (frequency)
- **Why** they matter (TSC mapping and severity)

## Control Structure

Each control is defined in YAML format with the following fields:

### Required Fields

```yaml
id: "CC6.1-IAM-MFA"                    # Unique identifier
name: "Multi-Factor Authentication"    # Human-readable name
description: "Detailed description"    # What the control checks
tsc_reference: "CC6.1"                 # TSC reference (e.g., CC6.1, A1.2)
category: "Security"                   # TSC category
control_type: "Technical"              # Administrative, Technical, or Physical
sources: ["okta", "aws_iam"]           # Required data sources
logic:                                 # Evaluation logic
  type: "boolean_check"                # Logic type
  query: "SELECT ..."                  # Check query
  success_condition: "row_count = 0"   # Success criteria
severity: "high"                       # critical, high, medium, low, info
evaluation_frequency: "1h"             # How often to run
```

### Optional Fields

```yaml
enabled: true                          # Whether control is active
remediation: "Steps to fix..."         # Remediation guidance
threshold: 5                           # Custom threshold for checks
```

## TSC Category Mapping

### Security (Common Criteria - CC)

**Mandatory for all SOC 2 reports**

Controls in this category focus on:
- Information security policies and procedures
- Access control and authentication
- Logical and physical security
- System operations and change management
- Risk assessment and mitigation

**Key TSC References:**
- **CC1**: Control Environment
- **CC2**: Communication and Information
- **CC3**: Risk Assessment
- **CC4**: Monitoring Activities
- **CC5**: Control Activities
- **CC6**: Logical and Physical Access Controls
- **CC7**: System Operations
- **CC8**: Change Management
- **CC9**: Risk Mitigation

### Availability (A)

Controls ensuring system uptime and accessibility:
- Infrastructure availability
- Disaster recovery and business continuity
- Capacity management
- Backup and restoration

**Key TSC References:**
- **A1**: Availability commitments and system requirements

### Confidentiality (C)

Controls protecting confidential information:
- Data classification
- Encryption (at rest and in transit)
- Secure disposal
- Access restrictions

**Key TSC References:**
- **C1**: Confidentiality commitments

### Processing Integrity (PI)

Controls ensuring accurate and complete processing:
- Input validation
- Processing completeness
- Data reconciliation
- Error handling

**Key TSC References:**
- **PI1**: Processing integrity commitments

### Privacy (P)

Controls protecting personal information:
- Privacy policies
- Data subject rights (DSAR)
- Data minimization
- Cross-border transfers

**Key TSC References:**
- **P1-P8**: Privacy principles

## Control Types

### Administrative Controls

**Definition**: Policies, procedures, and processes that govern security

**Examples:**
- Information security policy
- Incident response procedures
- Risk assessment process
- Vendor management workflow
- Security awareness training

**Evaluation**: Often require manual review or document verification

### Technical Controls

**Definition**: Technology-based controls that enforce security

**Examples:**
- MFA enforcement
- Encryption at rest/in transit
- Firewall rules
- Logging and monitoring
- Backup automation

**Evaluation**: Automated checks against system configurations

### Physical Controls

**Definition**: Physical security measures

**Examples:**
- Badge access systems
- CCTV surveillance
- Data center security
- Secure disposal

**Evaluation**: Usually evidenced through 3rd party attestations (e.g., data center SOC 2)

## Logic Types

### boolean_check

**Use for**: Deterministic yes/no checks

**Structure:**
```yaml
logic:
  type: "boolean_check"
  query: |
    # SQL-like query that returns violations
    SELECT user_id, email
    FROM users
    WHERE is_admin = TRUE AND mfa_enabled = FALSE
  success_condition: "row_count = 0"
  threshold: 0
  failure_message: "Found {count} violations"
```

**Success Conditions:**
- `row_count = 0`: No violations
- `row_count <= threshold`: Violations within acceptable limit
- `value >= minimum`: Numeric threshold

### manual_review

**Use for**: Controls requiring human judgment

**Structure:**
```yaml
logic:
  type: "manual_review"
  query: |
    # Query to identify items needing review
    SELECT incident_id, created_at
    FROM security_incidents
    WHERE status = 'open' AND age_days > 30
  success_condition: "manual_verification"
```

**Result**: Generates review tasks, not automatic pass/fail

### llm_based

**Use for**: Controls requiring AI analysis (future)

**Structure:**
```yaml
logic:
  type: "llm_based"
  prompt: "Analyze this policy for SOC 2 compliance..."
  grounding_data: ["policies", "procedures"]
```

## Severity Levels

### Critical

- **Impact**: Data breach, system compromise, regulatory violation
- **Examples**: Public S3 buckets, no encryption on sensitive data
- **Response**: Immediate remediation required

### High

- **Impact**: Significant security risk, audit failure
- **Examples**: Admin without MFA, CloudTrail disabled
- **Response**: Remediate within 24-48 hours

### Medium

- **Impact**: Potential security gap, best practice violation
- **Examples**: Insufficient backup retention, missing logging
- **Response**: Remediate within 1 week

### Low

- **Impact**: Minor gap, optimization opportunity
- **Examples**: Non-standard configuration, documentation gaps
- **Response**: Plan for remediation

### Info

- **Impact**: No immediate risk, informational
- **Examples**: Manual review reminders, policy review dates
- **Response**: For awareness only

## Evaluation Frequency

### Real-time (continuous)

```yaml
evaluation_frequency: "continuous"
```
Use for critical controls that need immediate detection

### Hourly

```yaml
evaluation_frequency: "1h"
```
Use for high-severity controls (MFA, public access)

### Daily

```yaml
evaluation_frequency: "24h"
```
Use for most technical controls (standard frequency)

### Weekly

```yaml
evaluation_frequency: "168h"
```
Use for administrative controls and reviews

### Monthly

```yaml
evaluation_frequency: "720h"
```
Use for policy reviews and attestations

## Creating New Controls

### Step 1: Identify the Control

1. Determine which TSC it maps to
2. Define what you're checking
3. Identify required data sources

### Step 2: Define the Control

Create YAML definition:

```yaml
- id: CC7.X-UNIQUE-ID
  name: "Control Name"
  description: "What this control checks and why it matters"
  tsc_reference: "CC7.X"
  category: "Security"
  control_type: "Technical"
  sources:
    - "data_source_1"
    - "data_source_2"
  logic:
    type: "boolean_check"
    query: |
      # Your evaluation logic
      SELECT resource_id
      FROM resources
      WHERE condition = true
    success_condition: "row_count = 0"
    failure_message: "Found {count} violations"
  severity: "high"
  evaluation_frequency: "24h"
  remediation: "How to fix violations"
```

### Step 3: Test the Control

1. Add control to catalog file
2. Restart the application
3. Run evaluation
4. Verify findings are accurate

### Step 4: Document the Control

Add to audit documentation:
- Control objective
- Control activities
- Evidence requirements
- Testing procedures

## Example Controls

### Access Control Example

```yaml
- id: CC6.1-IAM-MFA
  name: "Multi-Factor Authentication for Privileged Users"
  description: "All users with administrative or privileged access must have MFA enabled."
  tsc_reference: "CC6.1"
  category: "Security"
  control_type: "Technical"
  sources: ["okta", "azure_ad"]
  logic:
    type: "boolean_check"
    query: |
      SELECT user_id, email, role
      FROM users
      WHERE is_admin = TRUE AND mfa_enabled = FALSE
    success_condition: "row_count = 0"
    failure_message: "Found {count} privileged users without MFA"
  severity: "high"
  evaluation_frequency: "1h"
  remediation: "Enable MFA for all users with administrative privileges."
```

### Encryption Example

```yaml
- id: CC6.1-ENCRYPTION-S3
  name: "S3 Bucket Encryption"
  description: "All S3 buckets must have default encryption enabled."
  tsc_reference: "CC6.1"
  category: "Security"
  control_type: "Technical"
  sources: ["aws_s3"]
  logic:
    type: "boolean_check"
    query: |
      SELECT bucket_name
      FROM s3_buckets
      WHERE default_encryption = FALSE
    success_condition: "row_count = 0"
    failure_message: "Found {count} unencrypted S3 buckets"
  severity: "critical"
  evaluation_frequency: "24h"
  remediation: "Enable default encryption (AES-256 or KMS) on all S3 buckets."
```

### Change Management Example

```yaml
- id: CC8.1-CHANGE-PR-REVIEW
  name: "Code Review for Production Changes"
  description: "All production code changes must be reviewed and approved."
  tsc_reference: "CC8.1"
  category: "Security"
  control_type: "Administrative"
  sources: ["github"]
  logic:
    type: "boolean_check"
    query: |
      SELECT pr_id, pr_title
      FROM pull_requests
      WHERE merged_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
        AND target_branch = 'main'
        AND review_count < 1
    success_condition: "row_count = 0"
    failure_message: "Found {count} PRs merged without review"
  severity: "high"
  evaluation_frequency: "24h"
  remediation: "Enforce branch protection rules requiring at least one approval."
```

## Control Catalog Files

### Organization

```
control_catalog/
├── security_controls.yaml       # Common Criteria (CC) controls
├── availability_controls.yaml   # Availability controls (future)
├── confidentiality_controls.yaml # Confidentiality controls (future)
├── processing_integrity_controls.yaml
└── privacy_controls.yaml
```

### Loading Controls

The evaluation engine automatically loads all controls from the catalog on startup:

```python
from backend.services.evaluation_engine import ControlEvaluationEngine

engine = ControlEvaluationEngine()
controls = engine.list_controls()
```

## Best Practices

1. **Be Specific**: Clearly define what the control checks
2. **Be Measurable**: Use objective criteria for pass/fail
3. **Map to TSC**: Every control should map to a TSC reference
4. **Provide Remediation**: Include clear steps to fix violations
5. **Test Thoroughly**: Verify controls work before production
6. **Document Evidence**: Specify what evidence proves compliance
7. **Version Control**: Track control changes in git
8. **Review Regularly**: Update controls as requirements change

## References

- [AICPA Trust Services Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html)
- [SOC 2 Implementation Guide](https://www.aicpa.org/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
