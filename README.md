# VLAN Management REST API

A Python REST API for managing VLANs in network infrastructure, built with FastAPI and designed for containerized deployment with Kubernetes.

## Features

- **Complete VLAN CRUD operations** - Create, Read, Update, Delete VLANs
- **OpenAPI specification** - Fully documented API with Swagger UI
- **Input validation** - Comprehensive validation for VLAN IDs, IP addresses, and subnets
- **JSON file storage** - Persistent data storage using JSON files
- **Health monitoring** - Built-in health check endpoint
- **Containerized** - Docker support with health checks
- **CI/CD pipeline** - Automated testing, building, and deployment
- **Kubernetes ready** - Complete K8s manifests with probes and resource limits
- **Test coverage** - Comprehensive test suite with 89% coverage

## API Endpoints

### VLAN Management
- `GET /api/v1/vlans` - List all VLANs
- `POST /api/v1/vlans` - Create a new VLAN
- `GET /api/v1/vlans/{id}` - Get specific VLAN by ID
- `PUT /api/v1/vlans/{id}` - Update VLAN
- `DELETE /api/v1/vlans/{id}` - Delete VLAN

### Monitoring
- `GET /health` - Health check endpoint

## Data Model

VLAN objects contain:
- **id**: Unique identifier (auto-generated)
- **name**: Human-readable name (max 100 characters)
- **vlan_id**: VLAN ID (1-4094)
- **subnet**: Subnet in CIDR notation (e.g., 192.168.1.0/24)
- **gateway**: Gateway IP address (must be within subnet)
- **status**: Current status (active, inactive, maintenance)

## Quick Start

### Development Prerequisites

- Python 3.11+

### Deployment Prerequisites

- Docker Hub account (for container registry)
- Google Cloud project with GKE enabled
- Kubernetes cluster (GKE recommended)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dp-user-repo/hw-smit-se-pub.git
   cd hw-smit-se-pub
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\\Scripts\\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - OpenAPI spec: http://localhost:8000/openapi.json

## Testing

### Testing Strategy

This project implements a **comprehensive layered testing approach** with 83 test cases across multiple layers:

#### **Test Coverage Overview**
- **Current coverage**: 89% 
- **Total test cases**: 82 tests across 5 test files
- **Architecture**: Tests follow the application's clean architecture layers

#### **Testing Layers**

**1. Unit Tests (64 tests - 78%)**

*Data Transfer Object Tests* (`test_models.py` - 13 tests):
- DTO validation and serialization
- Pydantic model validation rules
- Input format validation (IP addresses, CIDR notation)
- Field constraint testing (VLAN ID ranges, string lengths)

*Repository Layer Tests* (`test_repository.py` - 11 tests):
- JSON file storage operations
- CRUD operations on data layer
- Data persistence verification
- File system error handling

*Service Layer Tests* (`test_vlan_service.py` - 18 tests):
- Business logic validation using mocked repository
- VLAN conflict detection
- Business rule enforcement (unique VLAN IDs, gateway validation)
- Service-level error handling

*Error Handling Tests* (`test_error_handling.py` - 22 tests):
- HTTP status code validation
- Error response format validation
- Edge case error scenarios
- Health check failure simulation

**2. Integration Tests (18 tests - 22%)**

*API Integration Tests* (`test_api.py` - 18 tests):
- End-to-end API workflow testing
- Complete CRUD operations through HTTP endpoints
- Request/response validation
- Real database interactions with temporary storage

#### **Testing Philosophy**

**Layer-Specific Testing**: Each architecture layer is tested independently:
- **Unit tests** use mocks to isolate components
- **Integration tests** use real implementations with temporary storage
- **API tests** simulate real HTTP requests through FastAPI TestClient

**Data Isolation**: 
- Temporary files for each test to prevent data contamination
- Clean state between test runs
- Realistic test data matching production scenarios

**Comprehensive Error Coverage**:
- All HTTP error codes specified in OpenAPI
- Business rule violations (duplicate VLAN IDs, invalid networks)
- Infrastructure failures (storage unavailable)

**Business Logic Validation**:
- VLAN ID uniqueness enforcement
- Gateway-subnet relationship validation
- Network address format validation
- Status transition rules

#### **Test Categories by Functionality**

