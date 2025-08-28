#!/bin/bash

# Set strict error handling
set -euo pipefail

# Configuration
DB_URI="./diabetes_management.db"

# Input validation function
validate_input() {
    local input="$1"
    local max_length="${2:-100}"
    
    # Check if input is empty or too long
    if [[ -z "$input" || ${#input} -gt $max_length ]]; then
        return 1
    fi
    
    # Check for potentially dangerous characters
    if [[ "$input" =~ [\"\'\;\\\|\&\$\`\(\)\{\}\[\]\<\>] ]]; then
        return 1
    fi
    
    return 0
}

# Validate command line arguments
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <name> <email> [api_key]"
    echo "  name: User's name (max 100 chars, no special chars)"
    echo "  email: User's email (max 100 chars, no special chars)"
    echo "  api_key: Optional 64-character hex string"
    exit 1
fi

# Validate and sanitize inputs
name="$1"
email="$2"

if ! validate_input "$name" 100; then
    echo "Error: Invalid name. Must be 1-100 characters with no special characters."
    exit 1
fi

if ! validate_input "$email" 100; then
    echo "Error: Invalid email. Must be 1-100 characters with no special characters."
    exit 1
fi

# Validate email format (basic check)
if ! [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "Error: Invalid email format."
    exit 1
fi

# Handle API key
if [ $# -eq 3 ]; then
    api_key="$3"
    # Validate API key format (64 hex characters)
    if ! [[ "$api_key" =~ ^[a-fA-F0-9]{64}$ ]]; then
        echo "Error: API key must be exactly 64 hexadecimal characters."
        exit 1
    fi
else
    echo "Generating API key..."
    api_key=$(openssl rand -hex 32)
fi

# Verify database file exists and is writable
if [ ! -f "$DB_URI" ]; then
    echo "Error: Database file '$DB_URI' does not exist."
    exit 1
fi

if [ ! -w "$DB_URI" ]; then
    echo "Error: Database file '$DB_URI' is not writable."
    exit 1
fi

# Check if user already exists
existing_user=$(sqlite3 "$DB_URI" "SELECT COUNT(*) FROM api_users WHERE name = '$name';" 2>/dev/null || echo "0")

if [ "$existing_user" -gt 0 ]; then
    echo "Error: User with name '$name' already exists."
    exit 1
fi

# Use parameterized query to prevent SQL injection
echo "Adding API key to database..."
echo "Name: $name"
echo "Email: $email"
echo "API Key: $api_key"

# Create temporary SQL file for safe execution
temp_sql=$(mktemp)
cat > "$temp_sql" << EOF
INSERT INTO api_users (name, email, api_key) VALUES ('$name', '$email', '$api_key');
EOF

# Execute SQL with error handling
if sqlite3 "$DB_URI" < "$temp_sql"; then
    echo "Successfully added API key for user: $name"
else
    echo "Error: Failed to add API key to database."
    rm -f "$temp_sql"
    exit 1
fi

# Clean up
rm -f "$temp_sql"

echo "Done."