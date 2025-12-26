# Architecture Overview

## System Architecture

The SOC 2 AI Compliance Platform follows a modular, layered architecture designed for extensibility, security, and scalability.

```
┌────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                          │
├────────────────────────────────────────────────────────────────────┤
│  Web Dashboard (HTML/CSS/JS)     │   API Documentation (Swagger)  │
│  - Real-time compliance view     │   - OpenAPI specification      │
│  - Interactive controls browser  │   - Try-it-out interface       │
│  - Findings management           │                                │
│  - Evidence viewer               │                                │
└────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                          API LAYER (FastAPI)                       │
├────────────────────────────────────────────────────────────────────┤
│  REST API Endpoints:                                               │
│  • /api/controls         - Control catalog operations             │
│  • /api/evaluations      - Trigger and retrieve evaluations       │
│  • /api/findings         - Finding management                     │
│  • /api/evidence         - Evidence retrieval                     │
│  • /api/dashboard        - Summary and analytics                  │
│  • /api/connectors       - Connector status                       │
└────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                        BUSINESS LOGIC LAYER                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Control Evaluation  │  │  Evidence Vault  │  │ LLM Service  │ │
│  │      Engine         │  │                  │  │  (Future)    │ │
│  ├─────────────────────┤  ├──────────────────┤  ├──────────────┤ │
│  │ • Load controls     │  │ • Store evidence │  │ • Policy gen │ │
│  │ • Execute rules     │  │ • SHA-256 hash   │  │ • Narratives │ │
│  │ • Generate findings │  │ • Retrieval      │  │ • RAG query  │ │
│  │ • Track remediation │  │ • Integrity chk  │  │ • Analysis   │ │
│  └─────────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                      DATA COLLECTION LAYER                         │
├────────────────────────────────────────────────────────────────────┤
│                     Connector Framework                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │   AWS    │  │   Okta   │  │  GitHub  │  │   SIEM   │  ...    │
│  │ Connector│  │ Connector│  │ Connector│  │ Connector│         │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤         │
│  │ • IAM    │  │ • Users  │  │ • PRs    │  │ • Logs   │         │
│  │ • RDS    │  │ • Groups │  │ • Reviews│  │ • Alerts │         │
│  │ • S3     │  │ • MFA    │  │ • Issues │  │ • Events │         │
│  │ • Trail  │  │ • HR     │  │ • Commits│  │          │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE LAYER                          │
├────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Relational DB  │  │   Evidence Vault │  │  Vector DB      │ │
│  │   (PostgreSQL)   │  │   (Object Store) │  │  (Embeddings)   │ │
│  ├──────────────────┤  ├──────────────────┤  ├─────────────────┤ │
│  │ • Controls       │  │ • Configs        │  │ • Policies      │ │
│  │ • Evaluations    │  │ • Logs           │  │ • Narratives    │ │
│  │ • Findings       │  │ • Screenshots    │  │ • Documents     │ │
│  │ • Users/Resources│  │ • Reports        │  │ • Semantic      │ │
│  │ • Metadata       │  │ • Immutable      │  │   search        │ │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer

#### Web Dashboard
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Features**:
  - Real-time compliance score
  - Control status visualization
  - Finding management interface
  - Evidence browser
  - Responsive design
- **Communication**: RESTful API calls to backend

#### API Documentation
- **Technology**: OpenAPI/Swagger via FastAPI
- **Location**: http://localhost:8000/docs
- **Features**: Interactive API testing, schema documentation

### 2. API Layer

#### FastAPI REST API
- **Technology**: FastAPI (Python 3.9+)
- **Key Endpoints**:
  - `GET /api/controls` - List all controls
  - `POST /api/evaluations/run` - Execute evaluations
  - `GET /api/findings` - Retrieve findings
  - `GET /api/evidence` - Access evidence
  - `GET /api/dashboard/summary` - Dashboard data
- **Features**:
  - Async request handling
  - Pydantic validation
  - CORS support
  - Automatic API documentation

### 3. Business Logic Layer

#### Control Evaluation Engine
- **File**: `backend/services/evaluation_engine.py`
- **Responsibilities**:
  - Load control definitions from YAML catalog
  - Parse and validate control logic
  - Execute boolean checks against data context
  - Generate findings for violations
  - Track evaluation history
- **Logic Types**:
  - `boolean_check`: Deterministic pass/fail checks
  - `manual_review`: Flag items needing human review
  - `llm_based`: AI-powered analysis (extensible)

#### Evidence Vault
- **File**: `backend/services/evidence_vault.py`
- **Responsibilities**:
  - Store evidence immutably
  - Compute SHA-256 integrity hashes
  - Organize by date and type
  - Enable retrieval with integrity verification
  - Support evidence filtering and search
- **Storage Structure**:
  ```
  evidence_vault/
  ├── YYYY/MM/DD/
  │   ├── log/
  │   ├── config/
  │   ├── policy/
  │   └── report/
  └── metadata.json
  ```

#### LLM Service (Future)
- **Purpose**: AI-powered compliance assistance
- **Planned Features**:
  - Policy document generation
  - Compliance narrative creation
  - Anomaly detection and explanation
  - Natural language querying
  - Grounded RAG for accuracy

### 4. Data Collection Layer

#### Connector Framework
- **Base Class**: `backend/connectors/base.py`
- **Interface**:
  ```python
  class BaseConnector:
      def connect() -> bool
      def collect_data() -> Dict[str, Any]
      def test_connection() -> tuple[bool, str]
  ```

#### Implemented Connectors (MVP - Mock)

**AWS Connector**
- **Collects**:
  - IAM users and policies
  - RDS instances and encryption status
  - S3 buckets and public access settings
  - CloudTrail logging status
- **Technology**: Mock implementation (boto3 in production)

**Okta Connector**
- **Collects**:
  - User accounts and MFA status
  - Group memberships
  - HR employee data (for orphan detection)
- **Technology**: Mock implementation (Okta API in production)

#### Future Connectors
- GitHub (PRs, reviews, commits)
- Azure AD (users, groups, conditional access)
- GCP (IAM, GCS, Cloud SQL)
- Datadog/Splunk (logs, metrics)
- Jira/ServiceNow (tickets, incidents)

### 5. Data Storage Layer

#### Relational Database (PostgreSQL)
- **Current**: In-memory (MVP)
- **Production**: PostgreSQL with encryption
- **Schema**:
  - Controls and control definitions
  - Evaluations and results
  - Findings and remediation tracking
  - Users, resources, events
  - Audit logs

#### Evidence Vault (Object Storage)
- **Current**: Local filesystem
- **Production**: S3, Azure Blob, or GCS
- **Features**:
  - Immutable append-only storage
  - Versioning enabled
  - Server-side encryption
  - Lifecycle policies for retention

#### Vector Database (Future)
- **Purpose**: Semantic search and RAG
- **Technology**: pgvector, Qdrant, or Pinecone
- **Use Cases**:
  - Policy similarity search
  - Intelligent finding grouping
  - Natural language queries
  - Historical analysis

## Data Flow

### Evaluation Cycle

```
1. Trigger Evaluation (API call or schedule)
   │
   ▼
