import swisseph as swe
from datetime import datetime, timedelta

def dt_jd(dt_utc: datetime) -> float:
    """Convert a UTC datetime to Julian Day Number."""
    h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, h, swe.GREG_CAL)


def local_to_jd(dt_local: datetime, tz_offset_hours: float = 5.5) -> float:
    dt_utc = dt_local - timedelta(hours=tz_offset_hours)
    hour_decimal = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)

def jd_to_local(jd_val: float, tz_offset: float = 5.5) -> datetime:
    """Convert a Julian Day Number to a local timezone datetime."""
    # 1. Convert Julian Day back to UTC year, month, day, and decimal hour
    y, m, d, h_dec = swe.revjul(jd_val, swe.GREG_CAL)

    # 2. Reconstruct UTC datetime using timedelta to handle the fractional hour
    dt_utc = datetime(y, m, d) + timedelta(hours=h_dec)

    # 3. Add the local timezone offset (5.5 for IST)
    dt_local = dt_utc + timedelta(hours=tz_offset)
    return dt_local

def absolute_to_rasi_dms(absolute_deg: float):
    absolute_deg = absolute_deg % 360.0

    rasi_idx = int(absolute_deg // 30)
    rasi_names = [
        "Mesham", "Rishabham", "Mithunam", "Kadagam",
        "Simmam", "Kanni", "Thulaam", "Viruchigam",
        "Dhanusu", "Magaram", "Kumbam", "Meenam"
    ]

    rasi_name = rasi_names[rasi_idx]

    deg_in_rasi = absolute_deg % 30

    d_int = int(deg_in_rasi)
    minutes_decimal = (deg_in_rasi - d_int) * 60
    m_int = int(minutes_decimal)
    seconds = (minutes_decimal - m_int) * 60

    return f"{rasi_name} ({rasi_idx + 1}) -- {d_int}° {m_int}' {seconds:.4f}\""

if __name__ == '__main__':
    dt_local = datetime(2026, 8, 4, 14, 30, 0)
    dt_utc   = dt_local - timedelta(hours=5.5)

    test = local_to_jd(dt_local)
    print(test)

