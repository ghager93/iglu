# API Test Commands

This file contains individual curl commands for testing the Diabetes Management API endpoints.

## Prerequisites
- Make sure the server is running on `http://localhost:8000`
- The server should be started with: `cd backend && python main.py`

## Base URLs
- Base URL: `http://localhost:8000`
- API Base: `http://localhost:8000/api`

---

## 1. Root Endpoint

```bash
curl -X GET "http://localhost:8000/" \
  -H "Content-Type: application/json"
```

---

## 2. Glucose Readings Endpoints

### Get all glucose readings
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/" \
  -H "Content-Type: application/json"
```

### Get glucose readings with pagination
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/?skip=0&limit=5" \
  -H "Content-Type: application/json"
```

### Get glucose readings with time filters
```bash
# Last 24 hours
FROM_TS=$(date -d "24 hours ago" +%s)
TO_TS=$(date +%s)
curl -X GET "http://localhost:8000/api/glucose-readings/?from=$FROM_TS&to=$TO_TS" \
  -H "Content-Type: application/json"
```

### Create new glucose readings
```bash
curl -X PUT "http://localhost:8000/api/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.2,
        "timestamp": "2024-01-15T10:30:00"
      },
      {
        "value": 6.1,
        "timestamp": "2024-01-15T09:30:00"
      }
    ]
  }'
```

### Get latest glucose reading
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/latest" \
  -H "Content-Type: application/json"
```

### Export readings (JSON format)
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/export?format=json&limit=10" \
  -H "Content-Type: application/json"
```

### Export readings (CSV format)
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/export?format=csv&limit=10" \
  -H "Content-Type: application/json"
```

### Export readings (HTML format)
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/export?format=html&limit=10" \
  -H "Content-Type: application/json"
```

### Import glucose readings
```bash
curl -X POST "http://localhost:8000/api/glucose-readings/import" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 4.8,
        "timestamp": "2024-01-15T08:30:00"
      }
    ],
    "format": "json"
  }'
```

### Get specific glucose reading by ID
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/1" \
  -H "Content-Type: application/json"
```

### Delete specific glucose reading by ID
```bash
curl -X DELETE "http://localhost:8000/api/glucose-readings/1" \
  -H "Content-Type: application/json"
```

### Delete glucose readings with time filters
```bash
FROM_TS=$(date -d "24 hours ago" +%s)
TO_TS=$(date +%s)
curl -X DELETE "http://localhost:8000/api/glucose-readings/?from=$FROM_TS&to=$TO_TS" \
  -H "Content-Type: application/json"
```

### Stream glucose readings (Server-Sent Events)
```bash
curl -X GET "http://localhost:8000/api/glucose-readings/stream" \
  -H "Accept: text/event-stream" \
  -H "Cache-Control: no-cache"
```

---

## 3. Libre View Endpoints

### Get Libre View readings
```bash
curl -X GET "http://localhost:8000/api/libre-view/" \
  -H "Content-Type: application/json"
```

---

## 4. Testing with Response Details

To see HTTP status codes and timing information, add the `-w` flag:

```bash
curl -X GET "http://localhost:8000/api/glucose-readings/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

---

## 5. Common Test Scenarios

### Test the complete CRUD cycle:
1. Create readings
2. List all readings
3. Get a specific reading
4. Update (via create with same timestamp)
5. Delete a reading

### Test error conditions:
- Try to get a non-existent reading ID
- Try to create readings with invalid data
- Try to delete non-existent readings

### Test filtering:
- Use different time ranges
- Test pagination with various skip/limit values
- Test export in different formats 