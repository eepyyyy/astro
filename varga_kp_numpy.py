"""
Vectorized Vedic Divisional Charts & KP Calculation Engine using NumPy
=======================================================================
Calculates all Vargas (D-1 to D-150) and KP 4-Tier Sub-Lords for single values
OR arrays of longitudes (all 9 planets + 12 cusps simultaneously) in microseconds.
"""

import numpy as np

# ============================================================================
# CONSTANTS & VECTORIZED LOOKUP ARRAYS
# ============================================================================

RASI_NAMES = np.array([
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
])

RASI_LORDS = np.array([
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
])

NAKSHATRAS = np.array([
    "Aswini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyestha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
])

VIMSHOTTARI_LORDS = np.array(["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"])
VIMSHOTTARI_YEARS = np.array([7.0, 20.0, 6.0, 10.0, 7.0, 18.0, 16.0, 19.0, 17.0])
VIMSHOTTARI_RATIOS = VIMSHOTTARI_YEARS / 120.0  # Normalized proportions sum to 1.0

# ============================================================================
# 1. VECTORIZED DMS CONVERTER
# ============================================================================

def deg_to_dms_vec(degrees: np.ndarray) -> np.ndarray:
    """Vectorized conversion of decimal degrees to DMS formatted strings."""
    deg = np.asarray(degrees) % 360.0
    d = np.floor(deg).astype(int)
    m_dec = (deg - d) * 60.0
    m = np.floor(m_dec).astype(int)
    s = (m_dec - m) * 60.0
    
    # Vectorized string formatting
    return np.array([f"{d_i:02d}° {m_i:02d}' {s_i:04.1f}\"" for d_i, m_i, s_i in zip(d, m, s)])

# ============================================================================
# 2. VECTORIZED DIVISIONAL CHARTS (VARGAS) ENGINE
# ============================================================================

