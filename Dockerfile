# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies (including curl for health checks and gosu for user switching)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Copy application code and required files
COPY app/ ./app/
COPY openapi.yml ./
COPY entrypoint.sh ./
COPY vlans.json ./

# Create directory for data storage (entrypoint will copy vlans.json here)
RUN mkdir -p /app/data

# Make entrypoint script executable and set proper ownership
RUN chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

# Note: We start as root to fix permissions, then switch to appuser
# USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint to fix permissions and run the application
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]