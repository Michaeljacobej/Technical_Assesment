# Backend Developer Technical Assessment

## Overview

A data pipeline with 3 Docker services:

- **Flask API** (port 5000) — Mock customer data server serving 22 customers from a JSON file
- **FastAPI** (port 8000) — Data ingestion pipeline that fetches from Flask and stores in PostgreSQL
- **PostgreSQL** (port 5432) — Persistent data storage

**Flow:** Flask (JSON) → FastAPI (Ingest) → PostgreSQL → API Response

## Prerequisites

- Docker Desktop (running)
- Python 3.10+
- Git

## Quick Start

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

## API Endpoints

### Flask Mock Server (port 5000)

| Endpoint | Method | Description |
|---|---|---|
| `/api/customers` | GET | Paginated list (`page`, `limit` params) |
| `/api/customers/{id}` | GET | Single customer by ID |
| `/api/health` | GET | Health check |

### FastAPI Pipeline Service (port 8000)

| Endpoint | Method | Description |
|---|---|---|
| `/api/ingest` | POST | Fetch Flask data → upsert into PostgreSQL |
| `/api/customers` | GET | Paginated list from database |
| `/api/customers/{id}` | GET | Single customer from database |
| `/api/health` | GET | Health check |

## Testing

```bash
# Test Flask mock server
curl http://localhost:5000/api/customers?page=1&limit=5

# Trigger data ingestion
curl -X POST http://localhost:8000/api/ingest

# Query ingested data
curl http://localhost:8000/api/customers?page=1&limit=5

# Get single customer
curl http://localhost:8000/api/customers/CUST001
```

## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```