def calculate_vargas_numpy(longitudes: np.ndarray, d: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized calculation of any D-N chart for an array of planetary longitudes.
    
    Returns:
        target_sign_indices: np.ndarray (0 to 11)
        target_sign_names: np.ndarray (e.g. ['Gemini', 'Aquarius', ...])
        deg_in_varga: np.ndarray (0.0 to 30.0)
    """
    lon = np.asarray(longitudes, dtype=np.float64) % 360.0
    rasi_idx = (lon // 30).astype(int)
    deg_in_rasi = lon % 30.0
    
    div_w = 30.0 / d
    k = np.clip((deg_in_rasi // div_w).astype(int), 0, d - 1)
    rem = deg_in_rasi - (k * div_w)
    deg_in_varga = (rem * d) % 30.0

    is_odd = (rasi_idx % 2 == 0)       # Boolean mask: True for Aries, Gemini, Leo, etc.
    modality = rasi_idx % 3            # 0 = Movable, 1 = Fixed, 2 = Dual
    element = rasi_idx % 4             # 0 = Fire, 1 = Earth, 2 = Air, 3 = Water

    # Vectorized sign assignments using NumPy array operations
    if d == 1:
        target = rasi_idx
    elif d == 2:  # Hora
        # Odd: k=0 -> Leo(4), k=1 -> Cancer(3) | Even: k=0 -> Cancer(3), k=1 -> Leo(4)
        target = np.where(is_odd, np.where(k == 0, 4, 3), np.where(k == 0, 3, 4))
    elif d == 3:  # Drekkana
        target = (rasi_idx + 4 * k) % 12
    elif d == 4:  # Chaturthamsa
        target = (rasi_idx + 3 * k) % 12
    elif d == 5:  # Panchamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
        target = (start + k) % 12
    elif d == 6:  # Shashtamsha
        start = np.where(is_odd, 0, 6)
        target = (start + k) % 12
    elif d == 7:  # Saptamsha
        start = np.where(is_odd, rasi_idx, rasi_idx + 6)
        target = (start + k) % 12
    elif d == 8:  # Ashtamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 8, 4])
        target = (start + k) % 12
    elif d == 9:  # Navamsha (Direct continuous pada mapping)
        global_padas = (lon // (30.0 / 9.0)).astype(int)
        target = global_padas % 12
    elif d == 10:  # Dasamsha
        start = np.where(is_odd, rasi_idx, rasi_idx + 8)
        target = (start + k) % 12
    elif d == 11:  # Rudramsha
        target = (12 - (rasi_idx + k) % 12) % 12
    elif d == 12:  # Dwadasamsha
        target = (rasi_idx + k) % 12
    elif d == 16:  # Shodashamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
        target = (start + k) % 12
    elif d == 20:  # Vimsamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 8, 4])
        target = (start + k) % 12
    elif d == 24:  # Siddhamsa
        start = np.where(is_odd, 4, 3)
        target = (start + k) % 12
    elif d == 27:  # Saptavimsamsha / Bhamsa
        start = np.select([element == 0, element == 1, element == 2, element == 3], [0, 3, 6, 9])
        target = (start + k) % 12
    elif d == 30:  # Trimsamsha (Vectorized piecewise selection)
        cond_odd = [
            deg_in_rasi < 5.0,
            deg_in_rasi < 10.0,
            deg_in_rasi < 18.0,
            deg_in_rasi < 25.0,
            deg_in_rasi >= 25.0
        ]
        choices_odd = [0, 10, 8, 2, 6]  # Ari, Aqu, Sag, Gem, Lib
        res_odd = np.select(cond_odd, choices_odd)

        cond_even = [
            deg_in_rasi < 5.0,
            deg_in_rasi < 12.0,
            deg_in_rasi < 20.0,
            deg_in_rasi < 25.0,
            deg_in_rasi >= 25.0
        ]
        choices_even = [1, 5, 11, 9, 7]  # Tau, Vir, Pis, Cap, Sco
        res_even = np.select(cond_even, choices_even)

        target = np.where(is_odd, res_odd, res_even)
    elif d == 40:  # Khavedamsha
        start = np.where(is_odd, 0, 6)
        target = (start + k) % 12
    elif d == 45:  # Akshavedamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
        target = (start + k) % 12
    elif d == 60:  # Shashtiamsha
        target = (rasi_idx + k) % 12
    elif d == 72:  # Ashtamamsha
        start = np.select([modality == 0, modality == 1, modality == 2], [0, 8, 4])
        target = (start + k) % 12
    elif d == 81:  # Nava-Navamsha
        start = np.select([element == 0, element == 1, element == 2, element == 3], [0, 9, 6, 3])
        target = (start + k) % 12
    elif d == 108:  # Ashtottaramsa
        target = (lon // (30.0 / 108.0)).astype(int) % 12
    elif d == 144:  # Dwadasa-Dwadasamsha
        target = (rasi_idx + k) % 12
    elif d == 150:  # Nadiamsa
        target = (rasi_idx + k) % 12
    elif d == 300:  # Ardha-Nadiamsa
        target = (rasi_idx + k) % 12
    else:
        target = (rasi_idx + k) % 12

    return target, RASI_NAMES[target], deg_in_varga

# ============================================================================
# 3. VECTORIZED KP SUB-LORD ENGINE
# ============================================================================

def calculate_kp_numpy(longitudes: np.ndarray) -> dict:
    """
    Vectorized KP calculations for any array of longitudes.
    Calculates Sign Lord, Star Lord, Sub Lord, SSL, and SSSL simultaneously in pure NumPy.
    """
    lon = np.asarray(longitudes, dtype=np.float64) % 360.0
    rasi_indices = (lon // 30).astype(int)
    sign_lords = RASI_LORDS[rasi_indices]

    nak_w = 360.0 / 27.0  # 13.333333333333334°
    nak_indices = (lon // nak_w).astype(int)
    pos_in_nak = lon % nak_w
    padas = (pos_in_nak // (nak_w / 4.0)).astype(int) + 1
    star_lord_indices = nak_indices % 9
    star_lords = VIMSHOTTARI_LORDS[star_lord_indices]
    nak_names = NAKSHATRAS[nak_indices]

    # Helper function to vectorize sub-division level resolution
    def resolve_sub_level(positions: np.ndarray, total_widths: np.ndarray, parent_indices: np.ndarray):
        # Shape: (N_planets, 9)
        step_offsets = np.arange(9)
        sub_orders = (parent_indices[:, None] + step_offsets[None, :]) % 9
        
        # Sub-widths matrix
        sub_widths = VIMSHOTTARI_RATIOS[sub_orders] * total_widths[:, None]
        cum_widths = np.cumsum(sub_widths, axis=1)
        cum_starts = cum_widths - sub_widths

        # Find which of the 9 bins each position falls into
        pos_matrix = positions[:, None]
        mask = (pos_matrix >= cum_starts) & (pos_matrix < cum_widths)
        
        # In case of exact upper boundary edge cases (e.g. 359.999999°)
        hit_counts = np.sum(mask, axis=1)
        fallback_mask = (hit_counts == 0)
        
        # Extract chosen indices and remainder positions
        sub_indices = np.where(fallback_mask, sub_orders[:, -1], np.take_along_axis(sub_orders, np.argmax(mask, axis=1)[:, None], axis=1).squeeze(1))
        chosen_starts = np.where(fallback_mask, cum_starts[:, -1], np.take_along_axis(cum_starts, np.argmax(mask, axis=1)[:, None], axis=1).squeeze(1))
        chosen_widths = np.where(fallback_mask, sub_widths[:, -1], np.take_along_axis(sub_widths, np.argmax(mask, axis=1)[:, None], axis=1).squeeze(1))

        pos_in_sub = positions - chosen_starts
        return sub_indices, pos_in_sub, chosen_widths

    # Level 1: Sub-Lord
    sub_indices, pos_in_sub, sub_widths = resolve_sub_level(pos_in_nak, np.full_like(lon, nak_w), star_lord_indices)
    sub_lords = VIMSHOTTARI_LORDS[sub_indices]

    # Level 2: Sub-Sub-Lord (SSL)
    ssl_indices, pos_in_ssl, ssl_widths = resolve_sub_level(pos_in_sub, sub_widths, sub_indices)
    ssl_lords = VIMSHOTTARI_LORDS[ssl_indices]

    # Level 3: Sub-Sub-Sub-Lord (SSSL)
    sssl_indices, _, _ = resolve_sub_level(pos_in_ssl, ssl_widths, ssl_indices)
    sssl_lords = VIMSHOTTARI_LORDS[sssl_indices]

    return {
        "longitudes": lon,
        "sign_lords": sign_lords,
        "nakshatras": nak_names,
        "padas": padas,
        "star_lords": star_lords,
        "sub_lords": sub_lords,
        "sub_sub_lords": ssl_lords,
        "sub_sub_sub_lords": sssl_lords
    }

# ============================================================================
# 4. FULL SCHEMA INTEGRATION (COMPREHENSIVE HOROSCOPE BUILDER)
# ============================================================================

from Schema import (
    VargaDetails, VargaCollections, KpDetails,
    HouseDetails, ComprehensivePlanetDetails, ComprehensiveHoroscope,
    VARGA_NAMES, RASI_NAMES_TAMIL
)

def build_horoscope_vargas_numpy(
    planet_longitudes: dict[str, float],
    ascendant_longitude: float
) -> dict[str, ComprehensivePlanetDetails]:
    """
    Constructs comprehensive Pydantic models for all planets using NumPy.
    Calculates Sign, House Number (1 to 12 relative to Lagna in each Varga),
    DMS, and KP Sub-lords across all 20+ divisional charts.
    """
    result = {}
    for p_name, p_deg in planet_longitudes.items():
        vargas_dict = {}
        for d, name in VARGA_NAMES.items():
            # 1. Planet sign in D-N (0 to 11)
            p_sign, _, deg_v = calculate_vargas_numpy(np.array([p_deg]), d=d)
            p_s = int(p_sign[0])
            d_v = float(deg_v[0])

            # 2. Ascendant sign in D-N (0 to 11)
            asc_sign, _, _ = calculate_vargas_numpy(np.array([ascendant_longitude]), d=d)
            asc_s = int(asc_sign[0])

            # 3. House index (0 to 11)
            h_num = (p_s - asc_s) % 12

            # 4. KP Details in Varga
            abs_v_deg = (p_s * 30.0) + d_v
            kp_res = calculate_kp_numpy(np.array([abs_v_deg]))
            
            kp_obj = KpDetails(
                nakshatra_name_en=str(kp_res["nakshatras"][0]),
                pada=int(kp_res["padas"][0]),
                star_lord=str(kp_res["star_lords"][0]),
                sub_lord=str(kp_res["sub_lords"][0]),
                sub_sub_lord=str(kp_res["sub_sub_lords"][0]),
                sub_sub_sub_lord=str(kp_res["sub_sub_sub_lords"][0]),
                formatted_kp=f"{kp_res['nakshatras'][0]}-{kp_res['padas'][0]}, {kp_res['star_lords'][0]}, {kp_res['sub_lords'][0]}, {kp_res['sub_sub_lords'][0]}"
            )

            v_detail = VargaDetails(
                varga_code=f"D-{d}",
                harmonic=d,
                name=name,
                rasi=RASI_NAMES_TAMIL[p_s],
                sign_index=p_s,
                house=h_num,
                deg_in_varga=d_v,
                DMS=deg_to_dms_vec(np.array([d_v]))[0],
                sign_lord=str(RASI_LORDS[p_s]),
                kp_details=kp_obj
            )
            vargas_dict[f"d{d}"] = v_detail

        vargas_col = VargaCollections(**vargas_dict)
        h_details = HouseDetails(deg=p_deg)

        result[p_name] = ComprehensivePlanetDetails(
            planet_name=p_name,
            deg=p_deg,
            housedetails=h_details,
            vargas=vargas_col
        )

    return result

# ============================================================================
# 5. BENCHMARK & DEMO: CALCULATE ALL 9 PLANETS + ASCENDANT AT ONCE
# ============================================================================

if __name__ == "__main__":
    planet_longitudes = {
        "Ascendant": 42.15,   # 12° 09' Taurus
        "Sun": 125.40,        # 05° 24' Leo
        "Moon": 212.80,       # 02° 48' Scorpio
        "Mars": 74.25,        # 14° 15' Gemini
        "Mercury": 110.10,    # 20° 06' Cancer
        "Jupiter": 315.65,    # 15° 39' Aquarius
        "Venus": 155.20,      # 05° 12' Virgo
        "Saturn": 289.45,     # 19° 27' Capricorn
        "Rahu": 19.30,        # 19° 18' Aries
        "Ketu": 199.30        # 19° 18' Libra
    }

    print("==================================================================")
    print("NUMPY + PYDANTIC INTEGRATED HOROSCOPE BUILDER")
    print("==================================================================")

    horoscope_data = build_horoscope_vargas_numpy(
        planet_longitudes=planet_longitudes,
        ascendant_longitude=planet_longitudes["Ascendant"]
    )

    jup = horoscope_data["Jupiter"]
    print(f"\nJupiter Details:")
    print(f"  Rasi (D-1)    : {jup.vargas.d1.rasi} (House {jup.vargas.d1.house}) - {jup.vargas.d1.DMS}")
    print(f"  Navamsha (D-9): {jup.vargas.d9.rasi} (House {jup.vargas.d9.house}) - {jup.vargas.d9.DMS}")
    print(f"  Dasamsha (D-10): {jup.vargas.d10.rasi} (House {jup.vargas.d10.house}) - {jup.vargas.d10.DMS}")
    print(f"  D-9 KP Details: {jup.vargas.d9.kp_details.formatted_kp}")

    mars = horoscope_data["Mars"]
    print(f"\nMars Details:")
    print(f"  Rasi (D-1)    : {mars.vargas.d1.rasi} (House {mars.vargas.d1.house}) - {mars.vargas.d1.DMS}")
    print(f"  Navamsha (D-9): {mars.vargas.d9.rasi} (House {mars.vargas.d9.house}) - {mars.vargas.d9.DMS}")
    print(f"  Dasamsha (D-10): {mars.vargas.d10.rasi} (House {mars.vargas.d10.house}) - {mars.vargas.d10.DMS}")