2. Collect Data from Connectors
   │
   ├─► AWS: IAM, RDS, S3, CloudTrail
   ├─► Okta: Users, MFA, HR
   └─► GitHub: PRs, Reviews
   │
   ▼
3. Store Data Snapshots as Evidence
   │
   ▼
4. Evaluate Each Control
   │
   ├─► Parse control logic
   ├─► Execute against data context
   ├─► Determine pass/fail status
   └─► Generate findings for violations
   │
   ▼
5. Store Evaluation Results
   │
   ▼
6. Update Dashboard Metrics
   │
   ▼
7. Return Results to Caller
```

### Evidence Collection Flow

```
1. Connector Collects Data
   │
   ▼
2. Serialize to JSON
   │
   ▼
3. Compute SHA-256 Hash
   │
   ▼
4. Generate Unique Evidence ID
   │
   ▼
5. Store in Vault (organized by date/type)
   │
   ▼
6. Save Metadata (with hash and location)
   │
   ▼
7. Link to Control Evaluations
```

## Security Architecture

### Authentication & Authorization
- **Current**: None (MVP)
- **Production Plan**:
  - JWT-based authentication
  - Role-based access control (RBAC)
  - API key management
  - SSO integration

### Secrets Management
- **Current**: Environment variables
- **Production Plan**:
  - AWS Secrets Manager / Azure Key Vault
  - Encrypted at rest and in transit
  - Automatic rotation
  - Audit logging

### Network Security
- **Production Requirements**:
  - TLS/HTTPS for all connections
  - Private VPC deployment
  - Security groups / network policies
  - Rate limiting and DDoS protection

### Data Security
- **Evidence Integrity**: SHA-256 hashing
- **Database Encryption**: TDE for PostgreSQL
- **Storage Encryption**: SSE for object storage
- **Tenant Isolation**: Multi-tenant safe design

## Scalability Considerations

### Horizontal Scaling
- API layer: Multiple instances behind load balancer
- Connector workers: Distributed task queue (Celery/RQ)
- Evidence storage: Cloud object storage auto-scales

### Performance Optimization
- **Caching**: Redis for frequently accessed data
- **Async I/O**: FastAPI async endpoints
- **Batch Processing**: Bulk evaluation of controls
- **Indexing**: Database indexes on common queries

### Monitoring & Observability
- **Metrics**: Prometheus + Grafana
- **Logging**: Structured logging to CloudWatch/Datadog
- **Tracing**: OpenTelemetry for distributed tracing
- **Alerting**: PagerDuty for critical issues

## Deployment Architecture

### Development
```
Local Machine
├── FastAPI Server (port 8000)
├── In-memory database
└── Local evidence vault
```

### Production (Recommended)
```
┌─────────────────────────────────────────┐
│          Load Balancer (ALB)            │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌────────┐     ┌────────┐     ┌────────┐
│API Srv │     │API Srv │     │API Srv │
│  Pod   │     │  Pod   │     │  Pod   │
└────────┘     └────────┘     └────────┘
    │               │               │
    └───────────────┼───────────────┘
                    ▼
    ┌───────────────────────────────────┐
    │   PostgreSQL (RDS/Cloud SQL)      │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │  Evidence Vault (S3/Blob/GCS)     │
    └───────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │    Task Queue (SQS/Pub/Sub)       │
    └───────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌────────┐     ┌────────┐     ┌────────┐
