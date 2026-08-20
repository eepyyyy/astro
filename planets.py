from Schema import PlanetDetails, HouseDetails, PlanetaryCollections
from datetime import datetime
from calc import local_to_jd
import swisseph as swe
from rich import print

swe.set_ephe_path("")
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

PLANETS_ID = {
    "sun" : swe.SUN,
    "moon" : swe.MOON,
    "mars" : swe.MARS,
    "mercury" : swe.MERCURY,
    "jupiter" : swe.JUPITER,
    "venus" : swe.VENUS,
    "saturn" : swe.SATURN,
    "rahu" : swe.MEAN_NODE,
}

def get_planets(jd: float,lat:float,lon:float) -> PlanetaryCollections:
    raw = {}
    for name, pid in PLANETS_ID.items():
        res, rflag, serr = swe.calc_ut(jd, pid, FLAGS)
        raw[name] = {"lon": res[0], "speed": res[3]}

    rahu_lon = raw["rahu"]["lon"]
    raw["ketu"] = {
        "lon": (rahu_lon + 180) % 360,
        "speed": -raw['rahu']['speed'],
    }
    Planets = {}
    for name,data in raw.items():
        retrograde = True if name == "ketu" else data["speed"] < 0
        Planets[name] = PlanetDetails(
            planet_name=name,
            housedetails=HouseDetails(deg=data['lon']),
            is_retrograde=retrograde
        )
    aya = swe.get_ayanamsa_ut(jd)

    cusps, ascmc = swe.houses(jd, lat, lon, b'p')
    tropical_asc = ascmc[0]

    ayanamasa = swe.get_ayanamsa_ut(jd)

    sidereal_asc = (tropical_asc - ayanamasa) % 360
    return PlanetaryCollections(**Planets,
                                ayanamsa=PlanetDetails(
                                    planet_name="ayanamsa",
                                    housedetails=HouseDetails(deg=aya),
                                    is_retrograde=False
                                ),
                                acendant_sidereal=PlanetDetails(
                                    planet_name="acendant_sidereal",
                                    housedetails=HouseDetails(deg=sidereal_asc),
                                    is_retrograde=False,
                                ),
                                acendant_tropical=PlanetDetails(
                                    planet_name="acendant_tropical",
                                    housedetails=HouseDetails(deg=tropical_asc),
                                    is_retrograde=False,
                                )
                                )


if __name__ == '__main__':
    dt_local = datetime(2026, 8, 13, 10, 14, 59)
    jd = local_to_jd(dt_local)

    lat, lon, alt = 12.986, 77.470, 820.0
    print(get_planets(jd, lat, lon))




