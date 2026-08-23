# Deploying PestWatch to the cloud (so anyone can use it)

Once deployed you get a public **https URL** that works for anyone, anytime —
your PC can be off. That URL also makes the **PWA installable on any phone**
("Add to Home Screen"), and we can point the Android APK at it too.

Everything needed is already prepared: `Dockerfile`, `requirements-deploy.txt`,
`.dockerignore`, `backend/`, `frontend/`, `models/`.

---

## Recommended: Hugging Face Spaces (free, enough RAM for the AI)

### Option A — Git push (most reliable)
1. Create a free account at https://huggingface.co and a **write token**
   (Settings → Access Tokens → New token, role: *write*).
2. Create a Space: https://huggingface.co/new-space
   - Name: `pestwatch`  ·  SDK: **Docker**  ·  Blank template  ·  Public.
3. In a terminal on this PC:
   ```bash
   # from a folder OUTSIDE this project
   git clone https://huggingface.co/spaces/<your-username>/pestwatch
   cd pestwatch
   ```
4. Copy these into that folder (keep the structure):
   `Dockerfile`, `requirements-deploy.txt`, `.dockerignore`,
   `backend/`, `frontend/`, `models/`,
   and copy **`SPACE_README.md` → `README.md`**.
5. Push:
   ```bash
   git add .
   git commit -m "PestWatch"
   git push
   ```
   (username = your HF username, password = the write **token**.)
6. The Space builds automatically (~5–8 min). Your URL:
   **`https://<your-username>-pestwatch.hf.space`**

### Option B — Web upload (no command line)
1. Create the Docker Space as above.
2. In the Space's **Files** tab → **Add file → Upload files**, and upload:
   `Dockerfile`, `requirements-deploy.txt`, and the folders
   `backend/`, `frontend/`, `models/` (drag the folders in).
   Also add `README.md` = the contents of `SPACE_README.md`.
3. It builds automatically and gives you the URL.

---

## Alternative: Render (also free)
1. Push this project to a **GitHub** repo.
2. https://render.com → New → **Web Service** → connect the repo.
3. Environment: **Docker** (it auto-detects the `Dockerfile`). Instance: Free.
4. Deploy → you get `https://pestwatch-xxxx.onrender.com`.
   (Free Render has 512 MB RAM and sleeps when idle — the AI models are heavy,
   so first request after sleep is slow; Hugging Face is comfier for this app.)

---

## After it's live
1. Open the URL in a browser → the full app loads over HTTPS.
2. On a phone browser → **Add to Home Screen** installs it as an app (no APK needed).
3. To point the **Android APK** at the cloud instead of your PC:
   edit `capacitor.config.json` → set `server.url` to your cloud URL, then run
   `build_apk.bat`. Share the new `PestWatch.apk` — it now works anywhere.

## Notes
- Demo data (2 outbreaks, 6 farms) re-seeds automatically on start.
- Storage is ephemeral (DB/uploads reset on restart) — fine for a demo.
- The image is CPU-only (no GPU needed); detection takes a second or two per photo.
