## Test Suite for Vila Acadia

Comprehensive test suite for the Vila Acadia timesheet system.

### 📋 Test Structure

```
tests/
├── __init__.py           # Test package init
├── conftest.py           # Pytest fixtures and configuration
├── test_api_endpoints.py # API endpoint integration tests
├── test_gsheets_service.py # Google Sheets service unit tests
├── test_models.py        # Pydantic model validation tests
├── test_config.py        # Configuration management tests
└── README.md             # This file
```

### 🚀 Running Tests

#### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock httpx
```

#### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=src/backend --cov-report=html --cov-report=term
```

#### Run Specific Test Files

```bash
# Test API endpoints only
pytest tests/test_api_endpoints.py

# Test Google Sheets service only
pytest tests/test_gsheets_service.py

# Test models only
pytest tests/test_models.py
```

#### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/test_api_endpoints.py::TestAuthEndpoint

# Run specific test method
pytest tests/test_api_endpoints.py::TestAuthEndpoint::test_auth_success

# Run tests matching pattern
pytest -k "test_auth"
```

### 📊 Test Coverage

The test suite covers:

#### API Endpoints (test_api_endpoints.py)
- ✅ Root endpoint (`/`)
- ✅ Health check endpoint (`/health`)
- ✅ Authentication endpoint (`/auth/verify`)
- ✅ Hours submission endpoint (`/submit-hours`)
- ✅ Daily tip submission endpoint (`/manager/submit-daily-tip`)

#### Google Sheets Service (test_gsheets_service.py)
- ✅ Service initialization
- ✅ Health check functionality
- ✅ Employee settings retrieval
- ✅ PIN verification (case-insensitive)
- ✅ Time calculations (including overnight shifts)
- ✅ Month closure validation
- ✅ Column helper methods
- ✅ Date column management
- ✅ Employee row management

#### Models (test_models.py)
- ✅ AuthRequest/Response validation
- ✅ HoursSubmissionRequest/Response validation
- ✅ DailyTipRequest/Response validation
- ✅ HealthResponse validation
- ✅ Date format validation
- ✅ Time format validation
- ✅ PIN format validation
- ✅ Numeric constraints

#### Configuration (test_config.py)
- ✅ Settings initialization
- ✅ Environment variable loading
- ✅ JSON validation
- ✅ Default values

### 🎯 Test Categories

#### Unit Tests
Test individual functions and methods in isolation with mocked dependencies.
- `test_gsheets_service.py`
- `test_models.py`
- `test_config.py`

#### Integration Tests
Test multiple components working together.
- `test_api_endpoints.py` (FastAPI + models + service)

### 🔧 Test Fixtures

Defined in `conftest.py`:

- `mock_spreadsheet` - Mock Google Spreadsheet
- `mock_worksheet` - Mock Google Worksheet
- `mock_settings_data` - Mock employee settings
- `mock_gsheets_service` - Fully mocked Google Sheets service
- `test_client` - FastAPI test client
- `sample_hours_request` - Sample hours submission data
- `sample_tip_request` - Sample tip submission data

### 📝 Writing New Tests

#### Example: Adding a New API Test

```python
def test_my_new_endpoint(test_client, mock_gsheets_service):
    """Test my new endpoint functionality."""
    response = test_client.post("/my-endpoint", json={
        "field": "value"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

#### Example: Adding a New Service Test

```python
def test_my_new_service_method(service, mock_worksheet):
    """Test my new service method."""
    result = service.my_new_method("param")
    
    assert result is not None
    mock_worksheet.some_method.assert_called_once()
```

### 🐛 Debugging Tests

#### Run with Print Statements

```bash
pytest -s tests/test_api_endpoints.py
```

#### Run with Debugger

```bash
pytest --pdb tests/test_api_endpoints.py
```

#### Show Test Duration

```bash
pytest --durations=10
```

### ✅ Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (Google Sheets API)
3. **Descriptive Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Edge Cases**: Test both happy paths and error cases
6. **Coverage**: Aim for >80% code coverage

### 🔍 Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=src/backend --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)

