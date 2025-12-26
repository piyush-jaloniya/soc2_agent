# SOC 2 AI Compliance Platform - Setup & Deployment Guide

## Overview

This is a production-grade SOC 2 compliance automation platform that provides:

- **Continuous Control Monitoring**: Automated evaluation of SOC 2 Trust Services Criteria
- **Evidence Collection**: Immutable evidence vault with integrity verification
- **Integration Framework**: Connectors for AWS, Okta, GitHub, and more
- **AI-Powered Analysis**: LLM-based policy drafting and anomaly detection (extensible)
- **Audit Readiness**: Generate compliance reports and evidence packages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web UI / Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│                         REST API                             │
│                    (FastAPI Backend)                         │
├─────────────────────────────────────────────────────────────┤
│  Control Evaluation Engine  │  Evidence Vault  │  LLM Service│
├─────────────────────────────────────────────────────────────┤
│              Connectors (AWS, Okta, GitHub, etc.)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Control Catalog** (`control_catalog/`)
   - YAML-based control definitions
   - Mapped to Trust Services Criteria
   - Rule-based evaluation logic

2. **Evaluation Engine** (`backend/services/evaluation_engine.py`)
   - Loads control definitions
   - Executes control checks
   - Generates findings for violations

3. **Evidence Vault** (`backend/services/evidence_vault.py`)
   - Immutable evidence storage
   - SHA-256 integrity verification
   - Organized by date and type

4. **Connectors** (`backend/connectors/`)
   - Modular integration framework
   - AWS, Okta, GitHub connectors (mock for demo)
   - Extensible to add more sources

5. **REST API** (`backend/api/main.py`)
   - FastAPI-based RESTful API
   - Endpoints for controls, evaluations, findings, evidence
   - Dashboard summary and analytics

6. **Web UI** (`frontend/templates/dashboard.html`)
   - Real-time compliance dashboard
   - Control status and findings view
   - Evidence browser

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/piyush-jaloniya/soc2_agent.git
cd soc2_agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Application Settings
APP_ENV=development
LOG_LEVEL=INFO

# Database (PostgreSQL for production)
DATABASE_URL=sqlite:///./soc2_compliance.db

# AWS Credentials (for AWS connector)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Okta Credentials (for Okta connector)
OKTA_DOMAIN=your-domain.okta.com
OKTA_API_TOKEN=your_api_token

# GitHub Credentials (for GitHub connector)
GITHUB_TOKEN=your_github_token

# OpenAI API Key (for LLM features)
OPENAI_API_KEY=your_openai_key
```

## Running the Application

### Development Mode

```bash
cd backend/api
python main.py
```

The API will be available at: `http://localhost:8000`

- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Production Mode

```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production deployment, use:
- **Gunicorn** with Uvicorn workers
- **Nginx** as reverse proxy
- **PostgreSQL** for database
- **Redis** for caching

## Using the Platform

### 1. Access the Dashboard

Navigate to `http://localhost:8000` in your browser.

### 2. Run an Evaluation

Click the "Run Compliance Evaluation" button to:
1. Collect data from all configured connectors
2. Evaluate all enabled controls
3. Generate findings for violations
4. Store evidence in the vault

### 3. Review Controls

The **Controls** tab shows all SOC 2 controls with:
- Control name and description
- TSC category (Security, Availability, etc.)
- Severity level
- Current status

### 4. Review Findings

The **Findings** tab displays:
- Open compliance issues
- Severity and affected resources
- Remediation recommendations

### 5. Browse Evidence

The **Evidence** tab shows:
- Collected evidence artifacts
- Source and collection time
- Evidence type (logs, configs, etc.)

## API Usage

### List Controls

```bash
curl http://localhost:8000/api/controls
```

### Run Evaluation

```bash
curl -X POST http://localhost:8000/api/evaluations/run \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Get Dashboard Summary

```bash
curl http://localhost:8000/api/dashboard/summary
```

### List Findings

```bash
curl http://localhost:8000/api/findings?status=open
```

## Adding New Controls

1. Edit `control_catalog/security_controls.yaml` (or create a new file)
2. Add control definition:

```yaml
- id: CC6.X-NEW-CONTROL
  name: "Control Name"
  description: "Control description"
  tsc_reference: "CC6.X"
  category: "Security"
  control_type: "Technical"
  sources:
    - "aws"
  logic:
    type: "boolean_check"
    query: |
      # Your check logic
    success_condition: "row_count = 0"
    failure_message: "Control failed"
  severity: "high"
  evaluation_frequency: "24h"
