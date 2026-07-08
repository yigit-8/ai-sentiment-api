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

# Start the orchestrator
CMD ["python", "run.py"]