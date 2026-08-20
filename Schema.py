from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator, Field


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

    dms_string = f"{d_int}° {m_int}' {seconds:.4f}"

    return {
        "rasi": rasi_name,
        "house": rasi_idx,
        "DMS": dms_string
    }

NAKSHATRA_NAMES = [
    {"english": "Aswini", "tamil": "Aswini"},
    {"english": "Bharani", "tamil": "Bharani"},
    {"english": "Krittika", "tamil": "Karthigai"},
    {"english": "Rohini", "tamil": "Rohini"},
    {"english": "Mrigashira", "tamil": "Mirugaseerisham"},
    {"english": "Ardra", "tamil": "Thiruvathirai"},
    {"english": "Punarvasu", "tamil": "Punarpoosam"},
    {"english": "Pushya", "tamil": "Poosam"},
    {"english": "Ashlesha", "tamil": "Ayilyam"},
    {"english": "Magha", "tamil": "Makam"},
    {"english": "Purva Phalguni", "tamil": "Pooram"},
    {"english": "Uttara Phalguni", "tamil": "Uthiram"},
    {"english": "Hasta", "tamil": "Hastham"},
    {"english": "Chitra", "tamil": "Chithirai"},
    {"english": "Swati", "tamil": "Swaathi"},
    {"english": "Vishakha", "tamil": "Visagam"},
    {"english": "Anuradha", "tamil": "Anusham"},
    {"english": "Jyestha", "tamil": "Kettai"},
    {"english": "Mula", "tamil": "Moolam"},
    {"english": "Purva Ashadha", "tamil": "Pooradam"},
    {"english": "Uttara Ashadha", "tamil": "Uthiraadam"},
    {"english": "Shravana", "tamil": "Thiruvonam"},
    {"english": "Dhanishtha", "tamil": "Avittam"},
    {"english": "Shatabhisha", "tamil": "Sadhayam"},
    {"english": "Purva Bhadrapada", "tamil": "Poorattathi"},
    {"english": "Uttara Bhadrapada", "tamil": "Uthirattathi"},
    {"english": "Revati", "tamil": "Revathi"}
]

VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

