FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY frontend.py .
COPY run.py .

# Create a non-root user (required for PyTorch on Hugging Face Spaces)
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 7860

# Container-level readiness: hit the Streamlit port the app actually exposes.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:7860/', timeout=3).status == 200 else sys.exit(1)"

# Start the orchestrator
CMD ["python", "run.py"]