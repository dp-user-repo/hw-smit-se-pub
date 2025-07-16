#!/bin/bash
set -e

# Check if we're running as root
if [ "$(id -u)" = "0" ]; then
    # Create data directory if it doesn't exist
    mkdir -p /app/data
    
    # Copy vlans.json to data directory if it doesn't exist there
    if [ ! -f "/app/data/vlans.json" ] && [ -f "/app/vlans.json" ]; then
        cp /app/vlans.json /app/data/vlans.json
    fi
    
    # Fix ownership of the entire /app directory
    chown -R appuser:appuser /app
    
    # Make sure the data directory is writable
    chmod -R 755 /app/data
    
    # Switch to appuser and execute command
    exec gosu appuser "$@"
else
    # Check if data directory exists and is writable
    if [ -d "/app/data" ] && [ ! -w "/app/data" ]; then
        # Fallback: use temporary directory
        mkdir -p /tmp/data
        export DATA_FILE_PATH="/tmp/data/vlans.json"
        if [ -f "/app/data/vlans.json" ]; then
            cp /app/data/vlans.json /tmp/data/vlans.json
        fi
    fi
    
    # Execute command
    exec "$@"
fi