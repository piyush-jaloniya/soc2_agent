# SOC 2 Compliance Platform - Quick Reference

## Quick Start

```bash
# Clone and setup
git clone https://github.com/piyush-jaloniya/soc2_agent.git
cd soc2_agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
./run.sh
# Or: PYTHONPATH=$(pwd) python backend/api/main.py

# Access dashboard
open http://localhost:8000
```

## API Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### List All Controls
```bash
curl http://localhost:8000/api/controls | jq
```

### Get Control Details
```bash
curl http://localhost:8000/api/controls/CC6.1-IAM-MFA | jq
```

### Run Evaluation
```bash
curl -X POST http://localhost:8000/api/evaluations/run \
  -H "Content-Type: application/json" \
  -d '{"force": true}' | jq
```

### Get Dashboard Summary
```bash
curl http://localhost:8000/api/dashboard/summary | jq
```

### List Open Findings
```bash
curl http://localhost:8000/api/findings?status=open | jq
```

### List Evidence
```bash
curl http://localhost:8000/api/evidence?limit=10 | jq
```

### Get Evidence by ID
```bash
curl http://localhost:8000/api/evidence/{evidence_id} | jq
```

### Check Connectors
```bash
curl http://localhost:8000/api/connectors | jq
```

## Control Catalog Reference

### Control Structure
```yaml
- id: "CC6.1-IAM-MFA"           # Unique ID
  name: "Control Name"           # Display name
  description: "What it checks"  # Full description
  tsc_reference: "CC6.1"         # TSC mapping
  category: "Security"           # TSC category
  control_type: "Technical"      # Type
  sources: ["okta", "aws"]       # Data sources
  logic:
    type: "boolean_check"        # Logic type
    query: "SELECT ..."          # Check query
    success_condition: "..."     # Pass criteria
  severity: "high"               # Severity
  evaluation_frequency: "1h"     # Frequency
```

### TSC Categories
- **Security** (CC) - Mandatory
- **Availability** (A) - Optional
- **Confidentiality** (C) - Optional
- **Processing Integrity** (PI) - Optional
- **Privacy** (P) - Optional

### Severity Levels
- **critical** - Immediate risk (data breach, system compromise)
- **high** - Significant risk (audit failure, security gap)
- **medium** - Potential gap (best practice violation)
- **low** - Minor issue (optimization opportunity)
- **info** - Informational only

### Control Types
- **Administrative** - Policies, procedures, governance
- **Technical** - Technology-based controls (MFA, encryption)
- **Physical** - Physical security (badge access, CCTV)

## File Structure

```
soc2_agent/
├── backend/
│   ├── api/main.py                    # FastAPI application
│   ├── models/__init__.py             # Data models
│   ├── services/
│   │   ├── evaluation_engine.py       # Control evaluation
│   │   └── evidence_vault.py          # Evidence storage
│   └── connectors/
│       ├── base.py                    # Connector interface
│       ├── aws_connector.py           # AWS integration
│       └── okta_connector.py          # Okta integration
├── control_catalog/
│   └── security_controls.yaml         # Control definitions
├── frontend/templates/
│   └── dashboard.html                 # Web UI
├── docs/
│   ├── SETUP.md                       # Setup guide
│   ├── CONTROL_CATALOG.md             # Control guide
│   ├── AUDITOR_GUIDE.md               # Auditor guide
│   └── ARCHITECTURE.md                # Architecture
├── requirements.txt                    # Python deps
├── run.sh                             # Run script
└── README.md                          # Main docs
```

## Environment Variables

```bash
# Application
APP_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost/soc2_db

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Okta
OKTA_DOMAIN=your-domain.okta.com
OKTA_API_TOKEN=your_token

# GitHub
GITHUB_TOKEN=your_github_token

# OpenAI
OPENAI_API_KEY=your_openai_key
```

## Common Tasks

### Add a New Control

1. Edit `control_catalog/security_controls.yaml`:
```yaml
- id: CC6.X-NEW-CONTROL
  name: "My New Control"
  description: "What this checks"
  tsc_reference: "CC6.X"
  category: "Security"
  control_type: "Technical"
  sources: ["aws"]
  logic:
    type: "boolean_check"
    query: "SELECT ..."
    success_condition: "row_count = 0"
  severity: "high"
  evaluation_frequency: "24h"
```

2. Restart application
3. Control auto-loads

### Add a New Connector

1. Create `backend/connectors/myservice_connector.py`:
```python
from backend.connectors.base import BaseConnector

class MyServiceConnector(BaseConnector):
    def connect(self):
        # Connect logic
        return True
    
    def collect_data(self):
        # Collection logic
        return {'users': [...]}
    
    def test_connection(self):
        return True, "Connected"
```

2. Register in `backend/api/main.py`:
```python
connectors['myservice'] = MyServiceConnector(config)
```

3. Restart application

### View Logs

```bash
# If using run.sh
tail -f /tmp/server.log

# If running in terminal
# Logs output to stdout
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Import Errors
```bash
# Set PYTHONPATH
export PYTHONPATH=$(pwd)
python backend/api/main.py
```

### Controls Not Loading
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('control_catalog/security_controls.yaml'))"
```

### Evidence Not Storing
```bash
# Check permissions
ls -la evidence_vault/
chmod -R 755 evidence_vault/
```

## Testing

### Test Models
```bash
python -c "from backend.models import Control; print('✓ Models OK')"
```

### Test Evaluation Engine
```bash
python -c "from backend.services.evaluation_engine import ControlEvaluationEngine; e = ControlEvaluationEngine(); print(f'✓ Loaded {len(e.controls)} controls')"
```

### Test Evidence Vault
```bash
python -c "from backend.services.evidence_vault import EvidenceVault; v = EvidenceVault(); print('✓ Vault OK')"
```

### Test API
```bash
# Start server in background
PYTHONPATH=$(pwd) python backend/api/main.py &
sleep 5

# Test endpoints
curl -s http://localhost:8000/health | jq
curl -s http://localhost:8000/api/controls | jq '. | length'

# Stop server
kill %1
```

## Performance Tips

### Optimize Evaluations
- Filter controls by severity
- Run only changed controls
- Use caching for static data

### Evidence Management
- Set retention policies
- Archive old evidence
- Use compression

### API Performance
- Enable response caching
- Use pagination
- Limit results with `?limit=N`

## Security Checklist

- [ ] Change default credentials
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication
- [ ] Use secrets manager
- [ ] Enable audit logging
- [ ] Restrict connector permissions
- [ ] Enable database encryption
- [ ] Set up firewalls
- [ ] Regular security updates
- [ ] Backup evidence vault

## Resources

- **AICPA SOC 2**: https://www.aicpa.org/soc2
- **Trust Services Criteria**: https://www.aicpa.org/trust-services-criteria
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **AWS Security**: https://aws.amazon.com/security/best-practices/
- **NIST Framework**: https://www.nist.gov/cyberframework

## Support

- **Issues**: https://github.com/piyush-jaloniya/soc2_agent/issues
- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/docs

## License

See LICENSE file for details.