def calculate_kp_sub_lords(deg: float):
    deg = deg % 360.0
    nak_width = 360.0 / 27.0
    ni = int(deg // nak_width)
    pos_in_nak = deg % nak_width
    pada = int(pos_in_nak // (nak_width / 4.0)) + 1
    
    star_lord_idx = ni % 9
    
    sub_lords_order = []
    sub_widths = []
    for i in range(9):
        curr_idx = (star_lord_idx + i) % 9
        w = (VIMSHOTTARI_YEARS[curr_idx] / 120.0) * nak_width
        sub_lords_order.append(curr_idx)
        sub_widths.append(w)
        
    cum_sub = 0.0
    sub_lord_idx = -1
    pos_in_sub = -1.0
    sub_width = -1.0
    for idx, w in zip(sub_lords_order, sub_widths):
        if cum_sub <= pos_in_nak < cum_sub + w:
            sub_lord_idx = idx
            pos_in_sub = pos_in_nak - cum_sub
            sub_width = w
            break
        cum_sub += w
    if sub_lord_idx == -1:
        sub_lord_idx = sub_lords_order[-1]
        pos_in_sub = pos_in_nak - (nak_width - sub_widths[-1])
        sub_width = sub_widths[-1]
        
    sub_sub_lords_order = []
    sub_sub_widths = []
    for i in range(9):
        curr_idx = (sub_lord_idx + i) % 9
        w = (VIMSHOTTARI_YEARS[curr_idx] / 120.0) * sub_width
        sub_sub_lords_order.append(curr_idx)
        sub_sub_widths.append(w)
        
    cum_sub_sub = 0.0
    sub_sub_lord_idx = -1
    pos_in_sub_sub = -1.0
    sub_sub_width = -1.0
    for idx, w in zip(sub_sub_lords_order, sub_sub_widths):
        if cum_sub_sub <= pos_in_sub < cum_sub_sub + w:
            sub_sub_lord_idx = idx
            pos_in_sub_sub = pos_in_sub - cum_sub_sub
            sub_sub_width = w
            break
        cum_sub_sub += w
    if sub_sub_lord_idx == -1:
        sub_sub_lord_idx = sub_sub_lords_order[-1]
        pos_in_sub_sub = pos_in_sub - (sub_width - sub_sub_widths[-1])
        sub_sub_width = sub_sub_widths[-1]
        
    sub_sub_sub_lords_order = []
    sub_sub_sub_widths = []
    for i in range(9):
        curr_idx = (sub_sub_lord_idx + i) % 9
        w = (VIMSHOTTARI_YEARS[curr_idx] / 120.0) * sub_sub_width
        sub_sub_sub_lords_order.append(curr_idx)
        sub_sub_sub_widths.append(w)
        
    cum_sub_sub_sub = 0.0
    sub_sub_sub_lord_idx = -1
    for idx, w in zip(sub_sub_sub_lords_order, sub_sub_sub_widths):
        if cum_sub_sub_sub <= pos_in_sub_sub < cum_sub_sub_sub + w:
            sub_sub_sub_lord_idx = idx
            break
        cum_sub_sub_sub += w
    if sub_sub_sub_lord_idx == -1:
        sub_sub_sub_lord_idx = sub_sub_sub_lords_order[-1]
        
    return {
        "nakshatra_idx": ni,
        "pada": pada,
        "star_lord": VIMSHOTTARI_LORDS[star_lord_idx],
        "sub_lord": VIMSHOTTARI_LORDS[sub_lord_idx],
        "sub_sub_lord": VIMSHOTTARI_LORDS[sub_sub_lord_idx],
        "sub_sub_sub_lord": VIMSHOTTARI_LORDS[sub_sub_sub_lord_idx]
    }


class KpDetails(BaseModel):
    nakshatra_name_en: Optional[str] = None
    nakshatra_name_tam: Optional[str] = None
    pada: Optional[int] = None
    star_lord: Optional[str] = None
    sub_lord: Optional[str] = None
    sub_sub_lord: Optional[str] = None
    sub_sub_sub_lord: Optional[str] = None
    formatted_kp: Optional[str] = None

class HouseDetails(BaseModel):
    rasi: Optional[str] = None
    house: Optional[int] = None
    deg: Optional[float] = None
    DMS: Optional[str] = None
    kp_details: Optional[KpDetails] = None

    @model_validator(mode='before')
    @classmethod
    def auto_calc_from_deg(cls, data: dict) -> dict:
        if isinstance(data, dict) and data.get('deg') is not None:
            calculated = absolute_to_rasi_dms(data['deg'])
            data['rasi'] = calculated['rasi']
            data['house'] = calculated['house']
            data['DMS'] = calculated['DMS']
            
            # Calculate Nakshatra and KP subdivisions
            kp = calculate_kp_sub_lords(data['deg'])
            nak_name_eng = NAKSHATRA_NAMES[kp["nakshatra_idx"]]["english"]
            nak_name_tam = NAKSHATRA_NAMES[kp["nakshatra_idx"]]["tamil"]
            pada = kp["pada"]
            star_lord = kp["star_lord"]
            sub_lord = kp["sub_lord"]
            sub_sub_lord = kp["sub_sub_lord"]
            sub_sub_sub_lord = kp["sub_sub_sub_lord"]
            
            data['kp_details'] = {
                'nakshatra_name_en': nak_name_eng,
                'nakshatra_name_tam': nak_name_tam,
                'pada': pada,
                'star_lord': star_lord,
                'sub_lord': sub_lord,
                'sub_sub_lord': sub_sub_lord,
                'sub_sub_sub_lord': sub_sub_sub_lord,
                'formatted_kp': f"{nak_name_eng}-{pada} / {nak_name_tam}-{pada},   {star_lord}, {sub_lord},  {sub_sub_lord}, {sub_sub_sub_lord}"
            }
            
        return data

class ReadableHouseDetails(HouseDetails):
    @model_validator(mode='before')
    @classmethod
    def auto_calc_from_deg(cls, data: dict) -> dict:
        data = super().auto_calc_from_deg(data)
        if data.get('house') is not None:
            data['house'] += 1
        return data

class UdhayamOutput(BaseModel):
    housedetails: HouseDetails
    sunrise: datetime
    sunset: datetime
    fraction: float
    method: str

class PlanetDetails(BaseModel):
    planet_name: str
    housedetails: HouseDetails
    is_retrograde: bool

class PlanetaryCollections(BaseModel):
    ayanamsa: Optional[PlanetDetails] = None
    acendant_sidereal: Optional[PlanetDetails]
    acendant_tropical: Optional[PlanetDetails]
    sun: PlanetDetails
    moon: PlanetDetails
    mars: PlanetDetails
    mercury: PlanetDetails
    jupiter: PlanetDetails
    venus: PlanetDetails
    saturn: PlanetDetails
    rahu: PlanetDetails
    ketu: PlanetDetails

class JamaPlanetDetails(BaseModel):
    planet_name: str
    housedetails: HouseDetails
    is_retrograde: bool = True
    rasi_name_en: str
    rasi_name_sanskrit: str

class JamaPlanetaryCollections(BaseModel):
    sun: JamaPlanetDetails
    mars: JamaPlanetDetails
    jupiter: JamaPlanetDetails
    mercury: JamaPlanetDetails
    venus: JamaPlanetDetails
    saturn: JamaPlanetDetails
    moon: JamaPlanetDetails
    snake: JamaPlanetDetails

class VargaDetails(BaseModel):
    varga_code: str
    harmonic: int
    name: str
    rasi: str
    sign_index: int
    house: int  # 0 to 11 (0-indexed relative to Lagna in this Varga chart)
    deg_in_varga: float
    DMS: str
    sign_lord: str
    kp_details: Optional[KpDetails] = None

class VargaCollections(BaseModel):
    d1: Optional[VargaDetails] = None
    d2: Optional[VargaDetails] = None
    d3: Optional[VargaDetails] = None
    d4: Optional[VargaDetails] = None
    d5: Optional[VargaDetails] = None
    d6: Optional[VargaDetails] = None
    d7: Optional[VargaDetails] = None
    d8: Optional[VargaDetails] = None
    d9: Optional[VargaDetails] = None
    d10: Optional[VargaDetails] = None
    d11: Optional[VargaDetails] = None
    d12: Optional[VargaDetails] = None
    d16: Optional[VargaDetails] = None
    d20: Optional[VargaDetails] = None
    d24: Optional[VargaDetails] = None
    d27: Optional[VargaDetails] = None
    d30: Optional[VargaDetails] = None
    d40: Optional[VargaDetails] = None
    d45: Optional[VargaDetails] = None
    d60: Optional[VargaDetails] = None
    d72: Optional[VargaDetails] = None
    d81: Optional[VargaDetails] = None
    d108: Optional[VargaDetails] = None
    d144: Optional[VargaDetails] = None
    d150: Optional[VargaDetails] = None
    d300: Optional[VargaDetails] = None

def calculate_single_varga_sign(lon: float, d: int) -> tuple[int, float]:
    lon = lon % 360.0
    s_idx = int(lon // 30.0)
    deg_in_sign = lon % 30.0
    div_w = 30.0 / d
    k = min(int(deg_in_sign // div_w), d - 1)
    rem = deg_in_sign - (k * div_w)
    deg_varga = (rem * d) % 30.0

    is_odd = (s_idx % 2 == 0)
    modality = s_idx % 3
    element = s_idx % 4

    if d == 1: target = s_idx
    elif d == 2: target = (4 if k == 0 else 3) if is_odd else (3 if k == 0 else 4)
    elif d == 3: target = (s_idx + 4 * k) % 12
    elif d == 4: target = (s_idx + 3 * k) % 12
    elif d == 5:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 6: target = ((0 if is_odd else 6) + k) % 12
    elif d == 7: target = ((s_idx if is_odd else (s_idx + 6)) + k) % 12
    elif d == 8:
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        target = (start + k) % 12
    elif d == 9: target = int(lon // (30.0 / 9.0)) % 12
    elif d == 10: target = ((s_idx if is_odd else (s_idx + 8)) + k) % 12
    elif d == 11: target = (12 - (s_idx + k) % 12) % 12
    elif d == 12: target = (s_idx + k) % 12
    elif d == 16:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 20:
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        target = (start + k) % 12
    elif d == 24: target = ((4 if is_odd else 3) + k) % 12
    elif d == 27:
        start = 0 if element == 0 else (3 if element == 1 else (6 if element == 2 else 9))
        target = (start + k) % 12
    elif d == 30:
        if is_odd:
            target = 0 if deg_in_sign < 5 else (10 if deg_in_sign < 10 else (8 if deg_in_sign < 18 else (2 if deg_in_sign < 25 else 6)))
        else:
            target = 1 if deg_in_sign < 5 else (5 if deg_in_sign < 12 else (11 if deg_in_sign < 20 else (9 if deg_in_sign < 25 else 7)))
    elif d == 40: target = ((0 if is_odd else 6) + k) % 12
    elif d == 45:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 60: target = (s_idx + k) % 12
    elif d == 72:
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        target = (start + k) % 12
    elif d == 81:
        start = 0 if element == 0 else (9 if element == 1 else (6 if element == 2 else 3))
        target = (start + k) % 12
    elif d == 108: target = int(lon // (30.0 / 108.0)) % 12
    elif d == 144: target = (s_idx + k) % 12
    elif d == 150: target = (s_idx + k) % 12
    elif d == 300: target = (s_idx + k) % 12
    else: target = (s_idx + k) % 12

    return target, deg_varga

class Input(BaseModel):
    dt: datetime
    lat: float
    lon: float
    alt: float = 0.0
    is_local: bool = True
    time_offset: float = 5.5
    method: str = "vedic"


VARGA_NAMES = {
    1: "Rasi", 2: "Hora", 3: "Drekkana", 4: "Chaturthamsa", 5: "Panchamsha",
    6: "Shashtamsha", 7: "Saptamsha", 8: "Ashtamsha", 9: "Navamsha", 10: "Dasamsha",
    11: "Rudramsha", 12: "Dwadasamsha", 16: "Shodashamsha", 20: "Vimsamsha",
    24: "Siddhamsa", 27: "Saptavimsamsha", 30: "Trimsamsha", 40: "Khavedamsha",
    45: "Akshavedamsha", 60: "Shashtiamsha", 72: "Ashtamamsha", 81: "Nava-Navamsha",
    108: "Ashtottaramsa", 144: "Dwadasamsa-Dwadasamsha", 150: "Nadiamsa", 300: "Ardha-Nadiamsa"
}

RASI_NAMES_TAMIL = [
    "Mesham", "Rishabham", "Mithunam", "Kadagam",
    "Simmam", "Kanni", "Thulaam", "Viruchigam",
    "Dhanusu", "Magaram", "Kumbam", "Meenam"
]

RASI_LORDS_NAMES = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

def build_all_vargas(planet_deg: float, ascendant_deg: Optional[float] = None) -> VargaCollections:
    if ascendant_deg is None:
        ascendant_deg = planet_deg

    vargas_dict = {}
    for d, name in VARGA_NAMES.items():
        # 1. Planet sign in D-N (0 to 11)
        p_sign, deg_v = calculate_single_varga_sign(planet_deg, d)
        # 2. Ascendant sign in D-N (0 to 11)
        asc_sign, _ = calculate_single_varga_sign(ascendant_deg, d)
        # 3. House index (0 to 11) relative to Ascendant Lagna in that Varga
        house_num = (p_sign - asc_sign) % 12

        # DMS string in Varga
        d_int = int(deg_v)
        m_dec = (deg_v - d_int) * 60
        m_int = int(m_dec)
        s_val = (m_dec - m_int) * 60
        dms_str = f"{d_int}° {m_int}' {s_val:.4f}\""

        # KP Details inside Varga absolute degree
        abs_varga_deg = (p_sign * 30.0) + deg_v
        kp_raw = calculate_kp_sub_lords(abs_varga_deg)
        nak_eng = NAKSHATRA_NAMES[kp_raw["nakshatra_idx"]]["english"]
        nak_tam = NAKSHATRA_NAMES[kp_raw["nakshatra_idx"]]["tamil"]

        kp_obj = KpDetails(
            nakshatra_name_en=nak_eng,
            nakshatra_name_tam=nak_tam,
            pada=kp_raw["pada"],
            star_lord=kp_raw["star_lord"],
            sub_lord=kp_raw["sub_lord"],
            sub_sub_lord=kp_raw["sub_sub_lord"],
            sub_sub_sub_lord=kp_raw["sub_sub_sub_lord"],
            formatted_kp=f"{nak_eng}-{kp_raw['pada']}, {kp_raw['star_lord']}, {kp_raw['sub_lord']}, {kp_raw['sub_sub_lord']}"
        )

        v_detail = VargaDetails(
            varga_code=f"D-{d}",
            harmonic=d,
            name=name,
            rasi=RASI_NAMES_TAMIL[p_sign],
            sign_index=p_sign,
            house=house_num,
            deg_in_varga=deg_v,
            DMS=dms_str,
            sign_lord=RASI_LORDS_NAMES[p_sign],
            kp_details=kp_obj
        )
        vargas_dict[f"d{d}"] = v_detail

    return VargaCollections(**vargas_dict)

class ComprehensivePlanetDetails(BaseModel):
    planet_name: str
    deg: float
    is_retrograde: bool = False
    housedetails: HouseDetails
    vargas: Optional[VargaCollections] = None

    @model_validator(mode='before')
    @classmethod
    def auto_calc(cls, data: dict) -> dict:
        if isinstance(data, dict) and data.get('deg') is not None:
            deg = data['deg']
            asc_deg = data.get('ascendant_deg', deg)
            if data.get('housedetails') is None:
                data['housedetails'] = HouseDetails(deg=deg)
            if data.get('vargas') is None:
                data['vargas'] = build_all_vargas(deg, asc_deg)
        return data

class ComprehensiveHoroscope(BaseModel):
    ascendant: ComprehensivePlanetDetails
    sun: ComprehensivePlanetDetails
    moon: ComprehensivePlanetDetails
    mars: ComprehensivePlanetDetails
    mercury: ComprehensivePlanetDetails
    jupiter: ComprehensivePlanetDetails
    venus: ComprehensivePlanetDetails
    saturn: ComprehensivePlanetDetails
    rahu: ComprehensivePlanetDetails
    ketu: ComprehensivePlanetDetails

    @classmethod
    def from_planetary_collections(
        cls,
        planets: "PlanetaryCollections",
        ascendant_deg: Optional[float] = None
    ) -> "ComprehensiveHoroscope":
        if ascendant_deg is None:
            if planets.acendant_sidereal is not None:
                ascendant_deg = planets.acendant_sidereal.housedetails.deg
            else:
                ascendant_deg = 0.0

        ascendant_details = ComprehensivePlanetDetails(
            planet_name="Ascendant",
            deg=ascendant_deg,
            ascendant_deg=ascendant_deg,
            is_retrograde=False
        )

        return cls(
            ascendant=ascendant_details,
            sun=ComprehensivePlanetDetails(planet_name="Sun", deg=planets.sun.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.sun.is_retrograde),
            moon=ComprehensivePlanetDetails(planet_name="Moon", deg=planets.moon.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.moon.is_retrograde),
            mars=ComprehensivePlanetDetails(planet_name="Mars", deg=planets.mars.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.mars.is_retrograde),
            mercury=ComprehensivePlanetDetails(planet_name="Mercury", deg=planets.mercury.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.mercury.is_retrograde),
            jupiter=ComprehensivePlanetDetails(planet_name="Jupiter", deg=planets.jupiter.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.jupiter.is_retrograde),
            venus=ComprehensivePlanetDetails(planet_name="Venus", deg=planets.venus.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.venus.is_retrograde),
            saturn=ComprehensivePlanetDetails(planet_name="Saturn", deg=planets.saturn.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.saturn.is_retrograde),
            rahu=ComprehensivePlanetDetails(planet_name="Rahu", deg=planets.rahu.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.rahu.is_retrograde),
            ketu=ComprehensivePlanetDetails(planet_name="Ketu", deg=planets.ketu.housedetails.deg, ascendant_deg=ascendant_deg, is_retrograde=planets.ketu.is_retrograde)
        )

    @classmethod
    def from_longitudes(
        cls,
        planet_degrees: dict[str, float],
        ascendant_deg: float
    ) -> "ComprehensiveHoroscope":
        ascendant_details = ComprehensivePlanetDetails(
            planet_name="Ascendant",
            deg=ascendant_deg,
            ascendant_deg=ascendant_deg,
            is_retrograde=False
        )
        planets_args = {"ascendant": ascendant_details}
        for name in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]:
            deg_val = planet_degrees.get(name, planet_degrees.get(name.capitalize(), 0.0))
            planets_args[name] = ComprehensivePlanetDetails(
                planet_name=name.capitalize(),
                deg=deg_val,
                ascendant_deg=ascendant_deg,
                is_retrograde=False
            )
        return cls(**planets_args)

class VargaPlanetaryCollection(BaseModel):
    varga_code: str
    harmonic: int
    name: str
    ascendant: VargaDetails
    sun: VargaDetails
    moon: VargaDetails
    mars: VargaDetails
    mercury: VargaDetails
    jupiter: VargaDetails
    venus: VargaDetails
    saturn: VargaDetails
    rahu: VargaDetails
    ketu: VargaDetails

class DivisionalChartsGroup(BaseModel):
    d1: Optional[VargaPlanetaryCollection] = None
    d2: Optional[VargaPlanetaryCollection] = None
    d3: Optional[VargaPlanetaryCollection] = None
    d4: Optional[VargaPlanetaryCollection] = None
    d5: Optional[VargaPlanetaryCollection] = None
    d6: Optional[VargaPlanetaryCollection] = None
    d7: Optional[VargaPlanetaryCollection] = None
    d8: Optional[VargaPlanetaryCollection] = None
    d9: Optional[VargaPlanetaryCollection] = None
    d10: Optional[VargaPlanetaryCollection] = None
    d11: Optional[VargaPlanetaryCollection] = None
    d12: Optional[VargaPlanetaryCollection] = None
    d16: Optional[VargaPlanetaryCollection] = None
    d20: Optional[VargaPlanetaryCollection] = None
    d24: Optional[VargaPlanetaryCollection] = None
    d27: Optional[VargaPlanetaryCollection] = None
    d30: Optional[VargaPlanetaryCollection] = None
    d40: Optional[VargaPlanetaryCollection] = None
    d45: Optional[VargaPlanetaryCollection] = None
    d60: Optional[VargaPlanetaryCollection] = None
    d72: Optional[VargaPlanetaryCollection] = None
    d81: Optional[VargaPlanetaryCollection] = None
    d108: Optional[VargaPlanetaryCollection] = None
    d144: Optional[VargaPlanetaryCollection] = None
    d150: Optional[VargaPlanetaryCollection] = None
    d300: Optional[VargaPlanetaryCollection] = None

def build_divisional_charts_group(
    planets: "PlanetaryCollections",
    ascendant_deg: Optional[float] = None
) -> DivisionalChartsGroup:
    if ascendant_deg is None:
        ascendant_deg = planets.acendant_sidereal.housedetails.deg if planets.acendant_sidereal else 0.0

    planet_map = {
        "ascendant": ascendant_deg,
        "sun": planets.sun.housedetails.deg,
        "moon": planets.moon.housedetails.deg,
        "mars": planets.mars.housedetails.deg,
        "mercury": planets.mercury.housedetails.deg,
        "jupiter": planets.jupiter.housedetails.deg,
        "venus": planets.venus.housedetails.deg,
        "saturn": planets.saturn.housedetails.deg,
        "rahu": planets.rahu.housedetails.deg,
        "ketu": planets.ketu.housedetails.deg,
    }

    group_dict = {}
    for d, name in VARGA_NAMES.items():
        asc_sign, _ = calculate_single_varga_sign(ascendant_deg, d)
        varga_bodies = {}
        for p_name, deg in planet_map.items():
            p_sign, deg_v = calculate_single_varga_sign(deg, d)
            house_num = (p_sign - asc_sign) % 12

            d_int = int(deg_v)
            m_dec = (deg_v - d_int) * 60
            m_int = int(m_dec)
            s_val = (m_dec - m_int) * 60
            dms_str = f"{d_int}° {m_int}' {s_val:.4f}\""

            abs_varga_deg = (p_sign * 30.0) + deg_v
            kp_raw = calculate_kp_sub_lords(abs_varga_deg)
            nak_eng = NAKSHATRA_NAMES[kp_raw["nakshatra_idx"]]["english"]
            nak_tam = NAKSHATRA_NAMES[kp_raw["nakshatra_idx"]]["tamil"]

            kp_obj = KpDetails(
                nakshatra_name_en=nak_eng,
                nakshatra_name_tam=nak_tam,
                pada=kp_raw["pada"],
                star_lord=kp_raw["star_lord"],
                sub_lord=kp_raw["sub_lord"],
                sub_sub_lord=kp_raw["sub_sub_lord"],
                sub_sub_sub_lord=kp_raw["sub_sub_sub_lord"],
                formatted_kp=f"{nak_eng}-{kp_raw['pada']}, {kp_raw['star_lord']}, {kp_raw['sub_lord']}, {kp_raw['sub_sub_lord']}"
            )

            v_detail = VargaDetails(
                varga_code=f"D-{d}",
                harmonic=d,
                name=name,
                rasi=RASI_NAMES_TAMIL[p_sign],
                sign_index=p_sign,
                house=house_num,
                deg_in_varga=deg_v,
                DMS=dms_str,
                sign_lord=RASI_LORDS_NAMES[p_sign],
                kp_details=kp_obj
            )
            varga_bodies[p_name] = v_detail

        group_dict[f"d{d}"] = VargaPlanetaryCollection(
            varga_code=f"D-{d}",
            harmonic=d,
            name=name,
            **varga_bodies
        )

    return DivisionalChartsGroup(**group_dict)

class MainChartDetails(BaseModel):
    ascendant_sidereal: PlanetDetails
    ascendant_tropical: Optional[PlanetDetails] = None
    udhayam: UdhayamOutput
    arudham: HouseDetails
    kavippu: HouseDetails
    planets: PlanetaryCollections
    jamma_planets: JamaPlanetaryCollections

class CompleteJamakkolHoroscopeOutput(BaseModel):
    datetime_utc: datetime
    datetime_local: datetime
    latitude: float
    longitude: float
    altitude: float
    julian_day: float
    ayanamsa: float
    main_chart: MainChartDetails
    divisional_charts: DivisionalChartsGroup

if __name__ == '__main__':
    print("--- Using HouseDetails (0-indexed) ---")
    normal_house = HouseDetails(deg=185.5)
    print(normal_house)

    print("\n--- Using ReadableHouseDetails (1-indexed) ---")
    human_house = ReadableHouseDetails(deg=185.5)
    print(human_house)

    print("\n--- Comprehensive Planet Details with all D-1 to D-60 Vargas and House Index (0-11) ---")
    test_planet = ComprehensivePlanetDetails(
        planet_name="Jupiter",
        deg=74.25,  # 14°15' Gemini
        ascendant_deg=42.15  # 12°09' Taurus Lagna
    )
    print(f"Planet: {test_planet.planet_name} at {test_planet.deg}°")
    print(f"D-1 (Rasi)     : {test_planet.vargas.d1.rasi} | House Index: {test_planet.vargas.d1.house} | {test_planet.vargas.d1.DMS}")
    print(f"D-9 (Navamsha) : {test_planet.vargas.d9.rasi} | House Index: {test_planet.vargas.d9.house} | {test_planet.vargas.d9.DMS}")
    print(f"D-10 (Dasamsha): {test_planet.vargas.d10.rasi} | House Index: {test_planet.vargas.d10.house} | {test_planet.vargas.d10.DMS}")
    print(f"D-9 KP Sub-Lord: {test_planet.vargas.d9.kp_details.formatted_kp}")



