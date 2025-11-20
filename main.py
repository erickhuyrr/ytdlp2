from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import uuid
import os
import subprocess

app = FastAPI(title="Seal-Style yt-dlp API")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def run_aria2(url, output):
    cmd = [
        "aria2c",
        "--allow-overwrite=true",
        "--auto-file-renaming=false",
        "-o", output,
        url
    ]

    process = subprocess.run(cmd, capture_output=True, text=True)
    return process.stdout + process.stderr


def run_ytdlp(url, output, audio_only=False, ext="mp4"):
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, output + ".%(ext)s"),
        "noplaylist": True,
    }

    if audio_only:
        ydl_opts.update({
            "format": "bestaudio/best",
            "extract_audio": True,
            "audio_format": ext,
        })
    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        filename = ydl.prepare_filename(info)
        return filename


@app.get("/")
def root():
    return {"status": "Seal-like yt-dlp API working"}


@app.get("/download")
def download(
    url: str = Query(...),
    audio_only: bool = Query(False),
    ext: str = Query("mp4"),
    use_aria2: bool = Query(False)
):

    file_id = str(uuid.uuid4())
    output_name = f"{file_id}"

    try:
        if use_aria2:
            log = run_aria2(url, output_name + "." + ext)
            filepath = os.path.join(DOWNLOAD_DIR, output_name + "." + ext)

        else:
            filepath = run_ytdlp(url, output_name, audio_only, ext)

        if not os.path.exists(filepath):
            return JSONResponse({"error": "Download failed"}, status_code=500)

        return FileResponse(
            filepath,
            filename=os.path.basename(filepath),
            media_type="application/octet-stream",
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/info")
def video_info(url: str = Query(...)):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
