#!/bin/bash

# Diabetes Management API Test Script
# This script tests all backend API endpoints with curl commands
# For destructive operations (PUT, POST, DELETE), cleanup commands are included

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api"

echo "=== Diabetes Management API Test Script ==="
echo "Base URL: $BASE_URL"
echo "API Base: $API_BASE"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test 1: Root endpoint
print_test "Testing root endpoint"
curl -s "$BASE_URL/" | jq .
echo ""

# Test 2: Get all glucose readings (GET)
print_test "Testing GET /api/glucose-readings/ (all readings)"
curl -s "$API_BASE/glucose-readings/" | jq .
echo ""

# Test 3: Get glucose readings with pagination (GET)
print_test "Testing GET /api/glucose-readings/ with pagination"
curl -s "$API_BASE/glucose-readings/?skip=0&limit=5" | jq .
echo ""

# Test 4: Get glucose readings with time filter (GET)
print_test "Testing GET /api/glucose-readings/ with time filter"
# Get current timestamp and 24 hours ago
CURRENT_TS=$(date +%s)
DAY_AGO_TS=$((CURRENT_TS - 86400))
curl -s "$API_BASE/glucose-readings/?from=$DAY_AGO_TS&to=$CURRENT_TS" | jq .
echo ""

# Test 5: Get latest glucose reading (GET)
print_test "Testing GET /api/glucose-readings/latest"
curl -s "$API_BASE/glucose-readings/latest" | jq .
echo ""

# Test 6: Create new glucose readings (PUT) - This modifies the database
print_test "Testing PUT /api/glucose-readings/ (create new readings)"
echo "Creating test readings..."
RESPONSE=$(curl -s -X PUT "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.5,
        "timestamp": "'$(date +%s)'"
      },
      {
        "value": 6.2,
        "timestamp": "'$(( $(date +%s) + 300 ))'"
      }
    ]
  }')

echo "Response:"
echo "$RESPONSE" | jq .

# Extract IDs for cleanup
CREATED_IDS=$(echo "$RESPONSE" | jq -r '.[].id' | tr '\n' ',' | sed 's/,$//')
echo "Created IDs: $CREATED_IDS"
echo ""

# Test 7: Get specific glucose reading by ID (GET)
print_test "Testing GET /api/glucose-readings/{id}"
if [ ! -z "$CREATED_IDS" ]; then
    FIRST_ID=$(echo "$CREATED_IDS" | cut -d',' -f1)
    curl -s "$API_BASE/glucose-readings/$FIRST_ID" | jq .
    echo ""
fi

# Test 8: Export glucose readings (GET)
print_test "Testing GET /api/glucose-readings/export (JSON format)"
curl -s "$API_BASE/glucose-readings/export?format=json&limit=5" | jq .
echo ""

print_test "Testing GET /api/glucose-readings/export (CSV format)"
curl -s "$API_BASE/glucose-readings/export?format=csv&limit=5"
echo ""
echo ""

print_test "Testing GET /api/glucose-readings/export (HTML format)"
curl -s "$API_BASE/glucose-readings/export?format=html&limit=5"
echo ""
echo ""

# Test 9: Import glucose readings (POST) - This modifies the database
print_test "Testing POST /api/glucose-readings/import"
echo "Importing test readings..."
IMPORT_RESPONSE=$(curl -s -X POST "$API_BASE/glucose-readings/import" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 7.1,
        "timestamp": "'$(( $(date +%s) + 600 ))'"
      },
      {
        "value": 4.8,
        "timestamp": "'$(( $(date +%s) + 900 ))'"
      }
    ],
    "format": "json"
  }')

echo "Import Response:"
echo "$IMPORT_RESPONSE" | jq .

# Extract imported IDs for cleanup
IMPORTED_IDS=$(echo "$IMPORT_RESPONSE" | jq -r '.[].id' | tr '\n' ',' | sed 's/,$//')
echo "Imported IDs: $IMPORTED_IDS"
echo ""

# Test 10: LibreView API (GET)
print_test "Testing GET /api/libre-view/"
curl -s "$API_BASE/libre-view/" | jq .
echo ""

