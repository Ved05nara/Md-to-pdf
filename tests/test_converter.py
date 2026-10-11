# pyrefly: ignore [missing-import]
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_healthcheck(client):
    """Requirement: Healthcheck route verification (200 OK)"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_convert_valid_markdown(client):
    """Requirement: Conversion success checks for Content-Type: application/pdf"""
    payload = {"markdown": "# Test Heading\n\nThis is sample body markdown."}
    response = client.post('/convert', json=payload)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert len(response.data) > 0

def test_convert_empty_payload(client):
    """Requirement: Validation tests for missing/empty input (400 Bad Request)"""
    payload = {"markdown": "   "}
    response = client.post('/convert', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()