from datetime import datetime, timedelta
import swisseph as swe

from Schema import HouseDetails
from calc import local_to_jd, jd_to_local, absolute_to_rasi_dms
from planets import get_planets

def arudam(dt_local: datetime) -> HouseDetails:


    total_sec = dt_local.minute * 60.0 + dt_local.second

    arudam_rasi = total_sec // 300
    seconds_in_rasi = total_sec % 300


    deg_in_rasi = seconds_in_rasi * (30.0 / 300.0)
    arudham_deg = (arudam_rasi * 30.0 + deg_in_rasi) % 360.0

    return HouseDetails(deg=arudham_deg)

def main():
    dt = datetime(2026, 8, 13, 10, 14, 59)
    res = arudam(dt)
    print(res)

if __name__ == '__main__':
    dt_local = datetime(2007, 10, 21, 0, 0, 0)
    jd = local_to_jd(dt_local)
    main()