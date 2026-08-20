from datetime import datetime
from email.mime import audio
from rich import print
from Schema import HouseDetails
from arudam import arudam
from calc import absolute_to_rasi_dms, local_to_jd, dt_jd
from planets import get_planets
from udhayam import udhayam


def get_soorya_veedi(sun_rasi: int):

    if sun_rasi in [1, 2, 3, 4]:
        return 0
    elif sun_rasi in [0, 5, 6, 11]:
        return 1
    else:
        return 2


def kavipu(
        udhyam_rasi: int,
        arudham_rasi: int,
        arudham_deg_in_rasi: float,  # Add this parameter
        sun_rasi: int,
):
    veedi_rasi = get_soorya_veedi(sun_rasi=sun_rasi)
    kavippu_rasi = (udhyam_rasi + veedi_rasi - arudham_rasi) % 12

    arudham_deg_in_realtive = arudham_deg_in_rasi % 30.0
    kavippu_deg_in_rasi = 30.0 - arudham_deg_in_realtive - (1.0 /3600.0)
    kavippu_deg = kavippu_rasi * 30 + kavippu_deg_in_rasi

    return HouseDetails(deg=kavippu_deg)

if __name__ == '__main__':
    dt_local = datetime(2026, 8, 13, 10, 14, 59)
    jd = local_to_jd(dt_local)
    planets = get_planets(jd)
    lat, lon, alt = 12.986, 77.470, 820.0

    sun = planets.sun
    arudam = arudam(dt_local)
    udhayam = udhayam(jd_query=jd, lat=lat, lon=lon, alt=alt)
    print(kavipu(udhayam.housedetails.house, arudam.house, arudam.deg, sun.housedetails.house))

