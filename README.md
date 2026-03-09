## Project Structure

```
flask-fast-dlt/
├── docker-compose.yml              # Docker orchestration file
├── pyproject.toml                  # Project metadata and dependencies
├── pipeline_service/               # Main FastAPI service for data ingestion
│   ├── main.py                     # FastAPI application and endpoints
│   ├── database.py                 # Database configuration
│   ├── models/                     # SQLAlchemy data models
│   │   └── customer.py             # Customer model definition
│   ├── services/                   # Business logic layer
│   │   └── ingestion.py            # Data ingestion service using dlt
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Docker configuration for pipeline service
├── mock_server/                    # Mock data source API
│   ├── app.py                      # Flask application with mock endpoints
│   ├── data/
│   │   └── customers.json          # Sample customer data
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Docker configuration for mock server
└── README.md                       # Project documentation
```

## How It Works

This project implements a data pipeline that ingests data from a mock REST API into a PostgreSQL database using the dlt (data load tool) library. Here's the workflow:

1. **Data Source**: A Flask mock server provides customer data through REST endpoints
2. **Ingestion Service**: A FastAPI service orchestrates the data ingestion process
3. **Data Processing**: The dlt library extracts data from the mock API and loads it into PostgreSQL
4. **Database Storage**: Customer data is stored in a PostgreSQL database with proper schema

## Installation & Running

### Option 1: Using Docker (Recommended)

1. Ensure Docker and Docker Compose are installed on your system
2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd flask-fast-dlt
   ```
3. Run the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will start three services:
- PostgreSQL database on port 5432
- Mock server on port 5000
- Pipeline service on port 8000

### Option 2: Local Installation

#### Prerequisites:
- Python 3.14+
- PostgreSQL database

#### Steps:

1. Install dependencies for both services:
   ```bash
   # For pipeline service
   cd pipeline_service
   pip install -r requirements.txt
   
   # For mock server
   cd ../mock_server
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file in the pipeline_service directory with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/customer_db
   ```

3. Start PostgreSQL database (ensure it matches DATABASE_URL)

4. Run the services:
   ```bash
   # Terminal 1: Start mock server
   cd mock_server
   python app.py
   
   # Terminal 2: Start pipeline service
   cd pipeline_service
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Pipeline Service (FastAPI) - Port 8000

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |
| POST | `/api/ingest` | Trigger data ingestion from mock server to PostgreSQL |
| GET | `/api/customers` | Retrieve paginated list of customers from database |
| GET | `/api/customers/{customer_id}` | Retrieve specific customer by ID |

### Mock Server (Flask) - Port 5000

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |
| GET | `/api/customers` | Retrieve paginated list of customers from JSON file |
| GET | `/api/customers/{customer_id}` | Retrieve specific customer by ID from JSON file |

## Data Flow

1. **Mock Server** serves static customer data from `customers.json`
2. **Pipeline Service** makes HTTP requests to the mock server to fetch customer data
3. **Ingestion Process** normalizes the data and uses dlt to load it into PostgreSQL
4. **Database** stores the structured customer data
5. **API Endpoints** allow querying the ingested data

## Key Components

1. **dlt Library**: Handles the Extract, Load process with automatic schema inference
2. **SQLAlchemy Models**: Define the database schema for customer data
3. **FastAPI Framework**: Provides high-performance API endpoints with automatic documentation
4. **PostgreSQL**: Persistent storage for customer data
5. **Docker**: Containerization for consistent deployment environments
