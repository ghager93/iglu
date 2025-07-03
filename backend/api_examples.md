# API Examples

This document provides simple curl examples for all endpoints in the Diabetes Management API.

## Base URL
All examples use `http://localhost:8000` as the base URL. Adjust this for your deployment.

## Authentication
Currently, no authentication is required for any endpoints.

---

## Root Endpoint

### Get API Welcome Message
```bash
curl http://localhost:8000/
```
**Description:** Returns a welcome message confirming the API is running.

---

## Glucose Readings API

### Get All Glucose Readings
```bash
curl http://localhost:8000/api/glucose-readings/
```
**Description:** Retrieves all glucose readings from the database, ordered by timestamp.

### Get Glucose Readings with Pagination
```bash
curl "http://localhost:8000/api/glucose-readings/?skip=0&limit=10"
```
**Description:** Retrieves the first 10 glucose readings, skipping 0 records.

### Get Glucose Readings by Time Range
```bash
curl "http://localhost:8000/api/glucose-readings/?from=1640995200&to=1641081600"
```
**Description:** Retrieves glucose readings between two timestamps (epoch format). This example gets readings from January 1, 2022 to January 2, 2022.

### Get Latest Glucose Reading
```bash
curl http://localhost:8000/api/glucose-readings/latest
```
**Description:** Returns the most recent glucose reading from the database.

### Get Specific Glucose Reading by ID
```bash
curl http://localhost:8000/api/glucose-readings/123
```
**Description:** Retrieves a specific glucose reading by its database ID.

### Create New Glucose Readings
```bash
curl -X PUT http://localhost:8000/api/glucose-readings/ \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.5,
        "timestamp": "1640995200"
      },
      {
        "value": 6.2,
        "timestamp": "1640998800"
      }
    ]
  }'
```
**Description:** Creates multiple new glucose readings. The timestamp should be in epoch format (seconds since Unix epoch).

### Import Glucose Readings
```bash
curl -X POST http://localhost:8000/api/glucose-readings/import \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 7.1,
        "timestamp": "1640995200"
      }
    ],
    "format": "json"
  }'
```
**Description:** Imports glucose readings in bulk. Currently supports JSON format.

### Export Glucose Readings (JSON)
```bash
curl "http://localhost:8000/api/glucose-readings/export?format=json&limit=100"
```
**Description:** Exports glucose readings in JSON format, limited to 100 records.

### Export Glucose Readings (CSV)
```bash
curl "http://localhost:8000/api/glucose-readings/export?format=csv&limit=100"
```
**Description:** Exports glucose readings in CSV format, limited to 100 records.

### Export Glucose Readings (HTML)
```bash
curl "http://localhost:8000/api/glucose-readings/export?format=html&limit=100"
```
**Description:** Exports glucose readings in HTML table format, limited to 100 records.

### Stream Real-time Updates
```bash
curl http://localhost:8000/api/glucose-readings/stream
```
**Description:** Establishes a Server-Sent Events (SSE) connection to receive real-time glucose reading updates. This connection stays open and streams new data as it becomes available.

### Delete Specific Glucose Reading
```bash
curl -X DELETE http://localhost:8000/api/glucose-readings/123
```
**Description:** Deletes a specific glucose reading by its database ID.

### Delete Glucose Readings by Time Range
```bash
curl -X DELETE "http://localhost:8000/api/glucose-readings/?from=1640995200&to=1641081600"
```
**Description:** Deletes all glucose readings within the specified time range.

### Delete Glucose Readings by IDs
```bash
curl -X DELETE "http://localhost:8000/api/glucose-readings/?ids=123,456,789"
```
**Description:** Deletes specific glucose readings by providing a comma-separated list of IDs.

---

## LibreView API

### Fetch Readings from LibreView
```bash
curl http://localhost:8000/api/libre-view/
```
**Description:** Fetches glucose readings from the LibreView remote API and returns them as RemoteReading objects.

---

## API Documentation

### View Interactive API Documentation
```bash
curl http://localhost:8000/docs
```
**Description:** Returns the Swagger UI documentation page (best viewed in a browser).

### Get OpenAPI Schema
```bash
curl http://localhost:8000/openapi.json
```
**Description:** Returns the OpenAPI specification in JSON format.

---

## Query Parameters Reference

### Common Parameters
- `skip`: Number of records to skip (for pagination)
- `limit`: Maximum number of records to return (for pagination)
- `from`: Start timestamp in epoch format (inclusive)
- `to`: End timestamp in epoch format (inclusive)
- `format`: Export format (`json`, `csv`, `html`)
- `ids`: Comma-separated list of reading IDs

### Example with Multiple Parameters
```bash
curl "http://localhost:8000/api/glucose-readings/?from=1640995200&to=1641081600&skip=10&limit=50"
```
**Description:** Gets glucose readings from a specific time range, skipping the first 10 records and returning up to 50 records.

---

## Response Formats

### Glucose Reading Object
```json
{
  "id": 123,
  "value": 5.5,
  "timestamp": "1640995200",
  "created_at": "2022-01-01T00:00:00Z",
  "updated_at": "2022-01-01T00:00:00Z"
}
```

### Remote Reading Object
```json
{
  "value": 5.5,
  "timestamp": 1640995200
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Tips

1. **Timestamps**: All timestamps should be in epoch format (seconds since Unix epoch)
2. **Content-Type**: Always include `Content-Type: application/json` for PUT/POST requests
3. **URL Encoding**: Use quotes around URLs with query parameters to handle special characters
4. **Streaming**: The stream endpoint keeps the connection open - use Ctrl+C to stop
5. **Error Handling**: Check the HTTP status code and response body for error details 