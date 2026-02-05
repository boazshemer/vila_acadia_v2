# Vila Acadia - Full Stack Dockerfile
# Multi-stage build for optimized production image with frontend and backend

# Stage 1: Frontend Builder
FROM node:20-slim as frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY src/frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY src/frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Python Dependencies Builder
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 3: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=python-builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/backend/ ./src/backend/
COPY --chown=appuser:appuser verify.py ./

# Copy built frontend from frontend-builder
COPY --from=frontend-builder --chown=appuser:appuser /frontend/dist ./static

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

