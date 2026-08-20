from datetime import datetime, timedelta
from typing import Optional, Tuple
import swisseph as swe

from jamma_planets import jamma_planets
from kavipu import kavipu
from calc import dt_jd, local_to_jd
from udhayam import udhayam
from arudam import arudam
from rich import print
from planets import get_planets
from Schema import (
    PlanetaryCollections,
    MainChartDetails,
    DivisionalChartsGroup,
    CompleteJamakkolHoroscopeOutput,
    build_divisional_charts_group,
    ComprehensiveHoroscope,
    ComprehensivePlanetDetails,
    HouseDetails,
    UdhayamOutput, Input
)
from fastapi import FastAPI

app = FastAPI()

@app.post("/horascope/")
def get_gorascope(input: Input) -> CompleteJamakkolHoroscopeOutput:
    hora = calculate_complete_jamakkol_horoscope(
        dt=input.dt,
        lat=input.lat,
        lon=input.lon,
        alt=input.alt,
        is_local= input.is_local,
        time_offset= input.time_offset,
        method= input.method
    )
    return hora

def calculate_complete_jamakkol_horoscope(
    dt: datetime,
    lat: float,
    lon: float,
    alt: float = 0.0,
    is_local: bool = True,
    time_offset: float = 5.5,
    method: str = "Vedic"
) -> CompleteJamakkolHoroscopeOutput:
    """
    Main unified API pipeline matching the architectural specification:
    
    1. Input: (datetime, lat, lon, alt, mode)
    2. Main Chart:
       - ascendant (Sidereal & Tropical)
       - udhayam (Udhayam Lagna, Sunrise/Sunset)
       - arudham (Arudham Lagna)
       - kavippu (Kavippu point)
       - planets (Ephemeris 9 planets + Ayanamsa)
       - jamma_planets (8 Jamakkol Outer wheel planets)
    3. Divisional Charts (D-1 to D-300):
       - Projected from Main Chart
       - Every divisional chart (d1, d2, d3, d4, d5, d6, d7, d8, d9, d10,
         d11, d12, d16, d20, d24, d27, d30, d40, d45, d60, d72, d81,
         d108, d144, d150, d300) contains all 10 celestial bodies with
         0-11 house indices, rasi names, DMS strings, and KP sub-lords!
    """
    if is_local:
        jd = local_to_jd(dt, tz_offset_hours=time_offset)
        dt_local = dt
        dt_utc = dt - timedelta(hours=time_offset)
    else:
        dt_utc = dt
        dt_local = dt + timedelta(hours=time_offset)
        jd = dt_jd(dt_utc)

    # 1. Main Chart Calculations
    u = udhayam(jd_query=jd, lat=lat, lon=lon, alt=alt, method=method)
    ardm = arudam(dt_local=dt_local)
    planets = get_planets(jd=jd, lat=lat, lon=lon)
    k = kavipu(
        udhyam_rasi=u.housedetails.house,
        arudham_deg_in_rasi=ardm.deg,
        arudham_rasi=ardm.house,
        sun_rasi=planets.sun.housedetails.house,
    )
    jammaplanets = jamma_planets(jd=jd, tz_offset=time_offset)

    asc_sidereal = planets.acendant_sidereal
    asc_deg = asc_sidereal.housedetails.deg if asc_sidereal else 0.0

    main_chart = MainChartDetails(
        ascendant_sidereal=asc_sidereal,
        ascendant_tropical=planets.acendant_tropical,
        udhayam=u,
        arudham=ardm,
        kavippu=k,
        planets=planets,
        jamma_planets=jammaplanets
    )

    # 2. Divisional Charts Calculations (D-1 to D-300)
    divisional_charts = build_divisional_charts_group(
        planets=planets,
        ascendant_deg=asc_deg
    )

    # 3. Assemble Complete Unified Output
    ayanamsa_val = swe.get_ayanamsa_ut(jd)
    return CompleteJamakkolHoroscopeOutput(
        datetime_utc=dt_utc,
        datetime_local=dt_local,
        latitude=lat,
        longitude=lon,
        altitude=alt,
        julian_day=jd,
        ayanamsa=ayanamsa_val,
        main_chart=main_chart,
        divisional_charts=divisional_charts
    )

