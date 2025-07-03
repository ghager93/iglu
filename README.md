# Diabetes Management Application

A comprehensive diabetes management system with a FastAPI backend and React frontend for tracking and visualizing glucose readings.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Installation](#backend-installation)
  - [Frontend Installation](#frontend-installation)
  - [Full Stack Installation](#full-stack-installation)
- [Deployment](#deployment)
  - [Backend Deployment](#backend-deployment)
  - [Frontend Deployment](#frontend-deployment)
  - [Full Stack Deployment](#full-stack-deployment)
- [API Documentation](#api-documentation)
- [How to Use the Application](#how-to-use-the-application)
- [Development](#development)
- [Contributing](#contributing)

## Overview

[TO BE FILLED: Brief description of what the application does and its main purpose]

## Features

- Real-time glucose reading tracking
- Data visualization with charts and graphs
- RESTful API for data management
- Server-Sent Events (SSE) for real-time updates
- Integration with LibreView API
- Export functionality (JSON, CSV, HTML)
- Responsive web interface

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Git** (for cloning the repository)

## Installation

### Backend Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd iglu2
   ```

2. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database** (if using Alembic migrations):
   ```bash
   alembic upgrade head
   ```

6. **Run the backend server**:
   ```bash
   python main.py
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

### Full Stack Installation

1. **Install backend dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

3. **Start both services**:

   **Terminal 1 (Backend)**:
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

   **Terminal 2 (Frontend)**:
   ```bash
   cd frontend
   npm run dev
   ```

## Deployment

### Backend Deployment

1. **Production dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   - Set up environment variables as needed
   - Configure database connection
   - Set up SSL certificates if required

3. **Run with production server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   Or using Gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Frontend Deployment

1. **Build the production version**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve the built files**:
   ```bash
   npm run preview
   ```

   Or deploy to a static hosting service (Netlify, Vercel, etc.)

### Full Stack Deployment

1. **Deploy backend first** following the backend deployment steps
2. **Update frontend API configuration** to point to your deployed backend
3. **Build and deploy frontend** following the frontend deployment steps

## API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `[YOUR_DEPLOYED_BACKEND_URL]`

### Authentication
Currently, the API does not require authentication.

### Endpoints

#### Glucose Readings API (`/api/glucose-readings`)

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/api/glucose-readings/` | Get glucose readings | `from`, `to`, `skip`, `limit` |
| `PUT` | `/api/glucose-readings/` | Create new glucose readings | `readings` (array) |
| `DELETE` | `/api/glucose-readings/` | Delete glucose readings | `ids`, `from`, `to`, `skip`, `limit` |
| `GET` | `/api/glucose-readings/export` | Export readings | `from`, `to`, `format`, `skip`, `limit` |
| `GET` | `/api/glucose-readings/latest` | Get latest reading | None |
| `POST` | `/api/glucose-readings/import` | Import readings | `readings` (array), `format` |
| `GET` | `/api/glucose-readings/stream` | Stream real-time updates | None |
| `GET` | `/api/glucose-readings/{id}` | Get specific reading | `reading_id` |
| `DELETE` | `/api/glucose-readings/{id}` | Delete specific reading | `reading_id` |

#### LibreView API (`/api/libre-view`)

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/api/libre-view/` | Fetch readings from LibreView | None |

### Query Parameters

- `from`: Epoch start timestamp (inclusive)
- `to`: Epoch end timestamp (inclusive)
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return (pagination)
- `format`: Export format (`json`, `csv`, `html`)
- `ids`: Array of reading IDs to delete

### Response Formats

#### Glucose Reading Object
```json
{
  "id": 1,
  "value": 120,
  "timestamp": 1640995200,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Remote Reading Object
```json
{
  "value": 120,
  "timestamp": 1640995200
}
```

### Real-time Updates

The `/api/glucose-readings/stream` endpoint provides Server-Sent Events (SSE) for real-time glucose reading updates.

## How to Use the Application

[TO BE FILLED: Step-by-step guide on how to use the application, including screenshots and examples]

### Getting Started

[TO BE FILLED: Initial setup and first-time user experience]

### Main Features

[TO BE FILLED: Detailed explanation of each major feature]

### Troubleshooting

[TO BE FILLED: Common issues and their solutions]

## Development

### Project Structure

```
iglu2/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   │   ├── controllers/   # Business logic
│   │   │   ├── db/           # Database configuration
│   │   │   ├── models/       # Database models
│   │   │   ├── repositories/ # Data access layer
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   └── services/     # External service integrations
│   │   ├── tests/            # Test files
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── requirements.txt  # Python dependencies
│   │   └── alembic.ini       # Database migration configuration
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── assets/       # Static assets
│   │   │   ├── App.tsx       # Main React component
│   │   │   └── main.tsx      # React entry point
│   │   ├── package.json      # Node.js dependencies
│   │   └── vite.config.ts    # Vite configuration
│   └── README.md
```

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

### Code Quality

**Backend**:
- Uses `ruff` for linting
- Follows PEP 8 style guidelines

**Frontend**:
- Uses ESLint for linting
- TypeScript for type safety

## Contributing

[TO BE FILLED: Guidelines for contributing to the project]

## License

[TO BE FILLED: License information]

## Support

[TO BE FILLED: How to get help and support] 