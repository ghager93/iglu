# API Testing

This folder contains test files for the Diabetes Management API.

## Files

- `api_tests.sh` - Complete test script that runs all API endpoints
- `curl_commands.md` - Individual curl commands for each endpoint
- `test_data.json` - Sample glucose reading data for testing
- `README.md` - This file

## Quick Start

1. **Start the server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Run all tests:**
   ```bash
   cd backend/test
   ./api_tests.sh
   ```

3. **Test individual endpoints:**
   - Copy commands from `curl_commands.md`
   - Or use the test data file:
   ```bash
   curl -X PUT "http://localhost:8000/api/glucose-readings/" \
     -H "Content-Type: application/json" \
     -d @test_data.json
   ```

## API Endpoints Tested

### Glucose Readings (`/api/glucose-readings/`)
- `GET /` - List all readings (with optional filters)
- `PUT /` - Create new readings
- `DELETE /` - Delete readings (by ID or time range)
- `GET /export` - Export readings (JSON/CSV/HTML)
- `GET /latest` - Get latest reading
- `POST /import` - Import readings
- `GET /{id}` - Get specific reading
- `DELETE /{id}` - Delete specific reading
- `GET /stream` - Server-Sent Events stream

### Libre View (`/api/libre-view/`)
- `GET /` - Fetch remote readings

### Root
- `GET /` - API welcome message

## Notes

- Some tests may fail if the database is empty
- The stream test has a timeout to prevent hanging
- Time filters use the last 24 hours as examples
- All timestamps are in ISO format for the API
- The server runs on `http://localhost:8000` by default 