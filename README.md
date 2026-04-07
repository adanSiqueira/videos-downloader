<div align="center">

# web-video-downloader

**A full-stack web application to download videos from virtually any platform on the internet.**

<br/>

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-Typed-blue?logo=typescript)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styling-38B2AC?logo=tailwind-css)
![Vite](https://img.shields.io/badge/Vite-Build-purple?logo=vite)
![yt--dlp](https://img.shields.io/badge/yt--dlp-Downloader-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

<br/>

🌐 **Live Frontend:** [stream-video-downloader.vercel.app](https://stream-video-downloader.vercel.app/)  
🔌 **Live API:** [stream-video-downloader.onrender.com](https://stream-video-downloader.onrender.com/)  
📦 **Repository:** [github.com/adanSiqueira/videos-downloader](https://github.com/adanSiqueira/videos-downloader)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Current State](#current-state)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Backend](#backend)
  - [Tech Stack](#backend-tech-stack)
  - [Core Modules](#core-modules)
  - [API Endpoints](#api-endpoints)
  - [yt-dlp Configuration](#yt-dlp-configuration)
  - [Cookie Handling](#cookie-handling)
  - [Async Strategy](#async-strategy)
  - [Dockerfile & Containerization](#dockerfile--containerization)
- [Frontend](#frontend)
  - [Tech Stack](#frontend-tech-stack)
  - [Application Flow](#application-flow)
  - [Cookie Upload UX](#cookie-upload-ux)
- [Deployment Strategy](#deployment-strategy)
  - [Backend on Render](#backend-on-render)
  - [Frontend on Vercel](#frontend-on-vercel)
  - [Environment Variables](#environment-variables)
- [YouTube Download Limitations](#youtube-download-limitations)
- [Security Considerations](#security-considerations)
- [Workflow (End-to-End)](#workflow-end-to-end)
- [Roadmap](#roadmap)

---

## Overview

**web-video-downloader** is a full-stack web application that allows users to download videos from virtually any website on the internet. It exposes a clean, modern interface where the user pastes a URL and receives a downloadable MP4 file in seconds.

The application is composed of two independently deployed services:

- A **React + TypeScript frontend**, deployed on [Vercel](https://stream-video-downloader.vercel.app/), responsible for the user interface.
- A **FastAPI backend**, deployed on [Render](https://stream-video-downloader.onrender.com/) inside a Docker container, responsible for video downloading, processing, and serving the file.

Video downloading is powered by **yt-dlp**, a battle-tested and actively maintained open-source library that supports thousands of websites. For sites that require authentication (notably YouTube), the application supports optional **cookie-based authentication** via file upload.

---

## Current State

| Feature | Status |
|---|---|
| Download videos from most websites | ✅ Working |
| MP4 output with H.264/AVC + M4A audio | ✅ Working |
| Cookie upload (`.txt` and `.json` formats) | ✅ Working |
| JSON → Netscape cookie conversion | ✅ Working |
| Frontend deployed on Vercel | ✅ Live |
| Backend deployed on Render (Docker) | ✅ Live |
| YouTube downloads | ⚠️ In Progress |
| Progress bar | 🔜 Planned |
| Video quality selector | 🔜 Planned |
| Audio-only download | 🔜 Planned |

> **YouTube Note:** YouTube downloads are currently unreliable due to YouTube's aggressive bot detection, which blocks requests originating from cloud server IPs. This is a known limitation of yt-dlp in server-side contexts. Active research is underway using yt-dlp's documentation, GitHub issues, and FAQs to resolve this — potential approaches include cookie passthrough, PO token handling, and JavaScript runtime injection.

---

## Architecture

```
┌─────────────────────────────────┐
│  User (Browser)                 │
│  stream-video-downloader        │
│  .vercel.app                    │
└────────────┬────────────────────┘
             │ POST /download (multipart form)
             │ GET  /file/{filename}
             ▼
┌─────────────────────────────────┐
│  FastAPI Backend                │
│  (Render · Docker Container)    │
│                                 │
│  main.py ──► download_module.py │
│                  │              │
│                  ▼              │
│              yt-dlp             │
│                  │              │
│                  ▼              │
│         /downloads/*.mp4        │
└─────────────────────────────────┘
```

The two services are decoupled and independently deployed. The frontend communicates with the backend exclusively over HTTP using a `VITE_API_URL` environment variable, which points to the Render API. This separation allows both layers to be scaled, updated, and redeployed independently.

---

## Project Structure

```
.
├── README.md
│
├── backend/
│   ├── main.py                  # FastAPI app, endpoints, CORS
│   ├── download_module.py       # yt-dlp logic, cookie handling
│   ├── schemas.py               # Pydantic response models
│   ├── requirements.txt         # Python dependencies
│   ├── packages.txt             # System packages (ffmpeg)
│   ├── Dockerfile               # Container definition
│   └── downloads/               # Runtime: downloaded MP4 files
│
└── frontend/
    ├── src/
    │   ├── App.tsx              # Main UI component
    │   ├── main.tsx             # React entry point
    │   └── services/
    │       └── api.ts           # API communication layer
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    ├── .env.example             # Environment variable template
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── tsconfig.json
```

Both `backend/` and `frontend/` are treated as independent root directories for their respective deployments — Render points to `backend/` and Vercel points to `frontend/`.

---

## Backend

### Backend Tech Stack

| Technology | Role |
|---|---|
| **Python 3.12** | Runtime |
| **FastAPI** | Web framework and API layer |
| **yt-dlp** | Video downloading engine |
| **Pydantic** | Request/response schema validation |
| **FFmpeg** | Video/audio stream merging |
| **Uvicorn** | ASGI server |
| **Docker** | Containerization for deployment |

---

### Core Modules

#### `main.py` — FastAPI Application

This is the entry point of the backend. It defines the FastAPI application instance, applies CORS middleware, configures the downloads directory, and registers the two API endpoints.

CORS is currently configured with `allow_origins=["*"]` for development convenience. In a production hardened environment, this should be restricted to the Vercel frontend domain.

The `downloads/` directory is created at startup using `Path.mkdir(exist_ok=True)`, ensuring the folder always exists when the container is running.

#### `download_module.py` — Download Engine

This module contains all the logic for actually downloading a video. It is kept separate from `main.py` to enforce a clean separation between:

- **Async I/O** (handled in FastAPI endpoints using `run_in_threadpool`)
- **Blocking I/O** (handled here synchronously, as yt-dlp is not async-native)

The module contains two functions:

**`convert_json_cookies_to_netscape(json_bytes)`**

yt-dlp requires cookies in the Netscape text format. However, browser cookie export extensions often produce JSON files. This function handles the conversion. It supports several JSON cookie structures:

- A raw list of cookie dicts: `[{...}, {...}]`
- A dict with a `"cookies"` key: `{"cookies": [{...}]}`
- Nested JSON (some extensions double-encode): parsed with a second `json.loads`
- Chrome/Edge-style exports with various keys

The function writes the Netscape header and then converts each cookie's `domain`, `path`, `secure`, `expirationDate`/`expires`/`expiry`, `name`, and `value` fields. Domains without a leading dot are prefixed with one (per Netscape format convention).

**`download_video(url, output_path, cookie_content, cookie_filename)`**

This is the main download function. It:

1. Receives `cookie_content` as raw bytes (already read by the async FastAPI endpoint — this avoids mixing sync/async file I/O).
2. Writes the cookie bytes to a temp file (`tempfile.gettempdir()`), converting from JSON to Netscape format if the filename ends in `.json`.
3. Configures yt-dlp options:
   - **Format string:** `bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4` — selects the best available H.264/AVC video stream and M4A audio stream, merging them into MP4 via FFmpeg.
   - **`merge_output_format`:** explicitly forces the output container to MP4.
   - **`js_runtimes`:** configures yt-dlp to use a Node.js runtime for JavaScript-based extraction challenges (relevant for YouTube).
   - **`cookiefile`:** path to the temp cookie file, if provided.
4. Calls `yt_dlp.YoutubeDL(ydl_opts).download([url])` to perform the download.

#### `schemas.py` — Response Models

Defines the Pydantic model used for the `/download` response:

```python
class DownloadResponse(BaseModel):
    filename: str
    download_url: str
```

This ensures FastAPI automatically validates and serializes the response JSON.

---

### API Endpoints

#### `POST /download`

Downloads a video from a provided URL and returns a link to the file.

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | `string` | ✅ | The video URL to download |
| `cookies` | `file` | ❌ | Cookie file (`.txt` Netscape or `.json` browser export) |

**Response** (`200 OK`):

```json
{
  "filename": "My Video Title.mp4",
  "download_url": "/file/My%20Video%20Title.mp4"
}
```

**Error responses:**

| Code | Scenario |
|---|---|
| `400` | Download completed but no `.mp4` file was found |
| `500` | yt-dlp raised an exception (e.g., unsupported site, bot detection) |

**Implementation notes:**

- `download_video` is a blocking function (yt-dlp is synchronous). It is offloaded to a thread pool using `await run_in_threadpool(...)` so it does not block the event loop.
- After download, the endpoint scans the `downloads/` directory, sorts files by modification time descending, and returns the most recently created file. This is a simple strategy that works for single-user or low-concurrency scenarios.
- Cookie file bytes are read inside the async endpoint (before the threadpool call) to avoid doing async I/O inside synchronous code.

#### `GET /file/{filename}`

Serves a previously downloaded video file.

**Response:** Streamed `video/mp4` using FastAPI's `FileResponse`.

**Security:** The resolved file path is checked against the `downloads/` directory to prevent path traversal attacks. A `403 Forbidden` is returned if the resolved path escapes the download directory.

---

### yt-dlp Configuration

The format selector used is:

```
bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4
```

Breaking this down:

- `bestvideo[ext=mp4][vcodec^=avc]` — selects the highest quality video-only stream that is already an MP4 container and uses an AVC (H.264) codec. This avoids VP9/AV1 streams that would require re-encoding.
- `+bestaudio[ext=m4a]` — merges with the best M4A audio stream.
- `/mp4` — fallback: if the above selection fails, use the best available MP4 stream.
- `merge_output_format: mp4` — instructs FFmpeg to merge the streams into an MP4 container.

This format string was chosen for maximum compatibility: H.264 video in MP4 is playable on virtually every device and browser without transcoding.

---

### Cookie Handling

Cookies are used to authenticate requests to platforms that require a logged-in session. The flow is:

1. The user exports cookies from their browser using a dedicated extension.
2. The file (`.txt` in Netscape format, or `.json` in the extension's format) is uploaded through the frontend.
3. The FastAPI endpoint reads the file bytes and passes them to `download_video`.
4. If the file is `.json`, `convert_json_cookies_to_netscape` is called to convert it to yt-dlp's required format.
5. The cookie file is written to the system's temp directory (`tempfile.gettempdir()`), which is always writable even in containerized/cloud environments.
6. yt-dlp is configured with `cookiefile` pointing to this temp file.

**Why temp dir?** The `downloads/` folder is the only persistent folder, but writing cookies there would risk leaking sensitive data via the `/file/` endpoint. Using the system temp directory isolates cookies from the public-facing file serving layer.

---

### Async Strategy

FastAPI is built on asyncio and uses an async event loop. yt-dlp, however, is a blocking synchronous library — calling it directly inside an `async def` endpoint would block the entire server.

The solution is `run_in_threadpool`, provided by Starlette (FastAPI's underlying framework). This runs the blocking `download_video` function in a separate OS thread, returning control to the event loop while the download executes. The `await` in:

```python
await run_in_threadpool(download_video, url, str(output_path), ...)
```

ensures the endpoint is non-blocking from FastAPI's perspective, even though `download_video` itself is fully synchronous.

---

### Dockerfile & Containerization

The backend is containerized using Docker for consistent, reproducible deployments.

```dockerfile
FROM python:3.12-slim
```

`python:3.12-slim` is used as the base image — it provides a full Python runtime with minimal footprint, avoiding unnecessary packages present in the full `python:3.12` image.

**Key build steps:**

1. **FFmpeg installation** — installed via `apt-get` as a system dependency. FFmpeg is required by yt-dlp to merge separate video and audio streams into a single MP4 file.
2. **Virtual environment** — a venv is created at `/opt/venv` and activated via `ENV PATH`. This isolates Python packages from the system Python.
3. **Dependency caching** — `requirements.txt` and `packages.txt` are copied and installed before the application code. This leverages Docker's layer cache: if dependencies haven't changed, Docker reuses the cached layer and skips reinstallation on subsequent builds.
4. **Downloads directory** — `RUN mkdir -p downloads` ensures the directory exists inside the image.
5. **Dynamic port binding** — the `CMD` uses `$PORT` instead of a hardcoded port. Render (and most PaaS providers) inject a `PORT` environment variable at runtime, and the application binds to it.

```dockerfile
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
```

---

## Frontend

### Frontend Tech Stack

| Technology | Role |
|---|---|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **TailwindCSS** | Utility-first styling |
| **Vite** | Build tool and dev server |

---

### Application Flow

The frontend is a single-page application composed of one main component (`App.tsx`) and one service module (`services/api.ts`).

**`services/api.ts`**

This module abstracts the HTTP communication with the backend. It reads the base API URL from the `VITE_API_URL` environment variable (injected at build time by Vite) and exports a single `downloadVideo` function:

```typescript
export const downloadVideo = async (formData: FormData) => {
  const response = await fetch(`${API_URL}/download`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Download failed");
  return response.json();
};
```

Using `FormData` allows both the text URL field and the optional binary cookie file to be sent in a single `multipart/form-data` request, matching the FastAPI endpoint's expected input.

**`App.tsx`**

State is managed with `useState` hooks:

| State | Purpose |
|---|---|
| `url` | The video URL entered by the user |
| `cookiesFile` | The optional uploaded cookie `File` object |
| `loading` | Controls the button disabled state and label |
| `error` | Displays error messages below the button |
| `downloadLink` | The full URL to the downloaded file |

On submit, `handleDownload`:

1. Validates that a URL was entered.
2. Builds a `FormData` object with the URL and (if present) the cookie file.
3. Calls `downloadVideo(formData)` from the service layer.
4. On success, constructs the full file URL by prepending the Render API base URL to `data.download_url`.
5. Stores the link in state and opens it in a new tab (`window.open`).

The UI uses a **glassmorphism** design aesthetic — translucent cards with `backdrop-blur`, white-tinted backgrounds, and a deep red gradient background.

---

### Cookie Upload UX

A collapsible `<details>` accordion section below the main card explains to users why cookies might be needed and provides step-by-step instructions for exporting them from the four major browsers:

- **Microsoft Edge** — using the J2TEAM Cookies extension
- **Google Chrome** — using the "Get cookies.txt LOCALLY" extension
- **Mozilla Firefox** — using the cookies.txt Firefox Add-on
- **Safari** — noted as having limited support, with a recommendation to use another browser

Each browser's instructions are nested inside their own `<details>` element, keeping the UI clean until expanded.

---

## Deployment Strategy

The monorepo contains both `backend/` and `frontend/` as separate subdirectories. Each is deployed independently, with its subdirectory set as the root directory in its respective platform.

### Backend on Render

Render is a PaaS (Platform as a Service) that supports Docker deployments. The backend is deployed as a **Docker Web Service**:

- **Root directory:** `backend/`
- **Build:** Render builds the Docker image using `backend/Dockerfile`
- **Runtime:** The container runs `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Persistent storage:** The `downloads/` directory lives inside the container. Note that Render's free tier does not provide persistent disks — the downloads folder is ephemeral and will be lost on redeploy or restart. For production, a persistent volume or external object storage (e.g., S3) should be used.

### Frontend on Vercel

Vercel is a frontend deployment platform with native Vite/React support.

- **Root directory:** `frontend/`
- **Framework preset:** Vite
- **Build command:** `vite build`
- **Output directory:** `dist/`
- **Environment variable:** `VITE_API_URL` is set in the Vercel project settings, pointing to the Render backend URL.

Vercel automatically handles CDN distribution, HTTPS, and preview deployments on pull requests.

### Environment Variables

**Frontend (`frontend/.env`):**

```env
VITE_API_URL=https://stream-video-downloader.onrender.com
```

This variable is injected at Vite build time. The `.env.example` file is committed to the repository as a template; the actual `.env` is gitignored.

**Backend:** No environment variables are required beyond `PORT`, which is injected automatically by Render at runtime.

---

## YouTube Download Limitations

YouTube is actively working to prevent programmatic downloads from server-side applications. The main barriers are:

1. **Server IP blocking** — YouTube identifies and blocks requests from known cloud provider IP ranges (AWS, GCP, Render, etc.), returning `HTTP 403` or triggering bot challenges.

2. **Bot detection (PO Tokens)** — YouTube issues "Proof of Origin" tokens that are generated client-side using JavaScript. Requests without a valid PO token are rejected or degraded.

3. **Cookie validation** — Even with a valid cookie file, YouTube cross-checks the request's IP against the session's origin IP. A cookie from a Brazilian home network used from a US-based Render server will likely be flagged.

**Current research directions:**

- Providing valid browser cookies via the cookie upload feature
- Exploring yt-dlp's `js_runtimes` (Node.js) for JavaScript-based challenge solving
- Reviewing yt-dlp's GitHub issues, FAQ, and the `--extractor-args youtube` options for PO token handling
- Investigating `--force-ipv4` and proxy configuration options

Downloads from other platforms (Instagram, Twitter/X, Reddit, TikTok, Vimeo, Dailymotion, and thousands more supported by yt-dlp) work reliably.

---

## Security Considerations

| Concern | Mitigation |
|---|---|
| Path traversal in file serving | Resolved path is checked to start with `downloads/` absolute path |
| Cookie data leakage | Cookies written to system temp dir, not the public `downloads/` folder |
| Arbitrary file access | `GET /file/{filename}` only serves files inside `downloads/` |
| CORS | Currently `allow_origins=["*"]`; should be restricted to the Vercel domain in production |
| Cookie privacy | Cookies are written to a temp file and used only for the current download — they are not persisted or logged |

---

## Workflow (End-to-End)

```
1. User opens https://stream-video-downloader.vercel.app/
2. Pastes a video URL into the input field
3. (Optional) uploads a browser cookie file
4. Clicks "Download Video"

5. Frontend builds a FormData with url + cookies
6. POST /download sent to Render backend

7. FastAPI receives the request
8. Cookie bytes are read from the UploadFile (async)
9. download_video() is dispatched to a threadpool

10. Cookie file written to /tmp/temp_cookies.txt
    (JSON converted to Netscape format if needed)
11. yt-dlp downloads the video stream(s)
12. FFmpeg merges video + audio into MP4
13. File saved to backend/downloads/

14. Backend scans downloads/, returns latest .mp4 filename
15. Response: { filename, download_url }

16. Frontend receives response
17. Full download URL constructed
18. window.open() triggers browser download
19. Fallback link displayed in UI
```

---

## Roadmap

- [ ] **Resolve YouTube downloads** — PO token + cookie passthrough strategy
- [ ] **Download progress bar** — stream yt-dlp progress events to frontend (WebSocket or SSE)
- [ ] **Video quality selector** — expose available formats before downloading
- [ ] **Audio-only download** — MP3/M4A output option
- [ ] **Persistent file storage** — replace ephemeral container storage with S3 or Render Disks
- [ ] **Download queue** — background task queue (Celery + Redis) for concurrent downloads
- [ ] **Rate limiting** — prevent abuse on the public API
- [ ] **Restrict CORS** — limit `allow_origins` to the Vercel frontend domain
- [ ] **Authentication** — optional user accounts for download history
- [ ] **Auto-cleanup** — periodic deletion of old files from the downloads directory