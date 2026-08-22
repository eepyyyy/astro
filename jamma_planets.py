import sys
from datetime import datetime
import swisseph as swe
from calc import local_to_jd, jd_to_local
from rich import print
from Schema import HouseDetails, JamaPlanetDetails, JamaPlanetaryCollections

# 12 Rasis: English and Sanskrit/Tamil Names matching user formatting:
# Aries/Mesha, Taurus/Vrishabha, Gemini/Mithuna, Cancer/Karkataka, Leo/Simha, Virgo/Kanya, Libra/Thula, Scorpio/Vrischika, Sagittarius/Dhanus, Capricorn/Makara, Aquarius/Kumbha, Pisces/Meena
RASI_NAMES_MAP = [
    ("Aries", "Mesha"),
    ("Taurus", "Vrishabha"),
    ("Gemini", "Mithuna"),
    ("Cancer", "Karkataka"),
    ("Leo", "Simha"),
    ("Virgo", "Kanya"),
    ("Libra", "Thula"),
    ("Scorpio", "Vrischika"),
    ("Sagittarius", "Dhanus"),
    ("Capricorn", "Makara"),
    ("Aquarius", "Kumbha"),
    ("Pisces", "Meena")
]

def jamma_planets(jd: float, tz_offset: float = 5.5):
    # Convert Julian Day to local datetime
    dt_local = jd_to_local(jd, tz_offset)
    
    # 8 Outer wheel planets order
    JAMA_OUTER_PLANETS = ["Sun", "Mars", "Jupiter", "Mercury", "Venus", "Saturn", "Moon", "Snake"]
    
    # Decimal hours local time (retaining full microsecond accuracy)
    t = dt_local.hour + dt_local.minute / 60.0 + (dt_local.second + dt_local.microsecond / 1000000.0) / 3600.0
    
    # In Vedic Jamakkol, the astrological day starts at 06:00 AM.
    # Before 06:00 AM, the weekday belongs to the previous day.
    if t < 6.0:
        astro_weekday = (dt_local.weekday() - 1) % 7
        hours_since_6am = t + 18.0  # (t + 24.0 - 6.0)
    else:
        astro_weekday = dt_local.weekday()
        hours_since_6am = t - 6.0

    # Weekday mapping (0=Sunday ... 6=Saturday)
    jkw = (astro_weekday + 1) % 7
    
    # Weekday lord starting position mapping
    WEEKDAY_L_MAP = {0: 0, 1: 6, 2: 1, 3: 3, 4: 2, 5: 4, 6: 5}
    idx_L = WEEKDAY_L_MAP[jkw]
    
    rotation = hours_since_6am * 30.0
    
    jamma_positions = {}
    for idx_P, p_name in enumerate(JAMA_OUTER_PLANETS):
        # Calculate starting degree at 06:00 AM
        start_deg = (0.0 - (idx_P - idx_L) * 45.0) % 360.0
        
        # Longitude at query time
        lon = (start_deg - rotation) % 360.0
        
        # Rasi index and names
        rasi_idx = int(lon // 30)
        rasi_eng, rasi_san = RASI_NAMES_MAP[rasi_idx]
        
        # Format starting degree DMS
        s_deg = int(start_deg)
        s_mnt = int((start_deg - s_deg) * 60)
        s_sec = int(round(((start_deg - s_deg) * 60 - s_mnt) * 60))
        if s_sec == 60:
            s_sec = 0
            s_mnt += 1
        if s_mnt == 60:
            s_mnt = 0
            s_deg = (s_deg + 1) % 360
        start_dms_str = f"{s_deg:03d}° {s_mnt:02d}' {s_sec:02d}\""

        # Instantiate JamaPlanetDetails using the HouseDetails schema (which automatically calculates KP subdivisions)
        jamma_positions[p_name.lower()] = JamaPlanetDetails(
            planet_name=p_name,
            housedetails=HouseDetails(deg=lon),
            is_retrograde=True,
            rasi_name_en=rasi_eng,
            rasi_name_sanskrit=rasi_san,
            start_deg=start_deg,
            start_deg_dms=start_dms_str
        )
        
    return JamaPlanetaryCollections(**jamma_positions)

if __name__ == '__main__':
    # Test the function with the sample date from the specification
    dt_local = datetime(2026, 8, 13, 10, 14, 59)
    jd = local_to_jd(dt_local)
    
    res = jamma_planets(jd)
    
    # Print formatted output exactly as requested
    print(res)