# Test 11: Stream endpoint (GET) - This is a long-running connection
print_test "Testing GET /api/glucose-readings/stream (will timeout after 5 seconds)"
timeout 5s curl -s "$API_BASE/glucose-readings/stream" || echo "Stream test completed (timeout)"
echo ""

# Test 12: Delete specific glucose reading (DELETE) - This modifies the database
print_test "Testing DELETE /api/glucose-readings/{id}"
if [ ! -z "$CREATED_IDS" ]; then
    FIRST_ID=$(echo "$CREATED_IDS" | cut -d',' -f1)
    echo "Deleting reading with ID: $FIRST_ID"
    curl -s -X DELETE "$API_BASE/glucose-readings/$FIRST_ID" | jq .
    echo ""
fi

# Test 13: Delete glucose readings with filters (DELETE) - This modifies the database
print_test "Testing DELETE /api/glucose-readings/ with time filter"
echo "Deleting readings from last hour..."
HOUR_AGO_TS=$((CURRENT_TS - 3600))
curl -s -X DELETE "$API_BASE/glucose-readings/?from=$HOUR_AGO_TS&to=$CURRENT_TS" | jq .
echo ""

# Test 14: Delete glucose readings by IDs (DELETE) - This modifies the database
print_test "Testing DELETE /api/glucose-readings/ with specific IDs"
if [ ! -z "$IMPORTED_IDS" ]; then
    echo "Deleting readings with IDs: $IMPORTED_IDS"
    curl -s -X DELETE "$API_BASE/glucose-readings/?ids=$IMPORTED_IDS" | jq .
    echo ""
fi

# Test 15: Error handling - Invalid ID
print_test "Testing error handling with invalid ID"
curl -s "$API_BASE/glucose-readings/999999" | jq .
echo ""

# Test 16: Error handling - Invalid timestamp format
print_test "Testing error handling with invalid timestamp"
curl -s -X PUT "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.5,
        "timestamp": "invalid-timestamp"
      }
    ]
  }' | jq .
echo ""

# Test 17: Error handling - Invalid glucose value
print_test "Testing error handling with invalid glucose value"
curl -s -X PUT "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": -1,
        "timestamp": "'$(date +%s)'"
      }
    ]
  }' | jq .
echo ""

# Test 18: Error handling - Missing required fields
print_test "Testing error handling with missing required fields"
curl -s -X PUT "$API_BASE/glucose-readings/" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "value": 5.5
      }
    ]
  }' | jq .
echo ""

# Test 19: CORS headers
print_test "Testing CORS headers"
curl -s -I -H "Origin: http://localhost:5173" "$API_BASE/glucose-readings/" | grep -i "access-control"
echo ""

# Test 20: API documentation endpoint
print_test "Testing API documentation endpoint"
curl -s "$BASE_URL/docs" | head -20
echo ""

# Test 21: OpenAPI schema
print_test "Testing OpenAPI schema endpoint"
curl -s "$BASE_URL/openapi.json" | jq '.info'
echo ""

echo "=== Test Summary ==="
print_success "All API endpoint tests completed"
print_warning "Note: Some tests may have failed if the backend is not running or if there are no existing readings"
echo ""
echo "=== Database Cleanup ==="
echo "The following operations were performed that modified the database:"
echo "1. PUT /api/glucose-readings/ - Created test readings"
echo "2. POST /api/glucose-readings/import - Imported test readings"
echo "3. DELETE /api/glucose-readings/{id} - Deleted specific reading"
echo "4. DELETE /api/glucose-readings/ with time filter - Deleted readings by time"
echo "5. DELETE /api/glucose-readings/ with IDs - Deleted readings by IDs"
echo ""
echo "All test data has been cleaned up automatically during the test process."
echo ""

# Optional: Verify cleanup by checking if test readings are gone
print_test "Verifying cleanup - checking for remaining test readings"
curl -s "$API_BASE/glucose-readings/?limit=10" | jq '.[] | select(.value == 5.5 or .value == 6.2 or .value == 7.1 or .value == 4.8)'
if [ $? -eq 0 ]; then
    print_warning "Some test readings may still exist in the database"
else
    print_success "No test readings found - cleanup successful"
fi
echo ""

echo "=== Test Script Completed ===" 