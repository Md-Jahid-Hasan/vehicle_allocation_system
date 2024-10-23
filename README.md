# FastAPI Vehicle Allocation System

This is a **FastAPI** application for a vehicle allocation system where employees can allocate vehicles for a day, given that the vehicle is not already allocated. The system includes CRUD operations and a report generation feature, with appropriate filters.

## Features

- Vehicle allocation for employees
- CRUD operations on vehicles, drivers, and allocations
- Allocation history report with filtering capabilities
- FastAPI documentation auto-generated at `/docs`

## Prerequisites

- **Python 3.11** (or higher)
- **MongoDB** (for data storage)

---

## Quickstart

### 1. Run with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t vehicle-allocation-app .
    ```
2. **Run the Docker container**:
    ```bash
    docker run -d --name vehicle-allocation-app -p 8000:8000 vehicle-allocation-app
    ```
3. The application will be available at http://localhost:8000.

### Run with virtual environment
1. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source ven/bin/activate # Linux activate
    ```
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the application**:
    ```bash
    uvicorn app.main:app --reload
   fastapi dev main.py # anyone you prefer
    ```
   
4. The application will be available at http://localhost:8000.

### API Documentation
FastAPI automatically provides interactive API documentation, available at the following locations once the application is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