```

3. Restart the application to load the new control

## Adding New Connectors

1. Create a new connector class in `backend/connectors/`:

```python
from backend.connectors.base import BaseConnector

class MyServiceConnector(BaseConnector):
    def connect(self) -> bool:
        # Implement connection logic
        pass
    
    def collect_data(self) -> Dict[str, Any]:
        # Implement data collection
        pass
    
    def test_connection(self) -> tuple[bool, str]:
        # Implement connection test
        pass
```

2. Register the connector in `backend/api/main.py`:

```python
connectors['myservice'] = MyServiceConnector(config)
```

## Testing

Run tests (when test suite is implemented):

```bash
pytest tests/
```

## Security Considerations

### For Development

- The current implementation uses mock connectors with sample data
- Database is SQLite (in-memory)
- No authentication/authorization implemented

### For Production

**Critical security measures to implement:**

1. **Authentication & Authorization**
   - Implement JWT-based authentication
   - Role-based access control (RBAC)
   - API key management

2. **Secrets Management**
   - Use AWS Secrets Manager / Azure Key Vault
   - Never commit credentials to version control
   - Rotate credentials regularly

3. **Database Security**
   - Use PostgreSQL with encrypted connections
   - Implement database-level encryption
   - Regular backups with encryption

4. **Network Security**
   - Deploy behind a firewall
   - Use HTTPS/TLS for all connections
   - Implement rate limiting

5. **Connector Security**
   - Use least-privilege IAM roles
   - Read-only access where possible
   - Audit all connector activities

6. **Evidence Integrity**
   - The evidence vault uses SHA-256 hashing
   - Implement additional digital signatures
   - Use append-only storage

7. **LLM Security**
   - Implement data redaction before LLM calls
   - Consider self-hosted LLM for sensitive data
   - Audit all LLM interactions

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t soc2-agent .
docker run -p 8000:8000 -e DATABASE_URL=... soc2-agent
```

### Kubernetes Deployment

See `docs/kubernetes-deployment.md` for detailed Kubernetes configuration.

### Cloud Deployment

#### AWS
- Deploy on ECS or EKS
- Use RDS for PostgreSQL
- Use S3 for evidence vault
- Use Secrets Manager for credentials

#### Azure
- Deploy on AKS
- Use Azure Database for PostgreSQL
- Use Azure Blob Storage for evidence
- Use Azure Key Vault

#### GCP
- Deploy on GKE
- Use Cloud SQL for PostgreSQL
- Use Cloud Storage for evidence
- Use Secret Manager

## Monitoring & Logging

### Application Logs

Logs are written to stdout. In production, configure:
- **Log aggregation** (CloudWatch, Datadog, Splunk)
- **Error tracking** (Sentry)
- **APM** (New Relic, Datadog APM)

### Metrics to Monitor

- Control evaluation success rate
- Finding generation rate
- Evidence collection volume
- API response times
- Connector health

## Troubleshooting

### Issue: Controls not loading

**Solution**: Check that `control_catalog/*.yaml` files are valid YAML and in the correct location.

### Issue: Evaluation fails

**Solution**: Ensure connectors can access their respective services. Check credentials in `.env`.

### Issue: Evidence not stored

**Solution**: Check that `evidence_vault/` directory is writable. Verify disk space.

### Issue: API returns 500 errors

**Solution**: Check application logs for detailed error messages. Verify database connectivity.

## Roadmap

### MVP (Current)
- ✅ Core control catalog (Security TSC)
- ✅ Evaluation engine
- ✅ Evidence vault
- ✅ Mock connectors (AWS, Okta)
- ✅ REST API
- ✅ Web dashboard

### v1.0
- [ ] Real connector implementations (boto3, Okta API)
- [ ] Database persistence (PostgreSQL)
- [ ] LLM integration for policy drafting
- [ ] Auditor portal
- [ ] SOC 2 readiness reports

### v2.0
- [ ] Additional TSC categories (Availability, Confidentiality)
- [ ] Vendor risk management
- [ ] HR integration
- [ ] Advanced analytics
- [ ] Scheduled evaluations

### v3.0
- [ ] Processing Integrity & Privacy controls
- [ ] Multi-framework support (ISO 27001, NIST)
- [ ] AI compliance copilot
- [ ] Mobile app

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/piyush-jaloniya/soc2_agent/issues
- Documentation: See `docs/` directory

## License

See LICENSE file for details.
