# Use Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app/src

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir torch==2.1.0 --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the application files
COPY src/ .
COPY README.md /app/

# Create startup script
COPY startup.sh /app/
RUN chmod +x /app/startup.sh

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:5000/ || exit 1

# Run the startup script
CMD ["/app/startup.sh"]

# Install Python dependencies
RUN pip install user-agents==2.2.0 