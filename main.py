from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI(title="Seal-Style Direct URL yt-dlp API")


# -------------------- LIST ALL FORMATS (DIRECT URL) --------------------
@app.get("/formats")
def list_formats(url: str = Query(...)):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True}

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
                "format_note": f.get("format_note"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "direct_url": f.get("url")  # <-- DIRECT DOWNLOAD URL
            })

        return {
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "duration": info.get("duration"),
            "formats": formats
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



# -------------------- GET BEST VIDEO DIRECT URL --------------------
@app.get("/video")
def get_video(url: str, quality: str = Query("best")):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        selected = None
        for f in info["formats"]:
            if quality == "best" or quality in (f.get("format_id"), f.get("format_note", "")):
                selected = f

        if not selected:
            selected = info["formats"][-1]

        return {
            "title": info["title"],
            "quality": selected.get("format_note"),
            "ext": selected.get("ext"),
            "direct_url": selected.get("url")
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



# -------------------- GET BEST AUDIO DIRECT URL --------------------
@app.get("/audio")
def get_audio(url: str):
    try:
        ydl_opts = {"quiet": True, "no_warnings": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        audio_formats = [f for f in info["formats"] if f.get("vcodec") == "none"]

        best = audio_formats[-1] if audio_formats else None

        return {
            "title": info["title"],
            "audio_quality": best.get("abr"),
            "ext": best.get("ext"),
            "direct_url": best.get("url")
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)})



@app.get("/")
def root():
    return {"message": "Direct URL yt-dlp API running!"}
