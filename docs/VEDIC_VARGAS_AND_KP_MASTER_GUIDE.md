# Master Guide: Vedic Divisional Charts ($D\text{-}1$ to $D\text{-}150+$) & KP Astrology Calculations

A complete, self-contained educational manual and mathematical specification for learning, calculating, and coding all **Vedic Divisional Charts (Vargas)** and **Krishnamurti Paddhati (KP) Cuspal / Sub-Lord Systems** from the ground up.

---

# Table of Contents
1. [Foundational Mathematics of the Astrological Circle](#1-foundational-mathematics-of-the-astrological-circle)
   - [The 360° Coordinate Space](#11-the-360-coordinate-space)
   - [Modulo Arithmetic & Angle Normalization](#12-modulo-arithmetic--angle-normalization)
   - [Degrees, Minutes, Seconds (DMS) Decomposition](#13-degrees-minutes-seconds-dms-decomposition)
   - [Zodiac Classifications (Modality, Elements, Parity)](#14-zodiac-classifications-modality-elements-parity)
2. [Universal Formula for Divisional Charts (Vargas)](#2-universal-formula-for-divisional-charts-vargas)
3. [Step-by-Step Varga Calculations ($D\text{-}2$ to $D\text{-}60$)](#3-step-by-step-varga-calculations-d-2-to-d-60)
   - [$D\text{-}2$ Hora](#d-2-hora-wealth--resources)
   - [$D\text{-}3$ Drekkana](#d-3-drekkana-siblings--courage)
   - [$D\text{-}4$ Chaturthamsa](#d-4-chaturthamsa-property--assets)
   - [$D\text{-}5$ Panchamsha](#d-5-panchamsha-spiritual-power--fame)
   - [$D\text{-}6$ Shasthamsa](#d-6-shasthamsa-health-conflicts--litigation)
   - [$D\text{-}7$ Saptamsha](#d-7-saptamsha-children--progeny)
   - [$D\text{-}8$ Ashtamsha](#d-8-ashtamsha-longevity--hidden-hazards)
   - [$D\text{-}9$ Navamsha](#d-9-navamsha-dharma-marriage--soul-essence)
   - [$D\text{-}10$ Dasamsha](#d-10-dasamsha-career-fame--social-status)
   - [$D\text{-}11$ Rudramsha](#d-11-rudramsha-challenges--destructive-forces)
   - [$D\text{-}12$ Dwadasamsha](#d-12-dwadasamsha-parents--ancestral-heritage)
   - [$D\text{-}16$ Shodashamsha](#d-16-shodashamsha-vehicles--luxuries)
   - [$D\text{-}20$ Vimsamsha](#d-20-vimsamsha-spiritual-progress--upasana)
   - [$D\text{-}24$ Siddhamsa / Chaturvimsamsha](#d-24-siddhamsa--chaturvimsamsha-education--learning)
   - [$D\text{-}27$ Saptavimsamsha / Bhamsa](#d-27-saptavimsamsha--bhamsa-strengths--weaknesses)
   - [$D\text{-}30$ Trimsamsha (Unequal Division)](#d-30-trimsamsha-misfortunes--arishta)
   - [$D\text{-}40$ Khavedamsha](#d-40-khavedamsha-auspicious-timing)
   - [$D\text{-}45$ Akshavedamsha](#d-45-akshavedamsha-moral-integrity--all-aspects)
   - [$D\text{-}60$ Shashtiamsha](#d-60-shashtiamsha-past-life-karmic-roots)
4. [Higher Divisional Harmonics ($D\text{-}72$ to $D\text{-}300$)](#4-higher-divisional-harmonics-d-72-to-d-300)
   - [$D\text{-}72$ Ashtamamsha](#d-72-ashtamamsha)
   - [$D\text{-}81$ Nava-Navamsha](#d-81-nava-navamsha)
   - [$D\text{-}108$ Ashtottaramsa](#d-108-ashtottaramsa)
   - [$D\text{-}144$ Dwadasamsha-Dwadasamsha](#d-144-dwadasamsha-dwadasamsha)
   - [$D\text{-}150$ Nadiamsa (Chandra Kala Nadi)](#d-150-nadiamsa-chandra-kala-nadi)
   - [$D\text{-}300$ Ardha-Nadiamsa](#d-300-ardha-nadiamsa)
5. [Vimsopaka Bala Scoring System](#5-vimsopaka-bala-scoring-system)
6. [Krishnamurti Paddhati (KP) System Calculations](#6-krishnamurti-paddhati-kp-system-calculations)
   - [KP Ayanamsha Precision Formula](#61-kp-ayanamsha-precision-formula)
   - [Placidus House Cusps & Intercepts](#62-placidus-house-cusps--intercepts)
   - [The 4-Tier Sub-Lord Hierarchy](#63-the-4-tier-sub-lord-hierarchy)
   - [Derivation of the 249 KP Sub-Divisions](#64-derivation-of-the-249-kp-sub-divisions)
   - [Sub-Sub-Lord (SSL) & Sub-Sub-Sub-Lord (SSSL)](#65-sub-sub-lord-ssl--sub-sub-sub-lord-sssl)
   - [4-Fold Significators (Levels 1 to 4)](#66-4-fold-significators-levels-1-to-4)
   - [Cuspal Sub-Lord Rules for Event Verification](#67-cuspal-sub-lord-rules-for-event-verification)
   - [Ruling Planets (RP) & Timing of Events](#68-ruling-planets-rp--timing-of-events)
   - [KP Fortuna (Part of Fortune)](#69-kp-fortuna-part-of-fortune)
7. [Complete Production Python Reference Engine](#7-complete-production-python-reference-engine)

---

# 1. Foundational Mathematics of the Astrological Circle

### 1.1 The 360° Coordinate Space
* Total Circle $= 360^\circ = 21,600' = 1,296,000''$.
* 12 Signs (Rasis) $= 30^\circ$ each ($1,800'$ or $108,000''$).
* 27 Nakshatras $= 13^\circ 20'$ each ($800'$ or $48,000''$).
* 108 Nakshatra Padas $= 3^\circ 20'$ each ($200'$ or $12,000''$).

```
Zodiac Index Mapping (0-indexed):
0 = Aries (Mesha)          6 = Libra (Thula)
1 = Taurus (Rishabha)      7 = Scorpio (Vrischika)
2 = Gemini (Mithuna)       8 = Sagittarius (Dhanus)
3 = Cancer (Kataka)        9 = Capricorn (Makara)
4 = Leo (Simha)           10 = Aquarius (Kumbha)
5 = Virgo (Kanya)         11 = Pisces (Meena)
```

### 1.2 Modulo Arithmetic & Angle Normalization
Any astronomical longitude $\lambda$ must be normalized to $[0^\circ, 360^\circ)$:
$$\lambda_{\text{norm}} = \lambda \pmod{360^\circ}$$
In Python:
```python
lambda_norm = raw_deg % 360.0
```

To extract the Sign Index ($S \in \{0, \dots, 11\}$) and Relative Longitude in Sign ($\lambda_{\text{rel}} \in [0^\circ, 30^\circ)$):
$$S = \lfloor \lambda_{\text{norm}} / 30^\circ \rfloor$$
$$\lambda_{\text{rel}} = \lambda_{\text{norm}} \pmod{30^\circ}$$

### 1.3 Degrees, Minutes, Seconds (DMS) Decomposition
Given a decimal degree $\theta$:
1. Degrees: $D = \lfloor \theta \rfloor$
2. Total Minutes: $M_{\text{total}} = (\theta - D) \times 60$
3. Minutes: $M = \lfloor M_{\text{total}} \rfloor$
4. Seconds: $S_{\text{sec}} = (M_{\text{total}} - M) \times 60$

In Python:
```python
def to_dms(deg: float) -> str:
    d = int(deg)
    m_dec = (deg - d) * 60.0
    m = int(m_dec)
    s = (m_dec - m) * 60.0
    return f"{d:02d}° {m:02d}' {s:04.1f}\""
```

### 1.4 Zodiac Classifications (Modality, Elements, Parity)
1. **Parity:**
   * **Odd Signs ($S \bmod 2 == 0$):** Aries, Gemini, Leo, Libra, Sagittarius, Aquarius.
   * **Even Signs ($S \bmod 2 == 1$):** Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces.
2. **Modality (Triplicity):**
   * **Movable / Chara ($S \bmod 3 == 0$):** Aries, Cancer, Libra, Capricorn.
   * **Fixed / Sthira ($S \bmod 3 == 1$):** Taurus, Leo, Scorpio, Aquarius.
   * **Dual / Dvisvabhava ($S \bmod 3 == 2$):** Gemini, Virgo, Sagittarius, Pisces.
3. **Element (Quadruplicity):**
   * **Fire / Agni ($S \bmod 4 == 0$):** Aries, Leo, Sagittarius.
   * **Earth / Prithvi ($S \bmod 4 == 1$):** Taurus, Virgo, Capricorn.
   * **Air / Vayu ($S \bmod 4 == 2$):** Gemini, Libra, Aquarius.
   * **Water / Jala ($S \bmod 4 == 3$):** Cancer, Scorpio, Pisces.

---

# 2. Universal Formula for Divisional Charts (Vargas)

For any harmonic division $N$:
1. **Division Width:**
   $$\Delta_N = \frac{30^\circ}{N}$$
2. **Division Index ($k \in \{0, 1, \dots, N-1\}$):**
   $$k = \left\lfloor \frac{\lambda_{\text{rel}}}{\Delta_N} \right\rfloor = \left\lfloor \frac{\lambda \pmod{30^\circ}}{30^\circ / N} \right\rfloor$$
3. **Remainder inside Division ($\delta_N$):**
   $$\delta_N = \lambda_{\text{rel}} - (k \cdot \Delta_N)$$
4. **Calculated Longitude within Varga Sign:**
   $$\lambda_{D\text{-}N} = (\delta_N \times N) \pmod{30^\circ}$$
5. **Target Sign in $D\text{-}N$ Chart:**
   $$S_{D\text{-}N} = (\text{StartSign}(S, N) + k) \pmod{12}$$

---

# 3. Step-by-Step Varga Calculations ($D\text{-}2$ to $D\text{-}60$)

---

### $D\text{-}2$: Hora (Wealth & Resources)
* **Divisor:** $N = 2$ | **Span:** $\Delta_2 = 15^\circ 00' 00''$ ($k \in \{0, 1\}$).
* **Parashari Rule:**
  * **Odd Signs:**
    * $k = 0$ ($0^\circ \text{--} 15^\circ$): **Leo (Sun)** $\implies S_{D2} = 4$
    * $k = 1$ ($15^\circ \text{--} 30^\circ$): **Cancer (Moon)** $\implies S_{D2} = 3$
  * **Even Signs:**
    * $k = 0$ ($0^\circ \text{--} 15^\circ$): **Cancer (Moon)** $\implies S_{D2} = 3$
    * $k = 1$ ($15^\circ \text{--} 30^\circ$): **Leo (Sun)** $\implies S_{D2} = 4$
* **Paravritti Hora (Alternate 12-sign mapping):**
  $$S_{D2} = (S + k \cdot 6) \pmod{12}$$

---

### $D\text{-}3$: Drekkana (Siblings & Courage)
* **Divisor:** $N = 3$ | **Span:** $\Delta_3 = 10^\circ 00' 00''$ ($k \in \{0, 1, 2\}$).
* **Parashari Rule (Trines / $1\text{st}, 5\text{th}, 9\text{th}$):**
  $$S_{D3} = (S + 4 \cdot k) \pmod{12}$$
  * $k = 0$ ($0^\circ \text{--} 10^\circ$): Same sign ($S$)
  * $k = 1$ ($10^\circ \text{--} 20^\circ$): 5th sign from $S$ ($(S+4)\bmod 12$)
  * $k = 2$ ($20^\circ \text{--} 30^\circ$): 9th sign from $S$ ($(S+8)\bmod 12$)

---

### $D\text{-}4$: Chaturthamsa (Property & Assets)
* **Divisor:** $N = 4$ | **Span:** $\Delta_4 = 7^\circ 30' 00'' = 450'$ ($k \in \{0, 1, 2, 3\}$).
* **Rule (Kendras / $1\text{st}, 4\text{th}, 7\text{th}, 10\text{th}$):**
  $$S_{D4} = (S + 3 \cdot k) \pmod{12}$$

---

### $D\text{-}5$: Panchamsha (Spiritual Power & Fame)
* **Divisor:** $N = 5$ | **Span:** $\Delta_5 = 6^\circ 00' 00''$ ($k \in \{0, 1, 2, 3, 4\}$).
* **Rule (by Sign Modality):**
  * **Movable Signs:** Start from Aries ($0$): $S_{D5} = (0 + k) \bmod 12$
  * **Fixed Signs:** Start from Leo ($4$): $S_{D5} = (4 + k) \bmod 12$
  * **Dual Signs:** Start from Sagittarius ($8$): $S_{D5} = (8 + k) \bmod 12$

---

### $D\text{-}6$: Shasthamsa (Health Conflicts & Litigation)
* **Divisor:** $N = 6$ | **Span:** $\Delta_6 = 5^\circ 00' 00''$ ($k \in \{0, 1, \dots, 5\}$).
* **Rule:**
  * **Odd Signs:** Start from Aries ($0$): $S_{D6} = (0 + k) \bmod 12$
  * **Even Signs:** Start from Libra ($6$): $S_{D6} = (6 + k) \bmod 12$

---

### $D\text{-}7$: Saptamsha (Children & Progeny)
* **Divisor:** $N = 7$ | **Span:** $\Delta_7 = 4^\circ 17' 08.57'' = 257.142857'$ ($k \in \{0, 1, \dots, 6\}$).
* **Rule:**
  * **Odd Signs:** Start from sign itself ($S$): $S_{D7} = (S + k) \bmod 12$
  * **Even Signs:** Start from 7th sign from $S$ ($(S+6)\bmod 12$): $S_{D7} = (S + 6 + k) \bmod 12$

---

### $D\text{-}8$: Ashtamsha (Longevity & Hidden Hazards)
* **Divisor:** $N = 8$ | **Span:** $\Delta_8 = 3^\circ 45' 00'' = 225'$ ($k \in \{0, 1, \dots, 7\}$).
* **Rule (by Modality):**
  * **Movable Signs:** Start from Aries ($0$): $S_{D8} = (0 + k) \bmod 12$
  * **Fixed Signs:** Start from Sagittarius ($8$): $S_{D8} = (8 + k) \bmod 12$
  * **Dual Signs:** Start from Leo ($4$): $S_{D8} = (4 + k) \bmod 12$

---

### $D\text{-}9$: Navamsha (Dharma, Marriage & Soul Essence)
* **Divisor:** $N = 9$ | **Span:** $\Delta_9 = 3^\circ 20' 00'' = 200'$ ($k \in \{0, 1, \dots, 8\}$).
* **Method 1: Direct Continuous Pada Mapping (Simplest & Most Robust):**
  $$P = \left\lfloor \frac{\lambda \times 60}{200} \right\rfloor = \lfloor \lambda / 3.333333^\circ \rfloor \quad (0 \le P \le 107)$$
  $$S_{D9} = P \pmod{12}$$
* **Method 2: Elemental Starting Point:**
  * **Fire Signs:** Start from Aries ($0$): $S_{D9} = (0 + k) \bmod 12$
  * **Earth Signs:** Start from Capricorn ($9$): $S_{D9} = (9 + k) \bmod 12$
  * **Air Signs:** Start from Libra ($6$): $S_{D9} = (6 + k) \bmod 12$
  * **Water Signs:** Start from Cancer ($3$): $S_{D9} = (3 + k) \bmod 12$

---

### $D\text{-}10$: Dasamsha (Career, Fame & Social Status)
* **Divisor:** $N = 10$ | **Span:** $\Delta_{10} = 3^\circ 00' 00'' = 180'$ ($k \in \{0, 1, \dots, 9\}$).
* **Rule:**
  * **Odd Signs:** Start from sign itself ($S$): $S_{D10} = (S + k) \bmod 12$
  * **Even Signs:** Start from 9th sign from $S$ ($(S+8)\bmod 12$): $S_{D10} = (S + 8 + k) \bmod 12$

---

### $D\text{-}11$: Rudramsha (Challenges & Destructive Forces)
* **Divisor:** $N = 11$ | **Span:** $\Delta_{11} = 2^\circ 43' 38.18'' = 163.636'$ ($k \in \{0, 1, \dots, 10\}$).
* **Rule:** Count in reverse zodiacal order starting from Aries ($0$):
  $$S_{D11} = (12 - (S + k) \bmod 12) \pmod{12} = (0 - S - k) \pmod{12}$$

---

### $D\text{-}12$: Dwadasamsha (Parents & Ancestral Heritage)
* **Divisor:** $N = 12$ | **Span:** $\Delta_{12} = 2^\circ 30' 00'' = 150'$ ($k \in \{0, 1, \dots, 11\}$).
* **Rule (Sequential from sign itself):**
  $$S_{D12} = (S + k) \pmod{12}$$

---

### $D\text{-}16$: Shodashamsha (Vehicles & Luxuries)
* **Divisor:** $N = 16$ | **Span:** $\Delta_{16} = 1^\circ 52' 30'' = 112.5'$ ($k \in \{0, 1, \dots, 15\}$).
* **Rule (by Modality):**
  * **Movable Signs:** Start from Aries ($0$): $S_{D16} = (0 + k) \bmod 12$
  * **Fixed Signs:** Start from Leo ($4$): $S_{D16} = (4 + k) \bmod 12$
  * **Dual Signs:** Start from Sagittarius ($8$): $S_{D16} = (8 + k) \bmod 12$

---

### $D\text{-}20$: Vimsamsha (Spiritual Progress & Upasana)
* **Divisor:** $N = 20$ | **Span:** $\Delta_{20} = 1^\circ 30' 00'' = 90'$ ($k \in \{0, 1, \dots, 19\}$).
* **Rule (by Modality):**
  * **Movable Signs:** Start from Aries ($0$): $S_{D20} = (0 + k) \bmod 12$
  * **Fixed Signs:** Start from Sagittarius ($8$): $S_{D20} = (8 + k) \bmod 12$
  * **Dual Signs:** Start from Leo ($4$): $S_{D20} = (4 + k) \bmod 12$

---

### $D\text{-}24$: Siddhamsa / Chaturvimsamsha (Education & Learning)
* **Divisor:** $N = 24$ | **Span:** $\Delta_{24} = 1^\circ 15' 00'' = 75'$ ($k \in \{0, 1, \dots, 23\}$).
* **Rule:**
  * **Odd Signs:** Start from Leo ($4$): $S_{D24} = (4 + k) \bmod 12$
  * **Even Signs:** Start from Cancer ($3$): $S_{D24} = (3 + k) \bmod 12$

---

### $D\text{-}27$: Saptavimsamsha / Bhamsa (Strengths & Weaknesses)
* **Divisor:** $N = 27$ | **Span:** $\Delta_{27} = 1^\circ 06' 40'' = 66.6667'$ ($k \in \{0, 1, \dots, 26\}$).
* **Rule (by Element):**
  * **Fire Signs:** Start from Aries ($0$): $S_{D27} = (0 + k) \bmod 12$
  * **Earth Signs:** Start from Cancer ($3$): $S_{D27} = (3 + k) \bmod 12$
  * **Air Signs:** Start from Libra ($6$): $S_{D27} = (6 + k) \bmod 12$
  * **Water Signs:** Start from Capricorn ($9$): $S_{D27} = (9 + k) \bmod 12$

---

### $D\text{-}30$: Trimsamsha (Misfortunes & Arishta)
* **Divisor:** $N = 30$ | **Unequal Step Boundaries**.
* **Step Function:** Let $\lambda_{\text{rel}} = \lambda \pmod{30^\circ}$.
  * **Odd Signs:**
    $$\begin{cases} 
    0^\circ \le \lambda_{\text{rel}} < 5^\circ & \implies \text{Aries (0 / Mars)} \\
    5^\circ \le \lambda_{\text{rel}} < 10^\circ & \implies \text{Aquarius (10 / Saturn)} \\
    10^\circ \le \lambda_{\text{rel}} < 18^\circ & \implies \text{Sagittarius (8 / Jupiter)} \\
    18^\circ \le \lambda_{\text{rel}} < 25^\circ & \implies \text{Gemini (2 / Mercury)} \\
    25^\circ \le \lambda_{\text{rel}} < 30^\circ & \implies \text{Libra (6 / Venus)} 
    \end{cases}$$
  * **Even Signs:**
    $$\begin{cases} 
    0^\circ \le \lambda_{\text{rel}} < 5^\circ & \implies \text{Taurus (1 / Venus)} \\
    5^\circ \le \lambda_{\text{rel}} < 12^\circ & \implies \text{Virgo (5 / Mercury)} \\
    12^\circ \le \lambda_{\text{rel}} < 20^\circ & \implies \text{Pisces (11 / Jupiter)} \\
    20^\circ \le \lambda_{\text{rel}} < 25^\circ & \implies \text{Capricorn (9 / Saturn)} \\
    25^\circ \le \lambda_{\text{rel}} < 30^\circ & \implies \text{Scorpio (7 / Mars)} 
    \end{cases}$$

---

### $D\text{-}40$: Khavedamsha (Auspicious Timing)
* **Divisor:** $N = 40$ | **Span:** $\Delta_{40} = 0^\circ 45' 00'' = 45'$ ($k \in \{0, 1, \dots, 39\}$).
* **Rule:**
  * **Odd Signs:** Start from Aries ($0$): $S_{D40} = (0 + k) \bmod 12$
  * **Even Signs:** Start from Libra ($6$): $S_{D40} = (6 + k) \bmod 12$

---

### $D\text{-}45$: Akshavedamsha (Moral Integrity & All Aspects)
* **Divisor:** $N = 45$ | **Span:** $\Delta_{45} = 0^\circ 40' 00'' = 40'$ ($k \in \{0, 1, \dots, 44\}$).
* **Rule (by Modality):**
  * **Movable Signs:** Start from Aries ($0$): $S_{D45} = (0 + k) \bmod 12$
  * **Fixed Signs:** Start from Leo ($4$): $S_{D45} = (4 + k) \bmod 12$
  * **Dual Signs:** Start from Sagittarius ($8$): $S_{D45} = (8 + k) \bmod 12$

---

### $D\text{-}60$: Shashtiamsha (Past Life Karmic Roots)
* **Divisor:** $N = 60$ | **Span:** $\Delta_{60} = 0^\circ 30' 00'' = 30'$ ($k \in \{0, 1, \dots, 59\}$).
* **Sign Mapping:**
  $$S_{D60} = (S + k) \pmod{12}$$
* **Deity Index ($m \in \{1, \dots, 60\}$):**
  * **Odd Signs:** $m = k + 1$ (Direct $1 \to 60$).
  * **Even Signs:** $m = 61 - (k + 1)$ (Reverse $60 \to 1$).

---

# 4. Higher Divisional Harmonics ($D\text{-}72$ to $D\text{-}300$)

### $D\text{-}72$: Ashtamamsha
* **Span:** $\Delta_{72} = 0^\circ 25' 00'' = 1500''$.
* **Mapping:** Movable start Aries ($0$), Fixed start Sagittarius ($8$), Dual start Leo ($4$).

### $D\text{-}81$: Nava-Navamsha
* **Span:** $\Delta_{81} = 0^\circ 22' 13.33'' = 1333.33''$.
* **Mapping:** $D\text{-}9$ of $D\text{-}9$. Elemental start (Fire: Aries, Earth: Cap, Air: Lib, Water: Can).

### $D\text{-}108$: Ashtottaramsa
* **Span:** $\Delta_{108} = 0^\circ 16' 40'' = 1000''$.
* **Mapping:** Global continuous 108 division index: $S_{D108} = \lfloor \lambda / 0.277778^\circ \rfloor \bmod 12$.

### $D\text{-}144$: Dwadasamsha-Dwadasamsha
* **Span:** $\Delta_{144} = 0^\circ 12' 30'' = 750''$.
* **Mapping:** Sequential from sign: $S_{D144} = (S + k) \bmod 12$.

### $D\text{-}150$: Nadiamsa (Chandra Kala Nadi)
* **Span:** $\Delta_{150} = 0^\circ 12' 00'' = 720'' = 0.2^\circ$.
* **Division Index:** $k = \lfloor \lambda_{\text{rel}} / 0.2^\circ \rfloor \quad (0 \le k \le 149)$.
* **Nadi Name Progression ($N_i \in \{1, \dots, 150\}$):**
  * **Movable Signs:** $N_i = k + 1$ ($1 \to 150$)
  * **Fixed Signs:** $N_i = 150 - k$ ($150 \to 1$)
  * **Dual Signs:**
    * If $k < 75$: $N_i = k + 76$ ($76 \to 150$)
    * If $k \ge 75$: $N_i = 150 - (k - 75)$ ($75 \to 1$)

### $D\text{-}300$: Ardha-Nadiamsa
* **Span:** $\Delta_{300} = 0^\circ 06' 00'' = 360'' = 0.1^\circ$.
* **Mapping:** Splits each of the 150 Nadiamsas into **Purva Bhaga** (first half, $0''\text{--}360''$) and **Uttara Bhaga** (second half, $360''\text{--}720''$).

---

# 5. Vimsopaka Bala Scoring System

| Varga Group | Total Points | Point Allocations per Chart |
| :--- | :---: | :--- |
| **Shadvarga (6)** | 20 | D1: 6, D2: 2, D3: 4, D9: 5, D12: 2, D30: 1 |
| **Saptavarga (7)** | 20 | D1: 5, D2: 2, D3: 3, D7: 2.5, D9: 4.5, D12: 2, D30: 1 |
| **Dashavarga (10)** | 20 | D1: 3, D2: 1.5, D3: 1.5, D7: 1.5, D9: 1.5, D10: 1.5, D12: 1.5, D16: 1.5, D30: 1.5, D60: 5 |
| **Shodashavarga (16)** | 20 | D1: 3.5, D2: 1, D3: 1, D4: 0.5, D7: 0.5, D9: 3, D10: 0.5, D12: 0.5, D16: 2, D20: 0.5, D24: 0.5, D27: 0.5, D30: 1, D40: 0.5, D45: 0.5, D60: 4 |

---

# 6. Krishnamurti Paddhati (KP) System Calculations

### 6.1 KP Ayanamsha Precision Formula
$$\text{Ayanamsha}(T) = 22^\circ 22' 31.6'' + 50.2388475'' \times (\text{Decimal Year} - 1900.0)$$

### 6.2 Placidus House Cusps & Intercepts
KP utilizes **Placidus Unequal Houses**:
* Cusps represent the **beginning** of the house (not the midpoint).
* **RAMC:** $\text{RAMC} = \text{Local Sidereal Time} \times 15^\circ$.
* **Ascendant:** $\tan(\text{Asc}) = \frac{\cos(\text{RAMC})}{-\sin(\text{RAMC})\cos(\epsilon) - \tan(\phi)\sin(\epsilon)}$.
* **MC ($10\text{th Cusp}$):** $\tan(\text{MC}) = \frac{\tan(\text{RAMC})}{\cos(\epsilon)}$.

### 6.3 The 4-Tier Sub-Lord Hierarchy
$$\text{Nakshatra Width } = \frac{360^\circ}{27} = 13^\circ 20' = 800'$$
$$\text{Sub-Lord Arc Width } = \frac{\text{Vimshottari Years of Sub-Lord}}{120} \times 800'$$

| Planet | Dasha Years | Fraction | Arc Width | Seconds of Arc |
| :--- | :---: | :---: | :--- | :--- |
| **Ketu** | 7 | $7 / 120$ | $0^\circ 46' 40''$ | $2,800''$ |
| **Venus** | 20 | $20 / 120$ | $2^\circ 13' 20''$ | $8,000''$ |
| **Sun** | 6 | $6 / 120$ | $0^\circ 40' 00''$ | $2,400''$ |
| **Moon** | 10 | $10 / 120$ | $1^\circ 06' 40''$ | $4,000''$ |
| **Mars** | 7 | $7 / 120$ | $0^\circ 46' 40''$ | $2,800''$ |
| **Rahu** | 18 | $18 / 120$ | $2^\circ 00' 00''$ | $7,200''$ |
| **Jupiter** | 16 | $16 / 120$ | $1^\circ 46' 40''$ | $6,400''$ |
| **Saturn** | 19 | $19 / 120$ | $2^\circ 06' 40''$ | $7,600''$ |
| **Mercury** | 17 | $17 / 120$ | $1^\circ 53' 20''$ | $6,800''$ |

### 6.4 Derivation of the 249 KP Sub-Divisions
There are $27 \times 9 = 243$ raw sub-divisions. Exactly **6 sub-divisions cross $30^\circ$ sign boundaries**, creating 6 split entries:
1. **$30^\circ$ (Aries/Taurus):** Krittika (Mars sub) $\implies$ Sub #26 & #27.
2. **$90^\circ$ (Gemini/Cancer):** Punarvasu (Rahu sub) $\implies$ Sub #67 & #68.
3. **$150^\circ$ (Leo/Virgo):** Uttara Phalguni (Mars sub) $\implies$ Sub #108 & #109.
4. **$180^\circ$ (Virgo/Libra):** Chitra (Rahu sub) $\implies$ Sub #129 & #130.
5. **$240^\circ$ (Scorpio/Sagittarius):** Vishakha (Jupiter sub) $\implies$ Sub #170 & #171.
6. **$330^\circ$ (Aquarius/Pisces):** Purva Bhadrapada (Rahu sub) $\implies$ Sub #231 & #232.

$$\text{Total Table Size} = 243 + 6 = \mathbf{249}$$

### 6.5 Sub-Sub-Lord (SSL) & Sub-Sub-Sub-Lord (SSSL)
$$\Delta_{\text{SSL}} = \frac{Y_{\text{SSL}}}{120} \times \Delta_{\text{Sub}}$$
$$\Delta_{\text{SSSL}} = \frac{Y_{\text{SSSL}}}{120} \times \Delta_{\text{SSL}}$$

### 6.6 4-Fold Significators (Levels 1 to 4)
* **Level 1 (A):** Planet posited in the Constellation (Star) of an Occupant of the house. (Strongest)
* **Level 2 (B):** Planet occupying the house.
* **Level 3 (C):** Planet in the Constellation (Star) of the Lord of the house.
* **Level 4 (D):** Lord (Sign ruler) of the house. (Weakest)

### 6.7 Cuspal Sub-Lord Rules for Event Verification
An event promised by a house cusp $H$ is fulfilled if its **Cuspal Sub-Lord** is a significator of favorable houses:
* **Marriage (House 7):** Sub-Lord of 7th Cusp signifies $2, 7, 11$ (Not $1, 6, 10, 12$).
* **Job / Career (House 10):** Sub-Lord of 10th Cusp signifies $2, 6, 10, 11$ (Not $1, 5, 9$).
* **Childbirth (House 5):** Sub-Lord of 5th Cusp signifies $2, 5, 11$ (Not $1, 4, 10$).
* **Foreign Travel (House 9/12):** Sub-Lord of 9th or 12th Cusp signifies $3, 9, 12$.

### 6.8 Ruling Planets (RP) & Timing of Events
1. **Lagna Star Lord**
2. **Lagna Sign Lord**
3. **Moon Star Lord**
4. **Moon Sign Lord**
5. **Day Lord (Vara Lord)** (from Sunrise to Sunrise)

### 6.9 KP Fortuna (Part of Fortune)
$$\lambda_{\text{Fortuna}} = (\lambda_{\text{Ascendant}} + \lambda_{\text{Moon}} - \lambda_{\text{Sun}}) \pmod{360^\circ}$$

---

# 7. Complete Production Python Reference Engine

```python
"""
Complete Vedic Divisional Charts (Vargas D-1 to D-150+) & KP Sub-Lord Calculation Engine
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
        "Star_Lord": VIMSHOTTARI_LORDS[star_idx],
        "Sub_Lord": VIMSHOTTARI_LORDS[sub_idx],
        "Sub_Sub_Lord": VIMSHOTTARI_LORDS[ssl_idx],
        "Sub_Sub_Sub_Lord": VIMSHOTTARI_LORDS[sssl_idx]
    }
```
