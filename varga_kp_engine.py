"""
Vedic Divisional Charts (Vargas D-1 to D-150+) & KP Sub-Lord Calculation Engine
================================================================================
"""

from typing import Dict, List, Tuple

RASI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

RASI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

NAKSHATRAS = [
    "Aswini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyestha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7.0, 20.0, 6.0, 10.0, 7.0, 18.0, 16.0, 19.0, 17.0]

def deg_to_dms(deg: float) -> str:
    deg = deg % 360.0
    d = int(deg)
    m_dec = (deg - d) * 60.0
    m = int(m_dec)
    s = (m_dec - m) * 60.0
    return f"{d:02d}° {m:02d}' {s:04.1f}\""

def calculate_varga(lon: float, d: int) -> Tuple[str, float]:
    """Calculates the target sign name and degree inside that sign for any D-N chart."""
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

    if d == 1:
        target = s_idx
    elif d == 2:
        target = (4 if k == 0 else 3) if is_odd else (3 if k == 0 else 4)
    elif d == 3:
        target = (s_idx + 4 * k) % 12
    elif d == 4:
        target = (s_idx + 3 * k) % 12
    elif d == 5:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 6:
        target = ((0 if is_odd else 6) + k) % 12
    elif d == 7:
        target = ((s_idx if is_odd else (s_idx + 6)) + k) % 12
    elif d == 8:
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        target = (start + k) % 12
    elif d == 9:
        target = int(lon // (30.0 / 9.0)) % 12
    elif d == 10:
        target = ((s_idx if is_odd else (s_idx + 8)) + k) % 12
    elif d == 11:
        target = (12 - (s_idx + k) % 12) % 12
    elif d == 12:
        target = (s_idx + k) % 12
    elif d == 16:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 20:
        start = 0 if modality == 0 else (8 if modality == 1 else 4)
        target = (start + k) % 12
    elif d == 24:
        target = ((4 if is_odd else 3) + k) % 12
    elif d == 27:
        start = 0 if element == 0 else (3 if element == 1 else (6 if element == 2 else 9))
        target = (start + k) % 12
    elif d == 30:
        if is_odd:
            target = 0 if deg_in_sign < 5 else (10 if deg_in_sign < 10 else (8 if deg_in_sign < 18 else (2 if deg_in_sign < 25 else 6)))
        else:
            target = 1 if deg_in_sign < 5 else (5 if deg_in_sign < 12 else (11 if deg_in_sign < 20 else (9 if deg_in_sign < 25 else 7)))
    elif d == 40:
        target = ((0 if is_odd else 6) + k) % 12
    elif d == 45:
        start = 0 if modality == 0 else (4 if modality == 1 else 8)
        target = (start + k) % 12
    elif d == 60:
        target = (s_idx + k) % 12
    elif d == 108:
        target = int(lon // (30.0 / 108.0)) % 12
    else:
        target = (s_idx + k) % 12

    return RASI_NAMES[target], deg_varga

def calculate_kp(deg: float) -> Dict[str, str]:
    """Calculates Sign Lord, Star Lord, Sub Lord, SSL, and SSSL for any degree."""
    deg = deg % 360.0
    rasi_idx = int(deg // 30.0)
    nak_w = 360.0 / 27.0
    ni = int(deg // nak_w)
    pos_nak = deg % nak_w
    pada = int(pos_nak // (nak_w / 4.0)) + 1
    star_idx = ni % 9

    def get_sub_level(pos, total_w, parent_idx):
        order = [(parent_idx + i) % 9 for i in range(9)]
        widths = [(VIMSHOTTARI_YEARS[i] / 120.0) * total_w for i in order]
        cum = 0.0
        for idx, w in zip(order, widths):
            if cum <= pos < cum + w:
                return idx, pos - cum, w
            cum += w
        return order[-1], pos - (total_w - widths[-1]), widths[-1]

    sub_idx, pos_sub, sub_w = get_sub_level(pos_nak, nak_w, star_idx)
    ssl_idx, pos_ssl, ssl_w = get_sub_level(pos_sub, sub_w, sub_idx)
    sssl_idx, _, _ = get_sub_level(pos_ssl, ssl_w, ssl_idx)

    return {
        "Sign_Lord": RASI_LORDS[rasi_idx],
        "Nakshatra": NAKSHATRAS[ni],
        "Pada": str(pada),
        "Star_Lord": VIMSHOTTARI_LORDS[star_idx],
        "Sub_Lord": VIMSHOTTARI_LORDS[sub_idx],
        "Sub_Sub_Lord": VIMSHOTTARI_LORDS[ssl_idx],
        "Sub_Sub_Sub_Lord": VIMSHOTTARI_LORDS[sssl_idx]
    }

if __name__ == "__main__":
    test_deg = 74.25  # 14°15' Gemini
    print(f"Test Longitude: {test_deg}° ({deg_to_dms(test_deg)})")
    sign, d_v = calculate_varga(test_deg, 9)
    print(f"Navamsha (D-9): {sign} at {deg_to_dms(d_v)}")
    kp = calculate_kp(test_deg)
    print("KP Analysis:", kp)
