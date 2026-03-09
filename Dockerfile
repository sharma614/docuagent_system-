# Build Stage for Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
# Add a wildcard just in case, but ensure we are grabbing from the frontend folder
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production Stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend and install requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose port (Render will override with its own PORT env var)
EXPOSE 8000

# Start command - use shell form so $PORT env variable is expanded at runtime
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
