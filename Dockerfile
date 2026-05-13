# Dockerfile optimized for running on Render (CPU-only, reduced layers)
# Base on Debian slim, install minimal system deps then pip install

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# create app directory
WORKDIR /app

# Install system deps needed for some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for layer caching
COPY requirements.txt /app/requirements.txt

# Install CPU-only torch wheel and pip deps
# Pin a CPU-only torch wheel that exists on the PyTorch CPU index.
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Ensure models directory exists (Render will mount/read repository)
RUN mkdir -p /app/ia_drl_engine/models

# Copy entrypoint script and make executable
COPY ia_drl_engine/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use a non-root user (optional)
RUN adduser --disabled-password --gecos '' appuser || true
RUN chown -R appuser:appuser /app
USER appuser

# Expose standard port that Render uses
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
