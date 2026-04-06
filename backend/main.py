from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from schemas import DownloadResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from download_module import download_video

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


@app.post("/download", response_model = DownloadResponse, summary = "Download a video from a URL", 
          description =
          """
            Downloads a video from a provided URL and stores it on the server.

            Optionally accepts a cookies file for accessing restricted or authenticated content
            (e.g., private or age-restricted videos).

            After download, returns the filename and a URL to retrieve the video.
            """)
async def download_endpoint(
    url: str = Form(...),
    cookies: UploadFile = File(None)
):
    try:
        output_path = DOWNLOAD_DIR

        cookie_file = None
        if cookies:
            cookie_file = cookies

        await run_in_threadpool(download_video, 
                                url, str(output_path), cookie_filename=cookie_file)

        files = sorted(output_path.glob("*.mp4"), key=os.path.getmtime, reverse=True)

        if not files:
            raise HTTPException(status_code=400, detail="Download failed")

        latest = files[0]

        return DownloadResponse (
            filename = latest.name, 
            download_url = f"/file/{latest.name}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/file/{filename}", summary="Retrieve a downloaded video file", description=
        """
        Serves a previously downloaded video file.

        ### Behavior:
        - Looks for the requested file inside the `downloads/` directory
        - Returns the file as a streamed response

        ### Notes:
        - Only files inside the download directory are accessible
        - Assumes `.mp4` media type
        """)
def get_file(filename: str):

    file_path = (DOWNLOAD_DIR / filename).resolve()

    if not str(file_path).startswith(str(DOWNLOAD_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="video/mp4", filename=filename)