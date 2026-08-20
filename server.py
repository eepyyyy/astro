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

class HoroscopeRequest(BaseModel):
    datetime_str: Optional[str] = None  # ISO format "YYYY-MM-DDTHH:MM:SS"
    latitude: float = 12.98117
    longitude: float = 77.48509
    altitude: float = 820.0
    is_local: bool = True
    time_offset: float = 5.5
    method: str = "vedic"
    ayanamsa_mode: str = "Lahiri"


def calculate_mandi(jd: float, lat: float, lon: float, dt_local: datetime) -> HouseDetails:
    weekday = dt_local.weekday()
    day_ghatis = [22, 18, 14, 10, 6, 2, 26]
    ghati = day_ghatis[weekday]
    hours_from_sunrise = (ghati / 60.0) * 24.0

    mandi_jd = jd + (hours_from_sunrise / 24.0) - 0.25
    cusps, ascmc = swe.houses(mandi_jd, lat, lon, b'p')
    aya = swe.get_ayanamsa_ut(mandi_jd)
    mandi_deg = (ascmc[0] - aya) % 360.0
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
    weekday = dt_local.weekday()
    start_chaldean_idx = WEEKDAY_TO_CHALDEAN_START[weekday]

    t = dt_local.hour + dt_local.minute / 60.0 + dt_local.second / 3600.0
    hours_from_6am = (t - 6.0) % 24.0
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
            dt = datetime.fromisoformat(clean_str)
        else:
            dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
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

    mandi = calculate_mandi(horoscope.julian_day, req.latitude, req.longitude, horoscope.datetime_local)
    hora_info = calculate_hora(horoscope.datetime_local)

    res_data = horoscope.model_dump(mode="json")
    res_data["main_chart"]["mandi"] = mandi.model_dump(mode="json")
    res_data["hora_info"] = hora_info
    
    t = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    is_day = (6.0 <= t < 18.0)
    t_jamam = (t - 6.0) % 24.0 if is_day else (t - 18.0) % 24.0
    jamam_num = int(t_jamam // 1.5) + 1
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = day_names[dt.weekday()]
    res_data["jamam_info"] = {
        "day_name": day_name,
        "is_day": is_day,
        "jamam_number": jamam_num,
        "display_title": f"HORA CHART, {day_name} Jamam # {jamam_num}"
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
        datetime_str=dt_local.strftime("%Y-%m-%dT%H:%M:%S"),
        latitude=lat,
        longitude=lon,
        altitude=alt,
        is_local=True,
        time_offset=time_offset
    )
    data = compute_horoscope_response(req)
    return JSONResponse(content=data)


# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Hora Chart API Backend Running. Please create static/index.html"}


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
