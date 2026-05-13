#!/usr/bin/env bash
set -euo pipefail

# ENTRYPOINT: downloads model from MODEL_URL if MODEL_PATH missing, then starts uvicorn
MODEL_PATH=${MODEL_PATH:-/app/ia_drl_engine/models/ppo_music_learning.zip}
MODEL_URL=${MODEL_URL:-}

if [ ! -f "$MODEL_PATH" ]; then
  if [ -n "$MODEL_URL" ]; then
    echo "Model not found at $MODEL_PATH. Downloading from MODEL_URL..."
    mkdir -p "$(dirname "$MODEL_PATH")"
    curl -fsSL "$MODEL_URL" -o "$MODEL_PATH"
    echo "Downloaded model to $MODEL_PATH"
  else
    echo "Warning: model not found at $MODEL_PATH and MODEL_URL not provided. App will attempt to start and fail on first inference if needed."
  fi
else
  echo "Model already present at $MODEL_PATH"
fi

# Start uvicorn
exec uvicorn ia_drl_engine.main:app --host 0.0.0.0 --port 8000 --workers 1