│Worker  │     │Worker  │     │Worker  │
│  Pod   │     │  Pod   │     │  Pod   │
└────────┘     └────────┘     └────────┘
```

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: FastAPI 0.104+
- **Validation**: Pydantic 2.5+
- **Database**: PostgreSQL (via SQLAlchemy)
- **HTTP Client**: httpx
- **YAML**: PyYAML

### Frontend
- **HTML5** with semantic markup
- **CSS3** with custom properties
- **Vanilla JavaScript** (no frameworks for simplicity)

### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes (production)
- **Cloud**: AWS/Azure/GCP compatible
- **CI/CD**: GitHub Actions (future)

### Future Additions
- **LLM**: OpenAI API / Self-hosted LLaMA
- **Vector DB**: pgvector or Qdrant
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Monitoring**: Prometheus + Grafana

## Extension Points

### Adding New Controls
1. Define control in YAML (`control_catalog/*.yaml`)
2. No code changes needed
3. Engine auto-loads on restart

### Adding New Connectors
1. Implement `BaseConnector` interface
2. Register in `backend/api/main.py`
3. Add credentials to environment

### Adding New TSC Categories
1. Create new YAML file (e.g., `availability_controls.yaml`)
2. Place in `control_catalog/`
3. Engine auto-loads

### Customizing Evaluation Logic
1. Add new logic type in `evaluation_engine.py`
2. Implement evaluation method
3. Use in control YAML definitions

## Future Enhancements

### Phase 1 (v1.0)
- Real connectors (boto3, Okta API, GitHub API)
- PostgreSQL persistence
- Scheduled evaluation jobs
- Auditor evidence packages

### Phase 2 (v2.0)
- LLM integration for policy drafting
- Additional TSC categories
- Vendor risk management
- Advanced analytics

### Phase 3 (v3.0)
- Multi-framework support (ISO 27001, NIST)
- AI compliance copilot
- Mobile application
- Multi-tenant SaaS
