FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
    
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Now copy the actual application code
# .dockerignore prevents unwanted files
# ─────────────────────────────────────────────
COPY . .

RUN mkdir -p logs

ENV PYTHONPATH=/app

EXPOSE 8501

# ─────────────────────────────────────────────
# Health check — EC2 load balancer uses this
# to verify the container is running correctly
# ─────────────────────────────────────────────

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ─────────────────────────────────────────────
# Run the app
# --server.address=0.0.0.0 → accept connections
#   from outside the container (required for EC2)
# --server.port=8501        → explicit port
# --server.headless=true    → no browser auto-open
# ─────────────────────────────────────────────

CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]