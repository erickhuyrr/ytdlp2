from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import uuid
import tempfile

app = FastAPI(title="Seal-Style yt-dlp API", version="1.0")


# ---------- LIST FORMATS ----------
@app.get("/formats")
def list_formats(url: str = Query(...)):
    try:
        ydl_opts = {"dump_single_json": True, "quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            formats.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f"{f.get('width')}x{f.get('height')}",
                "fps": f.get("fps"),
                "filesize": f.get("filesize"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "note": f.get("format_note"),
            })

        return {
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "duration": info.get("duration"),
            "available_formats": formats
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



# ---------- DOWNLOAD VIDEO ----------
@app.get("/download/video")
def download_video(url: str, quality: str = Query("best")):

    temp_dir = tempfile.gettempdir()
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(temp_dir, filename)

    ydl_opts = {
        "format": quality,  # best, 1080p, 720p etc
        "outtmpl": filepath,
        "quiet": True,
        "no_warnings": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return FileResponse(filepath, filename=os.path.basename(filepath))

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



# ---------- DOWNLOAD AUDIO ----------
@app.get("/download/audio")
def download_audio(url: str, audio_format: str = Query("mp3")):

    temp_dir = tempfile.gettempdir()
    filename = f"{uuid.uuid4()}.{audio_format}"
    filepath = os.path.join(temp_dir, filename)

    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": "320"
        }],
        "outtmpl": filepath,
        "quiet": True,
        "no_warnings": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return FileResponse(filepath, filename=os.path.basename(filepath))

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



# ---------- ROOT ----------
@app.get("/")
def root():
    return {"message": "Seal-Style yt-dlp API running successfully!"}
