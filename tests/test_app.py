import os
import pytest
from app import app

@pytest.fixture
def client():
    # print('test start')
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Ensure test log directory exists
    os.makedirs('/var/log', exist_ok=True)
    
    # Create a sample log file for testing
    test_log_file = '/var/log/testlog'
    with open(test_log_file, 'w') as f:
        f.write(
            '2024-06-22T12:34:56Z Error: Something went wrong\n'
            '2024-06-22T12:33:45Z Info: Just an info message\n'
            '2024-06-22T12:32:30Z Error: Another issue detected\n'
        )
    
    yield client
    
    # Clean up test log file after test
    os.remove(test_log_file)

def test_get_logs(client):
    response = client.get('/logs?filename=testlog&keyword=Error&limit=2')
    assert response.status_code == 200
    data = response.get_json()[0]['log']
    print(data)
    assert len(data) == 2
    assert data[0] == '2024-06-22T12:32:30Z Error: Another issue detected'
    assert data[1] == '2024-06-22T12:34:56Z Error: Something went wrong'

def test_get_logs_no_keyword(client):
    response = client.get('/logs?filename=testlog&limit=2')
    assert response.status_code == 200
    data = response.get_json()[0]['log']
    assert len(data) == 2
    assert data[0] == '2024-06-22T12:32:30Z Error: Another issue detected'
    assert data[1] == '2024-06-22T12:33:45Z Info: Just an info message'

def test_get_logs_file_not_found(client):
    response = client.get('/logs?filename=nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_get_logs_no_filename(client):
    response = client.get('/logs')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
