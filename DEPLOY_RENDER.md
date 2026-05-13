Render deployment instructions

1) Create a new Web Service on Render
   - Connect your GitHub/GitLab repo containing this project
   - Branch: choose the branch you want to deploy (e.g., `dev`)

2) Build and start commands
   - Build Command: leave blank (Dockerfile present)
   - Start Command: the Dockerfile CMD runs uvicorn. No change needed.

3) Environment
   - Add any required environment variables in Render dashboard (e.g., MODEL_PATH if you change it).
   - If your model file (ia_drl_engine/models/ppo_music_learning.zip) is large, consider hosting it on object storage (S3/Spaces) and download at startup.

4) Model larger than repo
   - If the model artifact doesn't fit in repo or you prefer to keep image small, add a small startup hook to download the model into `/app/ia_drl_engine/models/` from a secure URL (signed S3 URL) and set MODEL_PATH env var.

5) Health check
   - Configure a health check path: `/` or `/health` (root returns a basic message)

6) Tips to keep memory/CPU low
   - Use 1 Uvicorn worker (already in Dockerfile). More workers duplicate memory usage.
   - Use CPU-only PyTorch (recommended for free tiers).
   - Load model lazily on first request (the code already uses lazy singletons).
   - Use torch.inference_mode() or torch.no_grad() during prediction (code updated).
   - If model is large, serve a smaller distilled policy or quantized weights.

7) Logs and debugging
   - Enable streaming logs on Render. Check startup logs for model loading.

8) Free tier considerations
   - Free tiers may sleep the service; on wake model must be reloaded. Keep model loading fast (small models), or persist model in a mounted volume / object store.

9) Environment variables to add (suggested)
   - MODEL_PATH: path to model file inside container (default: `ia_drl_engine/models/ppo_music_learning.zip`)

10) Security
   - Don't commit large private models to the repo. Use private object storage and a download step.


If you want, I can also:
 - Add a startup script that downloads MODEL_URL at boot if MODEL_PATH missing
 - Add a simple `/health` endpoint that checks model loaded
 - Create a small script to convert or quantize the policy to reduce size

