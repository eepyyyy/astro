# Jamakkol Prasanam — Master Calculation & Troubleshooting Specification

This document is an exhaustive, production-grade technical specification for building a high-precision **Jamakkol Prasanam** (ஜாமக்கோள் பிரசன்னம்) calculation engine in Python using Swiss Ephemeris (`swisseph`).

It covers every individual calculation, mathematical formulas, 0-indexed vs. 1-indexed conversions, potential errors/bugs, and exact alignments with the reference web application [www.jamakkol.com](https://www.jamakkol.com/) and its API backend [api.vedicastrochart.com](https://api.vedicastrochart.com/).

---

## 📋 Table of Contents
1. [Core Setup & Astronomical Standards](#1-core-setup--astronomical-standards)
2. [Julian Day & Timezone Mechanics](#2-julian-day--timezone-mechanics)
3. [Vedic Sunrise & Sunset (Rise/Set Transits)](#3-vedic-sunrise--sunset-riseset-transits)
4. [Jamakkol Udhayam (Rising Sign)](#4-jamakkol-udhayam-rising-sign)
5. [Jamakkol Arudham (5-Minute Rule)](#5-jamakkol-arudham-5-minute-rule)
6. [Jamakkol Kavippu (Obstacle / Shadow Point)](#6-jamakkol-kavippu-obstacle--shadow-point)
7. [Nitya Grahas (9 Transit Planets)](#7-nitya-grahas-9-transit-planets)
8. [Maandi & Gulika (Upagrahas)](#8-maandi--gulika-upagrahas)
9. [Jamam Outer Planets (Jama Planets)](#9-jamam-outer-planets-jama-planets)
10. [Panchangam Calculations](#10-panchangam-calculations)
11. [Pydantic Schemas Architecture](#11-pydantic-schemas-architecture)
12. [Master Validation & Reference Benchmark](#12-master-validation--reference-benchmark)

---

## 1. Core Setup & Astronomical Standards

### 1.1 Ayanamsa Modes
Jamakkol Prasanam requires sidereal longitudes. The reference software supports both **Lahiri** and **True Chitra (True Citra)** ayanamsas:
* **Lahiri Ayanamsa**: `swe.SIDM_LAHIRI` (mode `1`)
* **True Chitra (True Citra)**: `swe.set_sid_mode(27, 0, 0)` (mode `27`, preferred by [www.jamakkol.com](https://www.jamakkol.com/))

```python
import swisseph as swe

# Basic Ephemeris setup (Moshier analytical fallback if files absent)
swe.set_ephe_path("")

# Set Sidereal Mode to True Chitra (27)
swe.set_sid_mode(27, 0, 0)
```

### 1.2 Potential Errors & Pitfalls
* 🔴 **Missing `set_sid_mode()` Call**: If `swe.set_sid_mode()` is not called before passing `swe.FLG_SIDEREAL` to `swe.calc_ut()`, Swiss Ephemeris defaults to Fagan/Bradley ayanamsa, causing a $\sim 24^\circ$ discrepancy across all planetary positions.
* 🔴 **Ayanamsa Mismatch**: Verification against [jamakkol.com](https://www.jamakkol.com/) requires matching `ayanamsa=27` in the API query string (`api.vedicastrochart.com/site/jamakkol/api/data/jamakkol?...&ayanamsa=27`).

---

## 2. Julian Day & Timezone Mechanics

### 2.1 Formula
All Swiss Ephemeris calculations require the Julian Day in Universal Time ($\text{JD}_{\text{UT}}$).

Given local datetime $T_{\text{local}} = (\text{year}, \text{month}, \text{day}, \text{hour}, \text{minute}, \text{second})$ and timezone offset $\Delta T_{\text{tz}}$ in hours (e.g. $+5.5$ for IST):

$$T_{\text{utc}} = T_{\text{local}} - \Delta T_{\text{tz}}$$

$$\text{hour}_{\text{dec}} = \text{hour}_{\text{utc}} + \frac{\text{minute}_{\text{utc}}}{60} + \frac{\text{second}_{\text{utc}}}{3600}$$

$$\text{JD}_{\text{UT}} = \text{swe.julday}(\text{year}_{\text{utc}}, \text{month}_{\text{utc}}, \text{day}_{\text{utc}}, \text{hour}_{\text{dec}}, \text{swe.GREG\_CAL})$$

### 2.2 Potential Errors & Pitfalls
* 🔴 **Passing Local Time to `julday()`**: Passing $T_{\text{local}}$ instead of $T_{\text{utc}}$ leads to a 5.5-hour time shift in sunrise, planetary positions, and Udhayam.
* 🔴 **ISO String Server Offset Bug**: Some API backends (e.g., `api.vedicastrochart.com`) serialize UTC dates with a server-local offset (e.g. `13:11:08.864+00:00` instead of `00:41:08.864Z`). Always rely on explicit decimal `julianDay` fields in responses rather than parsing raw ISO string headers.

---

## 3. Vedic Sunrise & Sunset (Rise/Set Transits)

### 3.1 Astronomical Flags
Standard astronomical sunrise uses upper-limb apparent horizon crossing with atmospheric refraction. **Vedic Jamakkol** uses upper limb or True Geometric Disc Center without refraction:

```python
# Vedic Sunrise / Sunset Flags (Disc center, geometric, no refraction)
VEDIC_RISE_FLAGS = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION # 768
```

### 3.2 Dynamic Day/Night Span Determination
To determine whether the query moment $\text{JD}_{\text{query}}$ falls in Daytime or Nighttime:

1. Calculate Midnight $\text{JD}_{\text{mid}} = \lfloor \text{JD}_{\text{query}} \rfloor - 0.5$.
2. Compute today's rise ($\text{SR}$) and set ($\text{SS}$):
   $$\text{SR}, \text{SS} = \text{swe.rise\_trans}(\text{JD}_{\text{mid}}, \text{swe.SUN}, \text{swe.CALC\_RISE | VEDIC\_FLAGS}, [\text{lon}, \text{lat}, \text{alt}])$$
3. Compute yesterday's set ($\text{PSS}$) and tomorrow's rise ($\text{NSR}$).
4. Select active span:
   $$\text{Span} = \begin{cases} 
   [\text{SR}, \text{SS}] & \text{if } \text{SR} \le \text{JD}_{\text{query}} < \text{SS} \quad (\text{Day Span}) \\
   [\text{PSS}, \text{SR}] & \text{if } \text{JD}_{\text{query}} < \text{SR} \quad (\text{Pre-sunrise Night Span}) \\
   [\text{SS}, \text{NSR}] & \text{if } \text{JD}_{\text{query}} \ge \text{SS} \quad (\text{Post-sunset Night Span})
   \end{cases}$$

### 3.3 Potential Errors & Pitfalls
* 🔴 **Night Span Bug (Yesterday's Rise vs. Yesterday's Sunset)**: A critical bug occurs if `span_start` for a pre-sunrise query is set to yesterday's *sunrise* ($\text{PSR}$) instead of yesterday's *sunset* ($\text{PSS}$). This doubles the span length ($\sim 24$ hours instead of $\sim 12$ hours), causing the fraction to be halved and moving Udhayam into the wrong sign (e.g., Sagittarius instead of Scorpio).
* 🔴 **Elevation (Altitude) Misconfiguration**: Omitting elevation (`alt=0` vs `alt=820m`) changes sunrise by $\sim 15-30$ seconds. While small, this slightly alters the fraction calculation.

---

## 4. Jamakkol Udhayam (Rising Sign)

### 4.1 Concept & Formula
Unlike the birth chart Ascendant (which completes $360^\circ$ in 24 hours), **Udhayam** completes a full $360^\circ$ cycle during daylight hours ($\text{SR} \to \text{SS}$) and another full $360^\circ$ cycle during night hours ($\text{SS} \to \text{NSR}$).

At sunrise, Udhayam starts at the **exact sidereal longitude of the Sun at Sunrise** ($\text{Sun}_{\text{lon,sr}}$):

$$\text{fraction} = \frac{\text{JD}_{\text{query}} - \text{span\_start}}{\text{span\_end} - \text{span\_start}}$$

$$\text{Udhayam Longitude} = (\text{Sun}_{\text{lon,sr}} + \text{fraction} \times 360.0) \pmod{360}$$

```python
# Sun longitude at Sunrise (True Chitra)
res_sr, _, _ = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
sun_lon_sr = res_sr[0]

fraction = (jd_query - span_start) / (span_end - span_start)
udhayam_deg = (sun_lon_sr + fraction * 360.0) % 360.0
```

### 4.2 Potential Errors & Pitfalls
* 🔴 **Rasi Boundary Starting Point Misconception**: Some documentation suggests starting Udhayam at $\lfloor \text{Sun}_{\text{lon,sr}} / 30 \rfloor \times 30^\circ$ ($0^\circ$ of the Sun's sign). However, **jamakkol.com** starts Udhayam from $\text{Sun}_{\text{lon,sr}}$ (the exact degree of the Sun at sunrise).
* 🔴 **Using Standard Astronomical Ascendant (`swe.houses`)**: Standard Lagna moves by Earth's rotation ($\sim 2$ hours per sign). Using standard Lagna for Udhayam will cause complete prediction failure.

---

## 5. Jamakkol Arudham (5-Minute Rule)

### 5.1 Concept & Formula
Arudham is the query answer point. In modern Jamakkol software (including [jamakkol.com](https://www.jamakkol.com/)), Arudham is based on clock time: each Rasi ($30^\circ$) gets **5 minutes** (300 seconds).

$$\text{total\_sec} = \text{minute} \times 60 + \text{second}$$

$$\text{arudham\_rasi} = \lfloor \text{total\_sec} / 300 \rfloor$$

$$\text{deg\_in\_rasi} = (\text{total\_sec} \bmod 300) \times \left(\frac{30.0}{300.0}\right)$$

$$\text{Arudham Longitude} = (\text{arudham\_rasi} \times 30.0 + \text{deg\_in\_rasi}) \pmod{360}$$

### 5.2 Potential Errors & Pitfalls
* 🔴 **Ignoring Seconds**: Calculating `arudham_rasi = minute // 5` without seconds causes Arudham to jump discretely every 5 minutes instead of sweeping smoothly at $0.1^\circ$ per second.
* 🔴 **1-Based Rasi Offsets**: In Python 0-indexed arrays, Mesham (Aries) = `0`. If `arudham_rasi` is treated as 1-indexed without adjusting by `-1`, Arudham will be off by 1 whole sign ($30^\circ$).

---

## 6. Jamakkol Kavippu (Obstacle / Shadow Point)

### 6.1 Concept & Formula
Kavippu ("closure") is a shadow point that moves **retrograde** (counter-clockwise) relative to Arudham.

#### Step 1: Find Soorya Veedi Rasi Index
Based on the physical Sun's Rasi index ($\text{sun\_rasi} = \lfloor \text{Sun}_{\text{lon}} / 30 \rfloor$):

$$\text{veedi\_rasi} = \begin{cases} 
0 \quad (\text{Mesha Veedi}) & \text{if } \text{sun\_rasi} \in [1, 2, 3, 4] \quad (\text{Taurus, Gemini, Cancer, Leo}) \\
1 \quad (\text{Vrishabha Veedi}) & \text{if } \text{sun\_rasi} \in [0, 5, 6, 11] \quad (\text{Aries, Virgo, Libra, Pisces}) \\
2 \quad (\text{Mithuna Veedi}) & \text{if } \text{sun\_rasi} \in [7, 8, 9, 10] \quad (\text{Scorpio, Sagit, Capr, Aquar})
\end{cases}$$

#### Step 2: Kavippu Rasi Index
$$\text{kavippu\_rasi} = (\text{udhayam\_rasi} + \text{veedi\_rasi} - \text{arudham\_rasi}) \pmod{12}$$

#### Step 3: Retrograde Degree Calculation
$$\text{arudham\_deg\_relative} = \text{Arudham Longitude} \bmod 30.0$$

$$\text{kavippu\_deg\_in\_rasi} = 30.0 - \text{arudham\_deg\_relative} - \frac{1.0}{3600.0}$$

$$\text{Kavippu Longitude} = \text{kavippu\_rasi} \times 30.0 + \text{kavippu\_deg\_in\_rasi}$$

### 6.2 Potential Errors & Pitfalls
* 🔴 **Passing Absolute Degree instead of Relative Degree**: Passing absolute Arudham longitude ($89.9^\circ$) into `arudham_deg_in_rasi` causes `30.0 - 89.9 = -59.9°`. This shifts Kavippu by **2 whole signs** (e.g. putting it in Cancer instead of Virgo). Always enforce `arudham_deg % 30.0`.

---

## 7. Nitya Grahas (9 Transit Planets)

### 7.1 Calculation
Physical transit planets are computed using `swe.calc_ut`:

```python
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

PLANETS_ID = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.TRUE_NODE
}
```

* **Retrograde Status**: A planet is retrograde if daily speed is negative (`res[3] < 0`).
* **Ketu Calculation**: Ketu is $180^\circ$ opposite Rahu:
  $$\text{Ketu Longitude} = (\text{Rahu Longitude} + 180.0) \pmod{360}$$
  Ketu is always retrograde.

---

## 8. Maandi & Gulika (Upagrahas)

### 8.1 Method 5 (Sun Degree-Based Method used by API)
The API `api.vedicastrochart.com` with `maandiCalculationMethod=5` computes Maandi directly by shifting the physical Sun's degree by Saturn's weekday Kala offset:

$$\text{MANDI\_DAY\_KALA} = [5, 4, 7, 3, 2, 1, 6] \quad (\text{Sun}=0 \dots \text{Sat}=6)$$

$$\text{MANDI\_NIGHT\_KALA} = [0, 1, 4, 2, 3, 6, 7]$$

$$\text{Maandi Longitude} = (\text{Sun Longitude} + \text{Saturn Kala Index} \times 30.0) \pmod{360}$$

### 8.2 Traditional Kala Ascendant Method
1. Divide Day/Night into 8 equal parts ($\text{Kala}_{\text{dur}} = (\text{SS} - \text{SR}) / 8$).
2. Identify Saturn's Kala start/end JD.
3. Compute the sidereal Ascendant (`swe.houses`) at that precise JD.

---

## 9. Jamam Outer Planets (Jama Planets)

### 9.1 Concept & 8-Rasi Wheel Mechanics
The 8 Jamam outer planets (`Jama Sun`, `Jama Mars`, `Jama Jupiter`, `Jama Mercury`, `Jama Venus`, `Jama Saturn`, `Jama Moon`, `Jama Snake`) represent symbolic time divisions placed on an outer wheel.

* **Wheel Signs**: The 4 common/dual signs (Gemini `2`, Virgo `5`, Sagittarius `8`, Pisces `11`) are **skipped**. The outer wheel consists of the 8 non-dual signs:
  $$\text{OUTER\_WHEEL} = [0, 1, 3, 4, 6, 7, 9, 10] \quad (\text{Aries, Taurus, Cancer, Leo, Libra, Scorpio, Capricorn, Aquarius})$$
* **Octagonal Spacing**: The 8 planets are spaced exactly **$45^\circ$ apart**.
* **Constant Speed**: The wheel rotates **counter-clockwise** at a constant speed of **$30^\circ$ per hour** ($0.5^\circ/\text{min}$, $30''/\text{sec}$) starting from 06:00 AM local time.

### 9.2 Exact Degree & Placement Formula
Given local time $t$ in decimal hours (e.g. $10:14:59 = 10.249722$):

$$\text{rotation} = (t - 6.0) \times 30.0^\circ$$

$$\text{Jama Planet Longitude} = (\text{Start\_Deg} - \text{rotation}) \pmod{360}$$

#### Starting Degrees at 06:00 AM for Thursday:
| Planet | 06:00 AM Base Deg | Sign at 06:00 AM | Formatted Degree at 10:14:59 | Sign at 10:14:59 |
| :--- | :--- | :--- | :--- | :--- |
| **Jama Sun** | $90.0^\circ$ | Cancer ($0^\circ$) | $322.50833^\circ$ | **Aquarius** ($22^\circ 30' 30''$) |
| **Jama Mars** | $45.0^\circ$ | Taurus ($15^\circ$) | $277.50833^\circ$ | **Capricorn** ($7^\circ 30' 30''$) |
| **Jama Jupiter** | $0.0^\circ$ | Aries ($0^\circ$) | $232.50833^\circ$ | **Scorpio** ($22^\circ 30' 30''$) |
| **Jama Mercury** | $315.0^\circ$ | Aquarius ($15^\circ$) | $187.50833^\circ$ | **Libra** ($7^\circ 30' 30''$) |
| **Jama Venus** | $270.0^\circ$ | Capricorn ($0^\circ$) | $142.50833^\circ$ | **Leo** ($22^\circ 30' 30''$) |
| **Jama Saturn** | $225.0^\circ$ | Scorpio ($15^\circ$) | $97.50833^\circ$ | **Cancer** ($7^\circ 30' 30''$) |
| **Jama Moon** | $180.0^\circ$ | Libra ($0^\circ$) | $52.50833^\circ$ | **Taurus** ($22^\circ 30' 30''$) |
| **Jama Snake** | $135.0^\circ$ | Leo ($15^\circ$) | $7.50833^\circ$ | **Aries** ($7^\circ 30' 30''$) |

---

## 10. Panchangam Calculations

1. **Thithi**: Based on Moon-Sun longitude difference:
   $$\Delta = (\text{Moon}_{\text{lon}} - \text{Sun}_{\text{lon}}) \pmod{360}$$
   $$\text{Thithi Index} = \lfloor \Delta / 12.0 \rfloor + 1 \quad (1 \dots 30)$$
2. **Yoga**: Sum of Sun and Moon longitudes:
   $$\text{Yoga Index} = \lfloor (\text{Sun}_{\text{lon}} + \text{Moon}_{\text{lon}}) \bmod 360 / (360 / 27) \rfloor$$
3. **Nakshatra**:
   $$\text{Nakshatra Index} = \lfloor \text{Moon}_{\text{lon}} / (360 / 27) \rfloor$$

---

## 11. Pydantic Schemas Architecture

Use flat, self-validating Pydantic schemas to keep the API engine code pure:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator

RASI_NAMES = [
    "Mesham", "Rishabham", "Mithunam", "Kadagam",
    "Simmam", "Kanni", "Thulaam", "Viruchigam",
    "Dhanusu", "Magaram", "Kumbam", "Meenam"
]

class AstronomyBaseModel(BaseModel):
    deg: float
    rasi_index: Optional[int] = None
    rasi_name: Optional[str] = None
    deg_in_rasi: Optional[float] = None
    formatted_dms: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def auto_calculate_dms(cls, data: dict) -> dict:
        if isinstance(data, dict) and data.get('deg') is not None:
            deg = data['deg'] % 360.0
            r_idx = int(deg // 30)
            d_in_r = deg % 30.0
            
            data['rasi_index'] = r_idx
            data['rasi_name'] = RASI_NAMES[r_idx]
            data['deg_in_rasi'] = round(d_in_r, 4)
            
            d_int = int(d_in_r)
            m_dec = (d_in_r - d_int) * 60
            m_int = int(m_dec)
            s = (m_dec - m_int) * 60
            data['formatted_dms'] = f"{RASI_NAMES[r_idx]} ({r_idx + 1}) -- {d_int}° {m_int}' {s:.4f}\""
        return data

class PlanetDetails(AstronomyBaseModel):
    name: str
    speed: float
    is_retrograde: Optional[bool] = None

    @model_validator(mode='before')
    @classmethod
    def set_retrograde(cls, data: dict) -> dict:
        data = super().auto_calculate_dms(data)
        if isinstance(data, dict) and data.get('speed') is not None:
            data['is_retrograde'] = data['speed'] < 0
        return data

class UdhayamOutput(AstronomyBaseModel):
    sunrise: datetime
    sunset: datetime
    fraction: float
    method: str
```

---

## 12. Master Validation & Reference Benchmark

### Benchmark Input:
* **Date**: August 13, 2026 at `10:14:59` IST
* **Coordinates**: `lat=12.9811704`, `lon=77.48509299999999`
* **Ayanamsa**: True Chitra (`27`)

### Expected Benchmark Results:
| Item | Expected Degree | Expected Rasi | Formatted DMS |
| :--- | :--- | :--- | :--- |
| **Sun** | $116.26554^\circ$ | Cancer (4) | $26^\circ 15' 55.9550''$ |
| **Moon** | $122.48670^\circ$ | Leo (5) | $2^\circ 29' 12.1286''$ |
| **Arudham** | $89.90000^\circ$ | Gemini (3) | $29^\circ 54' 00.0000''$ |
| **Kavippu** | $150.10000^\circ$ | Virgo (6) | $0^\circ 05' 59.9999''$ (R) |
| **Udhayam** | $233.53741^\circ$ | Scorpio (8) | $23^\circ 32' 14.6819''$ |
| **Maandi** | $176.26554^\circ$ | Virgo (6) | $26^\circ 15' 55.9577''$ |
| **Jama Sun** | $322.50833^\circ$ | Aquarius (11) | $22^\circ 30' 30.0000''$ |
| **Jama Mars** | $277.50833^\circ$ | Capricorn (10) | $7^\circ 30' 30.0000''$ |
| **Jama Jupiter** | $232.50833^\circ$ | Scorpio (8) | $22^\circ 30' 30.0000''$ |
| **Jama Mercury**| $187.50833^\circ$ | Libra (7) | $7^\circ 30' 30.0000''$ |
| **Jama Venus** | $142.50833^\circ$ | Leo (5) | $22^\circ 30' 30.0000''$ |
| **Jama Saturn** | $97.50833^\circ$ | Cancer (4) | $7^\circ 30' 30.0000''$ |
| **Jama Moon** | $52.50833^\circ$ | Taurus (2) | $22^\circ 30' 30.0000''$ |
| **Jama Snake** | $7.50833^\circ$ | Aries (1) | $7^\circ 30' 30.0000''$ |