**VLAN CRUD Operations**: Complete coverage of all endpoints
- Create VLAN (POST /api/v1/vlans)
- Read VLANs (GET /api/v1/vlans, GET /api/v1/vlans/{id})
- Update VLAN (PUT /api/v1/vlans/{id})
- Delete VLAN (DELETE /api/v1/vlans/{id})

**Health Monitoring**: Health endpoint testing
- Healthy service responses
- Storage failure simulation
- Service unavailable scenarios

**Input Validation**: Comprehensive validation testing
- VLAN ID range validation (1-4094)
- IP address format validation
- CIDR subnet notation validation
- Required field validation

### Running Tests

#### Run all tests
```bash
pytest
```

#### Run tests with coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

#### Run specific test files
```bash
pytest tests/test_api.py         # API integration tests (18 tests)
pytest tests/test_error_handling.py # Error scenarios (21 tests)
pytest tests/test_models.py      # DTO validation tests (13 tests)  
pytest tests/test_repository.py  # Repository layer tests (11 tests)
pytest tests/test_vlan_service.py # Service logic tests (20 tests)
```

#### Run tests by functionality
```bash
pytest -k "test_create"     # VLAN creation tests
pytest -k "test_error"      # Error handling tests
pytest -k "test_health"     # Health check tests
pytest -k "test_validation" # Input validation tests
```

Coverage reports are generated in `htmlcov/index.html`.

### Accessing Coverage Reports

#### Local Coverage Reports
When running tests locally, coverage reports are generated in:
- **HTML Report**: `htmlcov/index.html` (open in browser)
- **Terminal Report**: Displayed in console output

#### CI/CD Coverage Reports
Coverage reports from the CI/CD pipeline are available as GitHub Actions artifacts:

1. **Navigate to Actions**: Go to [GitHub Actions](https://github.com/dp-user-repo/hw-smit-se-pub/actions)
2. **Select a Workflow Run**: Click on any successful "CI/CD Pipeline" run
3. **Download Artifacts**: Scroll down to "Artifacts" section
4. **Download**: Click "coverage-reports" to download the HTML coverage report
5. **View**: Extract the ZIP file and open `htmlcov/index.html` in your browser

**Alternative**: View coverage online at [Codecov](https://codecov.io/gh/dp-user-repo/hw-smit-se-pub)

### Accessing Build History

#### Pipeline Execution History
All CI/CD pipeline runs are publicly accessible:

1. **GitHub Actions Tab**: Visit [https://github.com/dp-user-repo/hw-smit-se-pub/actions](https://github.com/dp-user-repo/hw-smit-se-pub/actions)
2. **View All Runs**: See complete history of pipeline executions
3. **Check Status**: Successful builds, Failed builds, In progress
4. **View Details**: Click any run to see detailed logs for each step

#### What You Can See:
- **Build Results**: Test results, coverage percentages, deployment status
- **Console Logs**: Full output from tests, builds, and deployments  
- **Execution Time**: How long each step took
- **Commit Info**: Which code change triggered each build
- **Artifacts**: Downloadable build outputs and reports

## API Usage Examples

### Create a VLAN
```bash
curl -X POST "http://localhost:8000/api/v1/vlans" \\
     -H "Content-Type: application/json" \\
     -d '{
       "name": "Production Network",
       "vlan_id": 100,
       "subnet": "192.168.1.0/24",
       "gateway": "192.168.1.1",
       "status": "active"
     }'
```

### Get all VLANs
```bash
curl "http://localhost:8000/api/v1/vlans"
```

### Get specific VLAN
```bash
curl "http://localhost:8000/api/v1/vlans/1"
```

### Update a VLAN
```bash
curl -X PUT "http://localhost:8000/api/v1/vlans/1" \\
     -H "Content-Type: application/json" \\
     -d '{
       "name": "Updated Production Network",
       "status": "maintenance"
     }'
```

### Delete a VLAN
```bash
curl -X DELETE "http://localhost:8000/api/v1/vlans/1"
```

### Health check
```bash
curl "http://localhost:8000/health"
```

## Deployment

Deployment is fully automated via the CI/CD pipeline. When code is pushed to the `main` branch:

1. **Automated Process**: GitHub Actions builds, tests, and deploys automatically
2. **No Manual Steps**: No kubectl commands needed - everything is handled by the pipeline
3. **Live Application**: Access the deployed API at the external IP provided by the LoadBalancer service

### Environment Variables

The following environment variables are configured in the Kubernetes deployment:

- `PYTHONPATH`: Application path (default: `/app`)
- `PYTHONUNBUFFERED`: Enable unbuffered output (default: `1`)
- `DATA_FILE_PATH`: Path to VLAN data storage file

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline that:

1. **Test Stage**
   - Runs all tests with coverage requirements (≥70%)
   - Uploads coverage reports to Codecov

2. **Build Stage**
   - Builds Docker image with multi-platform support
   - Pushes to Docker registry with proper tagging

3. **Deploy Stage**
   - Updates Kubernetes deployment with new image
   - Verifies deployment rollout

### Required Secrets

Configure these secrets in your GitHub repository:

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password
- `GCP_SA_KEY`: Google Cloud service account key (JSON format)
- `GCP_PROJECT_ID`: Google Cloud project ID

## Architecture

The application follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │ Infrastructure  │
│                 │    │                 │    │                 │
│  FastAPI        │────│  Business       │────│  JSON           │
│  DTOs           │    │  Logic          │    │  Repository     │
│  Error Handlers │    │  Domain Rules   │    │  Data Access    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                     ┌─────────────────┐
                     │  Domain Layer   │
                     │                 │
                     │  Entities       │
                     │  Repositories   │
                     │  Exceptions     │
                     └─────────────────┘
```

### Architecture Layers

- **Domain Layer**: Core business entities and repository interfaces
- **Infrastructure Layer**: Data access implementations (JSON repository)
- **Service Layer**: Business logic orchestration and use cases
- **API Layer**: HTTP endpoints, DTOs, and error handling

### Design Patterns

- **Repository Pattern**: Abstracted data access layer
- **Service Layer Pattern**: Business logic separation
- **Dependency Injection**: Loose coupling with IoC container
- **Factory Pattern**: Object creation patterns
- **DTO Pattern**: Data transfer objects for API contracts

## Development

### Project Structure

```
hw-smit-se-pub/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API layer
│   │   ├── __init__.py
│   │   ├── dto.py          # Data Transfer Objects
│   │   ├── error_handlers.py # Error handling
│   │   ├── mappers.py      # Entity-DTO mapping
│   │   └── routes.py       # HTTP endpoints
│   ├── domain/             # Domain layer
│   │   ├── __init__.py
│   │   ├── entities.py     # Business entities
│   │   ├── exceptions.py   # Domain exceptions
│   │   └── repositories.py # Repository interfaces
│   ├── infrastructure/     # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── factories.py    # Factory patterns
│   │   └── repositories.py # Repository implementations
│   └── services/           # Service layer
│       ├── __init__.py
│       ├── dependency_injection.py # IoC container
│       └── vlan_service.py # Business logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py         # API endpoint tests
│   ├── test_error_handling.py # Error handling tests
│   ├── test_models.py      # DTO validation tests
│   ├── test_repository.py  # Repository layer tests
│   └── test_vlan_service.py # Service logic tests
├── k8s/                    # Kubernetes manifests
│   ├── configmap.yaml      # Configuration
│   ├── deployment.yaml     # Pod deployment
│   └── service.yaml        # Service definition
├── .github/workflows/      # CI/CD pipeline
│   ├── ci-cd.yml          # Main pipeline
│   ├── cleanup-gke.yml    # Cluster cleanup
│   └── setup-gke.yml      # Cluster setup
├── kodutoo.md             # Assignment documentation (Estonian)
├── openapi.yml            # OpenAPI specification
├── Dockerfile             # Container configuration
├── entrypoint.sh          # Data storage folder init for vlans.json
├── requirements.txt       # Python dependencies
├── pytest.ini             # Test configuration
├── vlans.json             # Local data storage
└── README.md              # This file
```

### Code Quality

- **Type hints**: Comprehensive type annotations for main functions and data models
- **Validation**: Comprehensive input validation with Pydantic
- **Error handling**: Proper HTTP status codes and error messages
- **Testing**: Unit and integration tests with pytest
- **Documentation**: OpenAPI/Swagger documentation

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Tests failing**
   ```bash
   # Clear pytest cache
   rm -rf .pytest_cache __pycache__ app/__pycache__ tests/__pycache__
   ```

### Verbose Logging

Run the application with verbose server logs:
```bash
python -m uvicorn app.main:app --reload --log-level debug
```

**Note**: This increases uvicorn's log verbosity.


## Support

For issues and questions:
1. Review the OpenAPI documentation at `/docs`
2. Check the health endpoint at `/health`