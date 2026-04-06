import yt_dlp
import os
import json
from pathlib import Path
import tempfile


def convert_json_cookies_to_netscape(json_bytes):
    """
    Convert a YouTube/Chrome/Edge JSON cookie export into Netscape cookie format.

    This function accepts multiple cookie formats exported by browser extensions,
    including:
        - A raw list of cookie dictionaries
        - A dict containing {"cookies": [...]}
        - A JSON string inside a JSON blob (common in some extensions)
        - Chrome/Edge extension export formats

    It produces a Netscape-compatible cookie file (required by yt-dlp),
    converting relevant fields such as domain, path, secure flag, expiration
    timestamp, name, and value.

    Args:
        json_bytes (bytes):
            RAW bytes read from a cookie file (uploaded in Streamlit).
            Must represent a JSON array or dict containing cookie structures.

    Returns:
        bytes:
            A UTF-8 encoded string representing the cookie data in Netscape format.

    Raises:
        ValueError:
            If the JSON structure cannot be parsed into a known cookie format.

    Notes:
        - The Netscape format is required for yt-dlp's `--cookies` / `cookiefile`.
        - Unknown fields are ignored; missing fields are safely defaulted.
    """
    raw = json_bytes.decode("utf-8")

    try:
        data = json.loads(raw)
    except Exception:
        data = json.loads(json.loads(raw))

    if isinstance(data, dict) and "cookies" in data:
        cookies = data["cookies"]
    elif isinstance(data, list):
        cookies = data
    else:
        for v in data.values():
            if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                cookies = v
                break
        else:
            raise ValueError("JSON cookie file format not recognized.")

    lines = ["# Netscape HTTP Cookie File", ""]

    for c in cookies:
        domain = c.get("domain", "")
        if domain and not domain.startswith("."):
            domain = "." + domain

        line = (
            f"{domain}\t"
            f"{'TRUE' if domain.startswith('.') else 'FALSE'}\t"
            f"{c.get('path', '/')}\t"
            f"{'TRUE' if c.get('secure') else 'FALSE'}\t"
            f"{int(c.get('expirationDate') or c.get('expires') or c.get('expiry') or 0)}\t"
            f"{c.get('name','')}\t"
            f"{c.get('value','')}"
        )
        lines.append(line)

    return "\n".join(lines).encode("utf-8")


def download_video(url, output_path, cookie_content=None, cookie_filename=None):
    """
    Download a YouTube video using yt-dlp with optional authenticated cookies.

    This function:
        1. Receives cookie data as raw bytes (already read in the FastAPI async layer).
        2. Converts JSON cookie exports to Netscape format when necessary.
        3. Writes the cookies to a temporary file in the system temp directory.
        4. Configures yt-dlp to use the cookie file if provided.
        5. Downloads the video using a format that prioritizes
           AVC/H.264 video and M4A audio, merging the output into MP4.

    This design separates concerns between:
        - Async I/O (handled in the FastAPI endpoint)
        - Blocking operations (handled here in a threadpool)

    It ensures compatibility across environments where only temporary
    directories are writable (e.g., cloud platforms).

    Args:
        url (str):
            A valid YouTube video URL.

        output_path (str):
            Path to the directory where the final video file will be saved.

        cookie_content (bytes, optional):
            Raw bytes of the uploaded cookie file. This is read in the async
            FastAPI endpoint and passed to this function to avoid mixing async
            and sync file handling.

        cookie_filename (str, optional):
            Original filename of the uploaded cookie file. Used to determine
            how to process the cookie content (e.g., `.txt` vs `.json`).

    Returns:
        None:
            The video is downloaded directly to `output_path`.

    Raises:
        yt_dlp.utils.DownloadError:
            If the video cannot be downloaded (e.g., blocked, invalid URL,
            missing formats, or authentication failure).

        ValueError:
            If the provided cookie file format is not supported.

    Notes:
        - Cookies are written to a temporary file using `tempfile.gettempdir()`.
        - JSON cookies are converted to Netscape format before use.
        - Only one download is performed per function call.
        - Requires `ffmpeg` to be installed for proper merging of video/audio.
        - Uses Node.js (via yt-dlp `js_runtimes`) for handling YouTube's
          JavaScript-based extraction challenges.
    """

    # Writable temp folder for Streamlit Cloud
    tmp_dir = tempfile.gettempdir()
    cookie_path = None

    # ---- HANDLE COOKIES FIRST ----
    if cookie_content is not None:
        cookie_path = os.path.join(tmp_dir, "temp_cookies.txt")

        if cookie_filename.endswith(".txt"):
            with open(cookie_path, "wb") as f:
                f.write(cookie_content)

        elif cookie_filename.endswith(".json"):
            netscape = convert_json_cookies_to_netscape(cookie_content)
            with open(cookie_path, "wb") as f:
                f.write(netscape)

   # ---- YT-DLP OPTIONS ----
    ydl_opts = {
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "format": "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/mp4",
        "merge_output_format": "mp4",
        "js_runtimes": {
            "node": {}
        }
    }

    if cookie_path:
        ydl_opts["cookiefile"] = cookie_path

    # ---- DOWNLOAD ----
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])