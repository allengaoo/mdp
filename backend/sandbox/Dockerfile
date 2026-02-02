# Use existing mdp-backend image as base (already has Python and dependencies)
FROM mdp-backend:v1

LABEL maintainer="MDP Platform"
LABEL description="MDP Sandbox - Isolated Code Execution Service"
LABEL version="1.0.0"

WORKDIR /sandbox

# Copy requirements and install additional dependencies if needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run the service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
