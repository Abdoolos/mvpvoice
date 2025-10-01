# AI Callcenter Agent MVP - Backend Only Dockerfile
# Designer: Abdullah Alawiss

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only backend files (ignore frontend completely)
COPY backend/ ./

# Copy root level config files that backend might need
COPY runtime.txt ./
COPY requirements.txt ./

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=production

# Run the simple server
CMD ["python", "simple_server.py"]
