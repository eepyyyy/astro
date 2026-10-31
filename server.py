import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from main import calculate_complete_jamakkol_horoscope
from calc import local_to_jd
import swisseph as swe
from Schema import HouseDetails

app = FastAPI(title="Hora Chart & Jamakkol Prasanam API", version="2.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time

LAST_ACTIVITY_TIME = time.time()

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    global LAST_ACTIVITY_TIME
    LAST_ACTIVITY_TIME = time.time()
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

class HoroscopeRequest(BaseModel):
    datetime_str: Optional[str] = None  # ISO format "YYYY-MM-DDTHH:MM:SS"
    latitude: float = 12.98117
    longitude: float = 77.48509
    altitude: float = 820.0
    is_local: bool = True
    time_offset: float = 5.5
    method: str = "vedic"
    ayanamsa_mode: str = "Lahiri"


def calculate_mandi(jd: float, lat: float, lon: float, dt_local: datetime, sun_deg: float) -> HouseDetails:
    t = dt_local.hour + dt_local.minute / 60.0 + (dt_local.second + dt_local.microsecond / 1000000.0) / 3600.0
    if t < 6.0:
        astro_weekday = (dt_local.weekday() - 1) % 7
    else:
        astro_weekday = dt_local.weekday()
    
    # Weekday in 0=Sun ... 6=Sat
    jkw = (astro_weekday + 1) % 7
    is_day = (6.0 <= t < 18.0)
    
    # Method 5 (used by Jamakkol Prasanam): Saturn Kala / Ghati relative to Sun (1 Ghati = 6°)
    # Day Ghatis: Sun 26 (156°), Mon 22 (132°), Tue 18 (108°), Wed 14 (84°), Thu 10 (60°), Fri 6 (36°), Sat 2 (12°)
    MANDI_DAY_OFFSETS = [156.0, 132.0, 108.0, 84.0, 60.0, 36.0, 12.0]
    # Night Ghatis from Sunset (Sun+180°): Sun 10 (240°), Mon 6 (216°), Tue 2 (192°), Wed 26 (336°), Thu 22 (312°), Fri 18 (288°), Sat 14 (264°)
    MANDI_NIGHT_OFFSETS = [240.0, 216.0, 192.0, 336.0, 312.0, 288.0, 264.0]
    
    offset = MANDI_DAY_OFFSETS[jkw] if is_day else MANDI_NIGHT_OFFSETS[jkw]
    mandi_deg = (sun_deg + offset) % 360.0
    return HouseDetails(deg=mandi_deg)


def calculate_hora(dt_local: datetime) -> dict:
    CHALDEAN_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    WEEKDAY_TO_CHALDEAN_START = {
        6: 0,  # Sunday -> Sun
        0: 3,  # Monday -> Moon
        1: 6,  # Tuesday -> Mars
        2: 2,  # Wednesday -> Mercury
        3: 5,  # Thursday -> Jupiter
        4: 1,  # Friday -> Venus
        5: 4   # Saturday -> Saturn
    }
    t = dt_local.hour + dt_local.minute / 60.0 + (dt_local.second + dt_local.microsecond / 1000000.0) / 3600.0
    if t < 6.0:
        astro_weekday = (dt_local.weekday() - 1) % 7
        hours_from_6am = t + 18.0
    else:
        astro_weekday = dt_local.weekday()
        hours_from_6am = t - 6.0

    start_chaldean_idx = WEEKDAY_TO_CHALDEAN_START[astro_weekday]
    hora_index = int(hours_from_6am)

    current_chaldean_idx = (start_chaldean_idx + hora_index) % 7
    hora_lord = CHALDEAN_ORDER[current_chaldean_idx]

    h_start = int((6 + hora_index) % 24)
    h_end = int((h_start + 1) % 24)
    hora_str = f"Hora: {hora_lord} ({h_start:02d}:00 - {h_end:02d}:00)"
    return {
        "hora_lord": hora_lord,
        "hora_index": hora_index + 1,
        "hora_display": hora_str
    }


def compute_horoscope_response(req: HoroscopeRequest) -> dict:
    if req.datetime_str:
        clean_str = req.datetime_str.replace("Z", "")
        if "T" in clean_str:
            try:
                dt = datetime.fromisoformat(clean_str)
            except Exception:
                dt = datetime.strptime(clean_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        else:
            try:
                dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    dt = datetime.fromisoformat(clean_str)
    else:
        utc_now = datetime.now(timezone.utc)
        dt = utc_now + timedelta(hours=req.time_offset)
        dt = dt.replace(tzinfo=None)

    horoscope = calculate_complete_jamakkol_horoscope(
        dt=dt,
        lat=req.latitude,
        lon=req.longitude,
        alt=req.altitude,
        is_local=req.is_local,
        time_offset=req.time_offset,
        method=req.method.lower()
    )

    sun_deg = horoscope.main_chart.planets.sun.housedetails.deg
    mandi = calculate_mandi(horoscope.julian_day, req.latitude, req.longitude, horoscope.datetime_local, sun_deg)
    hora_info = calculate_hora(horoscope.datetime_local)

    res_data = horoscope.model_dump(mode="json")
    res_data["datetime_local"] = horoscope.datetime_local.isoformat(timespec="milliseconds")
    res_data["main_chart"]["mandi"] = mandi.model_dump(mode="json")
    res_data["hora_info"] = hora_info
    
    t = dt.hour + dt.minute / 60.0 + (dt.second + dt.microsecond / 1000000.0) / 3600.0
    is_day = (6.0 <= t < 18.0)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if t < 6.0:
        astro_weekday = (dt.weekday() - 1) % 7
        t_jamam = t + 6.0  # elapsed hours into night (from 18:00 of previous day)
    elif is_day:
        astro_weekday = dt.weekday()
        t_jamam = t - 6.0  # elapsed hours into day (from 06:00)
    else:
        astro_weekday = dt.weekday()
        t_jamam = t - 18.0 # elapsed hours into night (from 18:00)

    jamam_num = int(t_jamam // 1.5) + 1
    day_name = day_names[astro_weekday]
    res_data["jamam_info"] = {
        "day_name": day_name,
        "is_day": is_day,
        "jamam_number": jamam_num,
        "display_title": f"JAMAKKOL HORARY, {day_name} Jamam # {jamam_num}"
    }
    return res_data


# POST /api/horoscope and POST /horoscope
@app.post("/api/horoscope")
@app.post("/horoscope")
def post_horoscope(req: HoroscopeRequest):
    try:
        data = compute_horoscope_response(req)
        return JSONResponse(content=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# GET /api/horoscope and GET /horoscope
@app.get("/api/horoscope")
@app.get("/horoscope")
def get_horoscope_query(
    datetime_str: Optional[str] = None,
    lat: float = 12.98117,
    lon: float = 77.48509,
    alt: float = 820.0,
    time_offset: float = 5.5,
    method: str = "vedic"
):
    try:
        req = HoroscopeRequest(
            datetime_str=datetime_str,
            latitude=lat,
            longitude=lon,
            altitude=alt,
            is_local=True,
            time_offset=time_offset,
            method=method
        )
        data = compute_horoscope_response(req)
        return JSONResponse(content=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/now")
def get_now(lat: float = 12.98117, lon: float = 77.48509, alt: float = 820.0, time_offset: float = 5.5):
    utc_now = datetime.now(timezone.utc)
    dt_local = (utc_now + timedelta(hours=time_offset)).replace(tzinfo=None)
    req = HoroscopeRequest(
        datetime_str=dt_local.isoformat(timespec="milliseconds"),
        latitude=lat,
        longitude=lon,
        altitude=alt,
        is_local=True,
        time_offset=time_offset
    )
    data = compute_horoscope_response(req)
    return JSONResponse(content=data)


# Ensure static directory exists (supports PyInstaller _MEIPASS bundle path)
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Default Local Markdown Vault Directory (Obsidian-style local .md files)
WORK_ROOT = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
DEFAULT_VAULT_DIR = os.environ.get("JAMAKKOL_VAULT_DIR", os.path.join(WORK_ROOT, "HoraryVault"))
os.makedirs(DEFAULT_VAULT_DIR, exist_ok=True)


class VaultSaveRequest(BaseModel):
    filename: str
    markdown_content: str
    png_filename: Optional[str] = None
    png_data_url: Optional[str] = None
    vault_dir: Optional[str] = None


@app.get("/api/vault/info")
def get_vault_info(vault_dir: Optional[str] = None):
    target_dir = vault_dir or DEFAULT_VAULT_DIR
    os.makedirs(target_dir, exist_ok=True)
    return {"vault_dir": target_dir, "vault_name": os.path.basename(target_dir.rstrip("\\/"))}


@app.get("/api/vault/notes")
def list_vault_notes(vault_dir: Optional[str] = None):
    target_dir = vault_dir or DEFAULT_VAULT_DIR
    os.makedirs(target_dir, exist_ok=True)
    notes = []
    for fname in os.listdir(target_dir):
        if fname.lower().endswith(".md"):
            fpath = os.path.join(target_dir, fname)
            try:
                stat = os.stat(fpath)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                notes.append({
                    "filename": fname,
                    "title": fname[:-3],
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "preview": content[:320]
                })
            except Exception:
                pass
    notes.sort(key=lambda x: x["mtime"], reverse=True)
    return {"vault_dir": target_dir, "notes": notes}


@app.post("/api/vault/save")
def save_vault_note(req: VaultSaveRequest):
    import base64
    target_dir = req.vault_dir or DEFAULT_VAULT_DIR
    os.makedirs(target_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in req.filename).strip()
    if not safe_name.lower().endswith(".md"):
        safe_name += ".md"
    fpath = os.path.join(target_dir, safe_name)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(req.markdown_content)

    png_saved_path = None
    if req.png_data_url and req.png_data_url.startswith("data:image/png;base64,"):
        raw_png_name = req.png_filename or (safe_name[:-3] + ".png")
        safe_png = "".join(c if c.isalnum() or c in "._- " else "_" for c in raw_png_name).strip()
        if not safe_png.lower().endswith(".png"):
            safe_png += ".png"
        png_saved_path = os.path.join(target_dir, safe_png)
        b64_part = req.png_data_url.split(",", 1)[1]
        with open(png_saved_path, "wb") as pf:
            pf.write(base64.b64decode(b64_part))

    return {"ok": True, "filename": safe_name, "path": fpath, "png_path": png_saved_path}


@app.get("/api/vault/read")
def read_vault_note(filename: str, vault_dir: Optional[str] = None):
    target_dir = vault_dir or DEFAULT_VAULT_DIR
    safe_name = os.path.basename(filename)
    fpath = os.path.join(target_dir, safe_name)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Vault note not found")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    return {"filename": safe_name, "path": fpath, "markdown_content": content}


@app.delete("/api/vault/delete")
def delete_vault_note(filename: str, vault_dir: Optional[str] = None):
    target_dir = vault_dir or DEFAULT_VAULT_DIR
    safe_name = os.path.basename(filename)
    fpath = os.path.join(target_dir, safe_name)
    if os.path.exists(fpath):
        os.remove(fpath)
    return {"ok": True, "deleted": safe_name}


# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Hora Chart API Backend Running. Please create static/index.html"}

@app.get("/favicon.ico")
def read_favicon():
    fav_file = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav_file):
        return FileResponse(fav_file)
    raise HTTPException(status_code=404)


if __name__ == '__main__':
    import uvicorn
    # Default port is 8080 (or passed via command line, or PORT environment variable)
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8080))
    print(f"Starting server on http://0.0.0.0:{port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
