#!/bin/bash

# API Test Script for Diabetes Management API
# Make sure the server is running on http://localhost:8000 before running these tests

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api"

echo "🧪 Testing Diabetes Management API"
echo "=================================="
echo ""

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
curl -X GET "$BASE_URL/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 2: Get all glucose readings (no filters)
echo "2. Testing GET /api/glucose-readings (all readings)..."
curl -X GET "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 3: Get glucose readings with pagination
echo "3. Testing GET /api/glucose-readings with pagination..."
curl -X GET "$API_BASE/glucose-readings/?skip=0&limit=5" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 4: Get glucose readings with time filters
echo "4. Testing GET /api/glucose-readings with time filters..."
# Using timestamps for last 24 hours
FROM_TS=$(date -d "24 hours ago" +%s)
TO_TS=$(date +%s)
curl -X GET "$API_BASE/glucose-readings/?from=$FROM_TS&to=$TO_TS" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 5: Create new glucose readings
echo "5. Testing POST /api/glucose-readings (create readings)..."
curl -X PUT "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.2,
        "timestamp": "'$(date +%Y-%m-%dT%H:%M:%S)'"
      },
      {
        "value": 6.1,
        "timestamp": "'$(date -d "1 hour ago" +%Y-%m-%dT%H:%M:%S)'"
      }
    ]
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 6: Get latest glucose reading
echo "6. Testing GET /api/glucose-readings/latest..."
curl -X GET "$API_BASE/glucose-readings/latest" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 7: Export readings in JSON format
echo "7. Testing GET /api/glucose-readings/export (JSON)..."
curl -X GET "$API_BASE/glucose-readings/export?format=json&limit=10" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 8: Export readings in CSV format
echo "8. Testing GET /api/glucose-readings/export (CSV)..."
curl -X GET "$API_BASE/glucose-readings/export?format=csv&limit=10" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 9: Import glucose readings
echo "9. Testing POST /api/glucose-readings/import..."
curl -X POST "$API_BASE/glucose-readings/import" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 4.8,
        "timestamp": "'$(date -d "2 hours ago" +%Y-%m-%dT%H:%M:%S)'"
      }
    ],
    "format": "json"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 10: Get specific glucose reading by ID (assuming ID 1 exists)
echo "10. Testing GET /api/glucose-readings/{id}..."
curl -X GET "$API_BASE/glucose-readings/1" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 11: Delete specific glucose reading by ID (assuming ID 1 exists)
echo "11. Testing DELETE /api/glucose-readings/{id}..."
curl -X DELETE "$API_BASE/glucose-readings/1" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 12: Delete glucose readings with time filters
echo "12. Testing DELETE /api/glucose-readings with time filters..."
curl -X DELETE "$API_BASE/glucose-readings/?from=$FROM_TS&to=$TO_TS" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 13: Libre View readings
echo "13. Testing GET /api/libre-view..."
curl -X GET "$API_BASE/libre-view/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

# Test 14: Stream endpoint (with timeout)
echo "14. Testing GET /api/glucose-readings/stream (with 5s timeout)..."
curl -X GET "$API_BASE/glucose-readings/stream" \
  -H "Accept: text/event-stream" \
  -H "Cache-Control: no-cache" \
  --max-time 5 \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
echo ""

echo "✅ All tests completed!"
echo ""
echo "📝 Notes:"
echo "- Some tests may fail if the database is empty or specific IDs don't exist"
echo "- The stream test has a 5-second timeout to avoid hanging"
echo "- Time filters use the last 24 hours as an example"
echo "- Make sure the server is running on http://localhost:8000" 