# log-service
A Flask-based HTTP REST API service to read and filter logs from the /var/log directory. This service allows retrieving log entries from specified log files, filtering based on keywords, and limiting the number of entries returned. The newest log entries are returned first.

## Prerequisites
 - Python 3.10 or higher
 - Flask
 - pytest (for running tests)

## Installation
1. Clone repository
    ```sh
    git clone https://github.com/polarG/log-service.git
    ```
2. Install depenency
    ```sh
    cd log-service
    pip install -r requirements.txt
    ```

## Start Service
Start Flask server
```sh
python run
```
    
## API Endpoints
Endpoints
```sh
GET /logs
```
 - filename (required): The name of the log file within /var/log to read.
 - keyword (optional): A keyword to filter the log entries.
 - limit (optional): The number of log entries to retrieve. Defaults to 10 if not specified.
 - offset (optional): Start point. Defaults to 0 if not specified.
 
Example
```sh
GET /logs?filename=syslog&keyword=error&limit=5
```
Response
A JSON array containing the requested log entries in reverse chronological order (newest first).

Response example
```sh
{
    "IP": "192.168.36.252",
    "file": "/var/log/dpkg.log",
    "hostname": "laptopubuntuserver2",
    "offset": 10,
    "log": [
        "2024-06-25 20:13:26 status installed python3.10-venv:amd64 3.10.12-1~22.04.3",
        "2024-06-25 20:13:26 status half-configured python3.10-venv:amd64 3.10.12-1~22.04.3",
    ]
}
```

## Project Structure
```sh
log-service/
├── app.py               # Main Flask application
├── tests/               # Directory for tests
│   ├── __init__.py      # Init file for tests
│   ├── test_app.py      # Test cases for Flask application
├── requirements.txt     # Project dependencies
├── rsecondary.cfg       # configfile for  secondary servers 
└── README.md            # This README file
```

## Unit Test
Run test
```sh
pytest
```
To simulate the test file in /var/logs, please ensure that pytest is run using the root user.
