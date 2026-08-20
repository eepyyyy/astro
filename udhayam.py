from datetime import datetime, timedelta
import swisseph as swe
from rich import print
from Schema import UdhayamOutput, HouseDetails
from calc import local_to_jd, jd_to_local, absolute_to_rasi_dms
from planets import get_planets

swe.set_sid_mode(27, 0, 0)

def udhayam(jd_query, lat: float, lon: float, alt: float, method: str = "vedic", sid_mode: int = 27):
    """
    Calculate the Jamakkol Udhayam for a query time.
    
    Supports:
    - 'vedic': Apparent Sunrise/Sunset (upper limb + refraction). Offset by 50' to get geometric Sun.
    - 'astronomical': True Geometric Sunrise/Sunset (disc center, no refraction).
    """
    # Set the sidereal mode (27 = True Chitra, 1 = Lahiri)
    swe.set_sid_mode(sid_mode, 0, 0)

    geoops = [lon, lat, alt]

    dt_local = jd_to_local(jd_query)
    dt_midnight = datetime(dt_local.year, dt_local.month, dt_local.day, 0, 0, 0)
    midnight = local_to_jd(dt_midnight)


    method_clean = method.lower()
    if method_clean == "vedic":
        flags = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    elif method_clean == "astronomical":
        flags = 0
    else:
        raise ValueError("Invalid method. Choose 'vedic' or 'astronomical'.")

    # Today's rise/set
    _, sr_res = swe.rise_trans(midnight, swe.SUN, swe.CALC_RISE | flags, geoops, 0, 0)
    _, ss_res = swe.rise_trans(midnight, swe.SUN, swe.CALC_SET | flags, geoops, 0, 0)
    sr, ss = sr_res[0], ss_res[0]

    # Yesterday's rise/set
    _, psr_res = swe.rise_trans(midnight - 1, swe.SUN, swe.CALC_RISE | flags, geoops, 0, 0)
    _, pss_res = swe.rise_trans(midnight - 1, swe.SUN, swe.CALC_SET | flags, geoops, 0, 0)
    psr, pss = psr_res[0], pss_res[0]

    # Tomorrow's rise/set
    _, nsr_res = swe.rise_trans(midnight + 1, swe.SUN, swe.CALC_RISE | flags, geoops, 0, 0)
    nsr = nsr_res[0]

    # Determine the active span and active Sunrise for Sun longitude
    if sr <= jd_query < ss:
        span_start, span_end = sr, ss
        sunrise_for_sun = sr
        active_ss = ss
    elif jd_query < sr:
        span_start, span_end = pss, sr  # FIXED: span starts at yesterday's sunset pss, not psr
        sunrise_for_sun = psr
        active_ss = pss
    else:
        span_start, span_end = ss, nsr
        sunrise_for_sun = sr
        active_ss = ss


    fraction = (jd_query - span_start) / (span_end - span_start)

    # Calculate Sun longitude at Sunrise
    res_sr, _, _ = swe.calc_ut(sunrise_for_sun, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    sun_lon_sr = res_sr[0]

    # Starting degree correction
    # Astronomical method is apparent (limb + refraction) but the Udhayam starts at the geometric Sun position
    # The difference is 34' (refraction) + 16' (semi-diameter) = 50' (0.8333 degrees)
    if method == "astronomical":
        start_deg = sun_lon_sr - (50.0 / 60.0)
    else:
        start_deg = sun_lon_sr

    udhayam_deg = (start_deg + fraction * 360.0) % 360.0

    house_obj = HouseDetails(deg=udhayam_deg)

    return UdhayamOutput(
        housedetails=house_obj,
        sunrise= jd_to_local(sunrise_for_sun),
        sunset= jd_to_local(active_ss),
        fraction=fraction,
        method=method
    )



if __name__ == '__main__':
    dt_local = datetime(2026, 8, 13, 10, 14, 59)
    jd = local_to_jd(dt_local)

    lat, lon, alt = 12.986, 77.470, 820.0

    for method in ["vedic", "astronomical"]:
        res = udhayam(jd, lat, lon, alt, method=method, sid_mode=27)
        print(res)




