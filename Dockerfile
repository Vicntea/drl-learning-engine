FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# PyTorch CPU
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/ia_drl_engine/scripts/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/ia_drl_engine/scripts/entrypoint.sh"]