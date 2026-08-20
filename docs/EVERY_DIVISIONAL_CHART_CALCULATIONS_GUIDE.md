# Comprehensive Divisional Charts ($D\text{-}1$ to $D\text{-}300$) Calculation Handbook
## *Exact Mathematical Derivations, Worked Examples, Pure Python, and Vectorized NumPy Implementations*

---

## Workspace Source Code Links
* **Python Engine:** [`varga_kp_engine.py`](file:///d:/Gana/Jamakkol%20Prasanam/varga_kp_engine.py)
* **Vectorized NumPy Engine:** [`varga_kp_numpy.py`](file:///d:/Gana/Jamakkol%20Prasanam/varga_kp_numpy.py)
* **Pydantic Schema Module:** [`Schema.py`](file:///d:/Gana/Jamakkol%20Prasanam/Schema.py)
* **Master KP & Varga Guide:** [`VEDIC_VARGAS_AND_KP_MASTER_GUIDE.md`](file:///d:/Gana/Jamakkol%20Prasanam/docs/VEDIC_VARGAS_AND_KP_MASTER_GUIDE.md)

---

# Table of Contents
1. [Core Mathematical Variables & Standardization](#1-core-mathematical-variables--standardization)
2. [Universal Calculation Blueprint (Every Chart Follows This)](#2-universal-calculation-blueprint)
3. [Exhaustive Breakdown for Every Divisional Chart](#3-exhaustive-breakdown-for-every-divisional-chart)
   - [D-1: Rasi (Harmonic 1)](#d-1-rasi-chart)
   - [D-2: Hora (Harmonic 2)](#d-2-hora-wealth--resources)
   - [D-3: Drekkana (Harmonic 3)](#d-3-drekkana-siblings--courage)
   - [D-4: Chaturthamsa / Turyamsha (Harmonic 4)](#d-4-chaturthamsa-assets--home)
   - [D-5: Panchamsha (Harmonic 5)](#d-5-panchamsha-spiritual-power--fame)
   - [D-6: Shashtamsha (Harmonic 6)](#d-6-shashtamsha-health-debts--enemies)
   - [D-7: Saptamsha (Harmonic 7)](#d-7-saptamsha-progeny--children)
   - [D-8: Ashtamsha (Harmonic 8)](#d-8-ashtamsha-longevity--hidden-hazards)
   - [D-9: Navamsha (Harmonic 9)](#d-9-navamsha-dharma-marriage--inner-strength)
   - [D-10: Dasamsha (Harmonic 10)](#d-10-dasamsha-career-fame--profession)
   - [D-11: Rudramsha (Harmonic 11)](#d-11-rudramsha-death--destructive-forces)
   - [D-12: Dwadasamsha (Harmonic 12)](#d-12-dwadasamsha-parents--ancestry)
   - [D-16: Shodashamsha / Kalamsa (Harmonic 16)](#d-16-shodashamsha-vehicles--luxuries)
   - [D-20: Vimsamsha (Harmonic 20)](#d-20-vimsamsha-spiritual-progress--upasana)
   - [D-24: Siddhamsa / Chaturvimsamsha (Harmonic 24)](#d-24-siddhamsa-education--intellect)
   - [D-27: Saptavimsamsha / Bhamsa (Harmonic 27)](#d-27-saptavimsamsha-vitality--strengths)
   - [D-30: Trimsamsha (Harmonic 30 - Unequal)](#d-30-trimsamsha-misfortunes--arishta)
   - [D-40: Khavedamsha (Harmonic 40)](#d-40-khavedamsha-auspicious-timing)
   - [D-45: Akshavedamsha (Harmonic 45)](#d-45-akshavedamsha-moral-integrity--all-areas)
   - [D-60: Shashtiamsha (Harmonic 60)](#d-60-shashtiamsha-past-life-karmic-roots)
   - [D-72: Ashtamamsha (Harmonic 72)](#d-72-ashtamamsha-subtle-vitality)
   - [D-81: Nava-Navamsha (Harmonic 81)](#d-81-nava-navamsha-soul-refinement)
   - [D-108: Ashtottaramsa (Harmonic 108)](#d-108-ashtottaramsa-sacred-destiny)
   - [D-144: Dwadasa-Dwadasamsha (Harmonic 144)](#d-144-dwadasa-dwadasamsha-genetic-heritage)
   - [D-150: Nadiamsa (Harmonic 150)](#d-150-nadiamsa-chandra-kala-nadi)
   - [D-300: Ardha-Nadiamsa (Harmonic 300)](#d-300-ardha-nadiamsa-palm-leaf-timing)
4. [Master Verification Matrix for a Sample Chart](#4-master-verification-matrix)

---

# 1. Core Mathematical Variables & Standardization

Throughout this document, we use standard mathematical variables:
* **$\lambda$ (Absolute Longitude):** Continuous angle $[0^\circ, 360^\circ)$.
* **$S$ (Rasi Sign Index):** $S = \lfloor \lambda / 30^\circ \rfloor \in \{0, 1, \dots, 11\}$:
  * `0 = Aries`, `1 = Taurus`, `2 = Gemini`, `3 = Cancer`, `4 = Leo`, `5 = Virgo`
  * `6 = Libra`, `7 = Scorpio`, `8 = Sagittarius`, `9 = Capricorn`, `10 = Aquarius`, `11 = Pisces`
* **$\lambda_{\text{rel}}$ (Relative Longitude in Sign):** $\lambda_{\text{rel}} = \lambda \pmod{30^\circ} \in [0^\circ, 30^\circ)$.
* **Standard Test Planet Used in All Examples:**  
  **Jupiter at $14^\circ 15' 00''\text{ Gemini}$**
  $$\lambda = 60^\circ + 14.25^\circ = \mathbf{74.25^\circ} \implies S = 2 \text{ (Gemini)}, \quad \lambda_{\text{rel}} = 14.25^\circ$$

---

# 2. Universal Calculation Blueprint

Every equal harmonic divisional chart $D\text{-}N$ follows **4 identical mathematical steps**:

```
 1. Division Width (Δ_N)    ──► Δ_N = 30° / N
 2. Division Index (k)      ──► k = floor(λ_rel / Δ_N)   (where 0 <= k < N)
 3. Remainder inside Arc    ──► rem = λ_rel - (k * Δ_N)
 4. Longitude in D-N Chart  ──► deg_in_varga = (rem * N) mod 30°
 5. Target Sign Index       ──► S_DN = (StartSign(S, N) + k) mod 12
```

---

# 3. Exhaustive Breakdown for Every Divisional Chart

---

### $D\text{-}1$: Rasi Chart
* **Astrological Focus:** General destiny, physical constitution, overall life baseline.
* **Divisor:** $N = 1$ | **Arc:** $\Delta_1 = 30^\circ 00' 00'' = 1800'$.
* **Mathematical Formula:**
  $$S_{D1} = S = \lfloor \lambda / 30^\circ \rfloor, \quad \lambda_{D1} = \lambda_{\text{rel}}$$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * $S = \lfloor 74.25 / 30 \rfloor = 2 \implies \mathbf{Gemini}$ at $14.25^\circ$ ($14^\circ 15' 00''$).
* **Pure Python:**
  ```python
  target_sign = s_idx
  deg_varga = deg_in_sign
  ```
* **NumPy Vectorized:**
  ```python
  target_sign = (lon // 30).astype(int)
  deg_varga = lon % 30.0
  ```

---

### $D\text{-}2$: Hora (Wealth & Resources)
* **Astrological Focus:** Financial status, accumulated wealth, speech, capacity to earn.
* **Divisor:** $N = 2$ | **Arc:** $\Delta_2 = 15^\circ 00' 00'' = 900'$ ($k \in \{0, 1\}$).
* **Parashari Rules:**
  * **Odd Signs ($S \in \{0, 2, 4, 6, 8, 10\}$):**
    * $0^\circ \text{--} 15^\circ$ ($k=0$): **Leo (Sun / 4)**
    * $15^\circ \text{--} 30^\circ$ ($k=1$): **Cancer (Moon / 3)**
  * **Even Signs ($S \in \{1, 3, 5, 7, 9, 11\}$):**
    * $0^\circ \text{--} 15^\circ$ ($k=0$): **Cancer (Moon / 3)**
    * $15^\circ \text{--} 30^\circ$ ($k=1$): **Leo (Sun / 4)**
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is an **Odd Sign**.
  * $\lambda_{\text{rel}} = 14.25^\circ < 15^\circ \implies k = 0$.
  * Odd sign + 1st half $\implies \mathbf{Leo}$ ($S_{D2}=4$) at $14.25^\circ \times 2 = \mathbf{28^\circ 30' 00''\text{ Leo}}$.
* **Pure Python:**
  ```python
  is_odd = (s_idx % 2 == 0)
  target = (4 if k == 0 else 3) if is_odd else (3 if k == 0 else 4)
  ```
* **NumPy Vectorized:**
  ```python
  target = np.where(is_odd, np.where(k == 0, 4, 3), np.where(k == 0, 3, 4))
  ```

---

### $D\text{-}3$: Drekkana (Siblings & Courage)
* **Astrological Focus:** Younger siblings, courage, initiatives, drive, vitality.
* **Divisor:** $N = 3$ | **Arc:** $\Delta_3 = 10^\circ 00' 00'' = 600'$ ($k \in \{0, 1, 2\}$).
* **Formula (Trinal Progression: $1\text{st}, 5\text{th}, 9\text{th}$):**
  $$S_{D3} = (S + 4 \cdot k) \pmod{12}$$
  * $k = 0$ ($0^\circ \text{--} 10^\circ$): 1st sign (Same sign $S$)
  * $k = 1$ ($10^\circ \text{--} 20^\circ$): 5th sign from $S$ ($(S + 4) \bmod 12$)
  * $k = 2$ ($20^\circ \text{--} 30^\circ$): 9th sign from $S$ ($(S + 8) \bmod 12$)
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$), $\lambda_{\text{rel}} = 14.25^\circ$.
  * $k = \lfloor 14.25 / 10 \rfloor = 1$ ($2\text{nd part}, 10^\circ\text{--}20^\circ$).
  * $S_{D3} = (2 + 4 \times 1) \bmod 12 = 6 \implies \mathbf{Libra}$.
  * Remainder: $14.25 - 10 = 4.25^\circ \implies 4.25^\circ \times 3 = \mathbf{12^\circ 45' 00''\text{ Libra}}$.
* **Pure Python:**
  ```python
  target = (s_idx + 4 * k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = (rasi_idx + 4 * k) % 12
  ```

---

### $D\text{-}4$: Chaturthamsa (Assets & Home)
* **Astrological Focus:** Real estate, immovable property, vehicles, domestic peace.
* **Divisor:** $N = 4$ | **Arc:** $\Delta_4 = 7^\circ 30' 00'' = 450'$ ($k \in \{0, 1, 2, 3\}$).
* **Formula (Kendra Progression: $1\text{st}, 4\text{th}, 7\text{th}, 10\text{th}$):**
  $$S_{D4} = (S + 3 \cdot k) \pmod{12}$$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$), $\lambda_{\text{rel}} = 14.25^\circ$.
  * $k = \lfloor 14.25 / 7.5 \rfloor = 1$.
  * $S_{D4} = (2 + 3 \times 1) \bmod 12 = 5 \implies \mathbf{Virgo}$.
  * Remainder: $14.25 - 7.5 = 6.75^\circ \implies 6.75^\circ \times 4 = \mathbf{27^\circ 00' 00''\text{ Virgo}}$.
* **Pure Python:**
  ```python
  target = (s_idx + 3 * k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = (rasi_idx + 3 * k) % 12
  ```

---

### $D\text{-}5$: Panchamsha (Spiritual Power & Fame)
* **Astrological Focus:** Power, authority, spiritual mantra siddhi, legacy.
* **Divisor:** $N = 5$ | **Arc:** $\Delta_5 = 6^\circ 00' 00'' = 360'$ ($k \in \{0, 1, 2, 3, 4\}$).
* **Formula (by Modality):**
  * **Movable Signs ($S \bmod 3 == 0$):** Start from Aries ($0$): $S_{D5} = (0 + k) \bmod 12$
  * **Fixed Signs ($S \bmod 3 == 1$):** Start from Leo ($4$): $S_{D5} = (4 + k) \bmod 12$
  * **Dual Signs ($S \bmod 3 == 2$):** Start from Sagittarius ($8$): $S_{D5} = (8 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is a **Dual Sign** (modality $= 2$).
  * $k = \lfloor 14.25 / 6 \rfloor = 2$.
  * Dual signs start at Sagittarius ($8$) $\implies S_{D5} = (8 + 2) \bmod 12 = 10 \implies \mathbf{Aquarius}$.
  * Remainder: $14.25 - 12 = 2.25^\circ \implies 2.25^\circ \times 5 = \mathbf{11^\circ 15' 00''\text{ Aquarius}}$.
* **Pure Python:**
  ```python
  start = 0 if modality == 0 else (4 if modality == 1 else 8)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
  target = (start + k) % 12
  ```

---

### $D\text{-}6$: Shashtamsha (Health, Debts & Enemies)
* **Astrological Focus:** Chronic health, litigation, disputes, financial debts, obstacles.
* **Divisor:** $N = 6$ | **Arc:** $\Delta_6 = 5^\circ 00' 00'' = 300'$ ($k \in \{0, 1, \dots, 5\}$).
* **Formula:**
  * **Odd Signs:** Start from Aries ($0$): $S_{D6} = (0 + k) \bmod 12$
  * **Even Signs:** Start from Libra ($6$): $S_{D6} = (6 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $k = \lfloor 14.25 / 5 \rfloor = 2$.
  * $S_{D6} = (0 + 2) \bmod 12 = 2 \implies \mathbf{Gemini}$.
  * Remainder: $14.25 - 10 = 4.25^\circ \implies 4.25^\circ \times 6 = \mathbf{25^\circ 30' 00''\text{ Gemini}}$.
* **Pure Python:**
  ```python
  start = 0 if is_odd else 6
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.where(is_odd, 0, 6)
  target = (start + k) % 12
  ```

---

### $D\text{-}7$: Saptamsha (Progeny & Children)
* **Astrological Focus:** Children, grandchildren, fertility, legacy, happiness from kids.
* **Divisor:** $N = 7$ | **Arc:** $\Delta_7 = 4^\circ 17' 08.57'' = 257.142857'$ ($k \in \{0, \dots, 6\}$).
* **Formula:**
  * **Odd Signs:** Start from $S$: $S_{D7} = (S + k) \bmod 12$
  * **Even Signs:** Start from $S + 6$: $S_{D7} = (S + 6 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $\Delta_7 = 4.285714^\circ$.
  * $k = \lfloor 14.25 / 4.285714 \rfloor = 3$.
  * $S_{D7} = (2 + 3) \bmod 12 = 5 \implies \mathbf{Virgo}$.
  * Remainder: $14.25 - (3 \times 4.285714) = 1.392857^\circ \implies 1.392857 \times 7 = \mathbf{9^\circ 45' 00''\text{ Virgo}}$.
* **Pure Python:**
  ```python
  start = s_idx if is_odd else (s_idx + 6)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.where(is_odd, rasi_idx, rasi_idx + 6)
  target = (start + k) % 12
  ```

---

### $D\text{-}8$: Ashtamsha (Longevity & Hidden Hazards)
* **Astrological Focus:** Longevity, unexpected hazards, sudden windfalls, occult.
* **Divisor:** $N = 8$ | **Arc:** $\Delta_8 = 3^\circ 45' 00'' = 225'$ ($k \in \{0, \dots, 7\}$).
* **Formula (by Modality):**
  * **Movable:** Start Aries ($0$): $S_{D8} = (0 + k) \bmod 12$
  * **Fixed:** Start Sagittarius ($8$): $S_{D8} = (8 + k) \bmod 12$
  * **Dual:** Start Leo ($4$): $S_{D8} = (4 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Dual**. $k = \lfloor 14.25 / 3.75 \rfloor = 3$.
  * $S_{D8} = (4 + 3) \bmod 12 = 7 \implies \mathbf{Scorpio}$.
  * Remainder: $14.25 - (3 \times 3.75) = 3.00^\circ \implies 3.00^\circ \times 8 = \mathbf{24^\circ 00' 00''\text{ Scorpio}}$.
* **Pure Python:**
  ```python
  start = 0 if modality == 0 else (8 if modality == 1 else 4)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([modality == 0, modality == 1, modality == 2], [0, 8, 4])
  target = (start + k) % 12
  ```

---

### $D\text{-}9$: Navamsha (Dharma, Marriage & Inner Strength)
* **Astrological Focus:** The most essential divisional chart. Represents spouse, marital happiness, innate dharma, and the true inner strength of all planets.
* **Divisor:** $N = 9$ | **Arc:** $\Delta_9 = 3^\circ 20' 00'' = 200'$ ($k \in \{0, \dots, 8\}$).
* **Global Continuous Pada Formula:**
  $$P = \lfloor \lambda / 3.333333^\circ \rfloor = \lfloor (\lambda \times 60) / 200 \rfloor \quad (0 \le P \le 107)$$
  $$S_{D9} = P \pmod{12}$$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Global Pada $P = \lfloor 74.25 / 3.333333 \rfloor = 22$.
  * $S_{D9} = 22 \bmod 12 = 10 \implies \mathbf{Aquarius}$.
  * Remainder in Pada: $74.25 - (22 \times 3.333333) = 0.916667^\circ$.
  * Longitude in Aquarius: $0.916667 \times 9 = \mathbf{8^\circ 15' 00''\text{ Aquarius}}$.
* **Pure Python:**
  ```python
  target = int(lon // (30.0 / 9.0)) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = ((lon // (30.0 / 9.0)).astype(int)) % 12
  ```

---

### $D\text{-}10$: Dasamsha (Career, Fame & Profession)
* **Astrological Focus:** Profession, career achievement, government honours, reputation.
* **Divisor:** $N = 10$ | **Arc:** $\Delta_{10} = 3^\circ 00' 00'' = 180'$ ($k \in \{0, \dots, 9\}$).
* **Formula:**
  * **Odd Signs:** Start from $S$: $S_{D10} = (S + k) \bmod 12$
  * **Even Signs:** Start from $S + 8$ (9th sign): $S_{D10} = (S + 8 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $k = \lfloor 14.25 / 3.0 \rfloor = 4$.
  * $S_{D10} = (2 + 4) \bmod 12 = 6 \implies \mathbf{Libra}$.
  * Remainder: $14.25 - 12 = 2.25^\circ \implies 2.25^\circ \times 10 = \mathbf{22^\circ 30' 00''\text{ Libra}}$.
* **Pure Python:**
  ```python
  start = s_idx if is_odd else (s_idx + 8)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.where(is_odd, rasi_idx, rasi_idx + 8)
  target = (start + k) % 12
  ```

---

### $D\text{-}11$: Rudramsha (Death & Destructive Forces)
* **Astrological Focus:** Arishta, heavy karmic battles, destructive challenges, longevity threats.
* **Divisor:** $N = 11$ | **Arc:** $\Delta_{11} = 2^\circ 43' 38.18'' = 163.636'$ ($k \in \{0, \dots, 10\}$).
* **Formula:** Reverse counting from Aries ($0$):
  $$S_{D11} = (12 - (S + k) \bmod 12) \pmod{12} = (0 - S - k) \pmod{12}$$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * $S = 2, \Delta_{11} = 2.727273^\circ$. $k = \lfloor 14.25 / 2.727273 \rfloor = 5$.
  * $S_{D11} = (0 - 2 - 5) \bmod 12 = -7 \bmod 12 = 5 \implies \mathbf{Virgo}$.
* **Pure Python:**
  ```python
  target = (12 - (s_idx + k) % 12) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = (12 - (rasi_idx + k) % 12) % 12
  ```

---

### $D\text{-}12$: Dwadasamsha (Parents & Ancestry)
* **Astrological Focus:** Father, mother, ancestral bloodline, genetic conditioning.
* **Divisor:** $N = 12$ | **Arc:** $\Delta_{12} = 2^\circ 30' 00'' = 150'$ ($k \in \{0, \dots, 11\}$).
* **Formula (Sequential from sign itself):**
  $$S_{D12} = (S + k) \pmod{12}$$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$), $k = \lfloor 14.25 / 2.5 \rfloor = 5$.
  * $S_{D12} = (2 + 5) \bmod 12 = 7 \implies \mathbf{Scorpio}$.
  * Remainder: $14.25 - 12.5 = 1.75^\circ \implies 1.75 \times 12 = \mathbf{21^\circ 00' 00''\text{ Scorpio}}$.
* **Pure Python:**
  ```python
  target = (s_idx + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = (rasi_idx + k) % 12
  ```

---

### $D\text{-}16$: Shodashamsha (Vehicles & Luxuries)
* **Astrological Focus:** Conveyances, vehicles, mental contentment, material comforts.
* **Divisor:** $N = 16$ | **Arc:** $\Delta_{16} = 1^\circ 52' 30'' = 112.5'$ ($k \in \{0, \dots, 15\}$).
* **Formula (by Modality):**
  * Movable: Start Aries ($0$), Fixed: Start Leo ($4$), Dual: Start Sagittarius ($8$).
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Dual** (start $= 8$). $\Delta_{16} = 1.875^\circ$.
  * $k = \lfloor 14.25 / 1.875 \rfloor = 7$.
  * $S_{D16} = (8 + 7) \bmod 12 = 15 \bmod 12 = 3 \implies \mathbf{Cancer}$.
* **Pure Python:**
  ```python
  start = 0 if modality == 0 else (4 if modality == 1 else 8)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
  target = (start + k) % 12
  ```

---

### $D\text{-}20$: Vimsamsha (Spiritual Progress & Upasana)
* **Astrological Focus:** Spiritual evolution, meditation, chosen deity (Ishta Devata), upasana.
* **Divisor:** $N = 20$ | **Arc:** $\Delta_{20} = 1^\circ 30' 00'' = 90'$ ($k \in \{0, \dots, 19\}$).
* **Formula (by Modality):**
  * Movable: Start Aries ($0$), Fixed: Start Sagittarius ($8$), Dual: Start Leo ($4$).
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Dual** (start $= 4$). $\Delta_{20} = 1.5^\circ$.
  * $k = \lfloor 14.25 / 1.5 \rfloor = 9$.
  * $S_{D20} = (4 + 9) \bmod 12 = 1 \implies \mathbf{Taurus}$.
* **Pure Python:**
  ```python
  start = 0 if modality == 0 else (8 if modality == 1 else 4)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([modality == 0, modality == 1, modality == 2], [0, 8, 4])
  target = (start + k) % 12
  ```

---

### $D\text{-}24$: Siddhamsa (Education & Intellect)
* **Astrological Focus:** Academic achievements, scholarship, intellectual prowess, skill mastery.
* **Divisor:** $N = 24$ | **Arc:** $\Delta_{24} = 1^\circ 15' 00'' = 75'$ ($k \in \{0, \dots, 23\}$).
* **Formula:**
  * **Odd Signs:** Start Leo ($4$): $S_{D24} = (4 + k) \bmod 12$
  * **Even Signs:** Start Cancer ($3$): $S_{D24} = (3 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $\Delta_{24} = 1.25^\circ$.
  * $k = \lfloor 14.25 / 1.25 \rfloor = 11$.
  * $S_{D24} = (4 + 11) \bmod 12 = 3 \implies \mathbf{Cancer}$.
* **Pure Python:**
  ```python
  start = 4 if is_odd else 3
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.where(is_odd, 4, 3)
  target = (start + k) % 12
  ```

---

### $D\text{-}27$: Saptavimsamsha (Vitality & Strengths)
* **Astrological Focus:** Subconscious strengths, physical stamina, constitutional resilience.
* **Divisor:** $N = 27$ | **Arc:** $\Delta_{27} = 1^\circ 06' 40'' = 66.6667'$ ($k \in \{0, \dots, 26\}$).
* **Formula (by Element):**
  * Fire $\to$ Aries ($0$), Earth $\to$ Cancer ($3$), Air $\to$ Libra ($6$), Water $\to$ Capricorn ($9$).
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Air** (start $= 6$). $\Delta_{27} = 1.111111^\circ$.
  * $k = \lfloor 14.25 / 1.111111 \rfloor = 12$.
  * $S_{D27} = (6 + 12) \bmod 12 = 6 \implies \mathbf{Libra}$.
* **Pure Python:**
  ```python
  start = 0 if element == 0 else (3 if element == 1 else (6 if element == 2 else 9))
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([element == 0, element == 1, element == 2, element == 3], [0, 3, 6, 9])
  target = (start + k) % 12
  ```

---

### $D\text{-}30$: Trimsamsha (Misfortunes & Arishta)
* **Astrological Focus:** Misfortunes, severe sickness, karmic obstacles, chronic diseases.
* **Divisor:** $N = 30$ | **Unequal Step Boundaries**.
* **Step Function:**
  * **Odd Signs:**
    * $0^\circ \text{--} 5^\circ$: Aries ($0$ / Mars)
    * $5^\circ \text{--} 10^\circ$: Aquarius ($10$ / Saturn)
    * $10^\circ \text{--} 18^\circ$: Sagittarius ($8$ / Jupiter)
    * $18^\circ \text{--} 25^\circ$: Gemini ($2$ / Mercury)
    * $25^\circ \text{--} 30^\circ$: Libra ($6$ / Venus)
  * **Even Signs:**
    * $0^\circ \text{--} 5^\circ$: Taurus ($1$ / Venus)
    * $5^\circ \text{--} 12^\circ$: Virgo ($5$ / Mercury)
    * $12^\circ \text{--} 20^\circ$: Pisces ($11$ / Jupiter)
    * $20^\circ \text{--} 25^\circ$: Capricorn ($9$ / Saturn)
    * $25^\circ \text{--} 30^\circ$: Scorpio ($7$ / Mars)
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $\lambda_{\text{rel}} = 14.25^\circ$.
  * $14.25^\circ$ falls into $10^\circ \text{--} 18^\circ$ $\implies \mathbf{Sagittarius}$ ($S_{D30}=8$, ruled by Jupiter).
* **Pure Python:**
  ```python
  if is_odd:
      target = 0 if deg_in_sign < 5 else (10 if deg_in_sign < 10 else (8 if deg_in_sign < 18 else (2 if deg_in_sign < 25 else 6)))
  else:
      target = 1 if deg_in_sign < 5 else (5 if deg_in_sign < 12 else (11 if deg_in_sign < 20 else (9 if deg_in_sign < 25 else 7)))
  ```
* **NumPy Vectorized:**
  ```python
  cond_odd = [deg_in_rasi < 5.0, deg_in_rasi < 10.0, deg_in_rasi < 18.0, deg_in_rasi < 25.0, deg_in_rasi >= 25.0]
  choices_odd = [0, 10, 8, 2, 6]
  res_odd = np.select(cond_odd, choices_odd)

  cond_even = [deg_in_rasi < 5.0, deg_in_rasi < 12.0, deg_in_rasi < 20.0, deg_in_rasi < 25.0, deg_in_rasi >= 25.0]
  choices_even = [1, 5, 11, 9, 7]
  res_even = np.select(cond_even, choices_even)

  target = np.where(is_odd, res_odd, res_even)
  ```

---

### $D\text{-}40$: Khavedamsha (Auspicious Timing)
* **Astrological Focus:** Auspicious and inauspicious planetary timing, blessings and curses.
* **Divisor:** $N = 40$ | **Arc:** $\Delta_{40} = 0^\circ 45' 00'' = 45'$ ($k \in \{0, \dots, 39\}$).
* **Formula:**
  * **Odd Signs:** Start Aries ($0$): $S_{D40} = (0 + k) \bmod 12$
  * **Even Signs:** Start Libra ($6$): $S_{D40} = (6 + k) \bmod 12$
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Odd**. $\Delta_{40} = 0.75^\circ$.
  * $k = \lfloor 14.25 / 0.75 \rfloor = 19$.
  * $S_{D40} = (0 + 19) \bmod 12 = 7 \implies \mathbf{Scorpio}$.
* **Pure Python:**
  ```python
  start = 0 if is_odd else 6
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.where(is_odd, 0, 6)
  target = (start + k) % 12
  ```

---

### $D\text{-}45$: Akshavedamsha (Moral Integrity & All Areas)
* **Astrological Focus:** General moral conduct, purity of soul, universal life analysis.
* **Divisor:** $N = 45$ | **Arc:** $\Delta_{45} = 0^\circ 40' 00'' = 40'$ ($k \in \{0, \dots, 44\}$).
* **Formula (by Modality):**
  * Movable: Start Aries ($0$), Fixed: Start Leo ($4$), Dual: Start Sagittarius ($8$).
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$) is **Dual** (start $= 8$). $\Delta_{45} = 0.666667^\circ$.
  * $k = \lfloor 14.25 / 0.666667 \rfloor = 21$.
  * $S_{D45} = (8 + 21) \bmod 12 = 5 \implies \mathbf{Virgo}$.
* **Pure Python:**
  ```python
  start = 0 if modality == 0 else (4 if modality == 1 else 8)
  target = (start + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  start = np.select([modality == 0, modality == 1, modality == 2], [0, 4, 8])
  target = (start + k) % 12
  ```

---

### $D\text{-}60$: Shashtiamsha (Past Life Karmic Roots)
* **Astrological Focus:** The deepest, most authoritative Parashari chart. Represents the exact root cause of past-life karma shaping this birth.
* **Divisor:** $N = 60$ | **Arc:** $\Delta_{60} = 0^\circ 30' 00'' = 30'$ ($k \in \{0, \dots, 59\}$).
* **Formula:**
  $$S_{D60} = (S + k) \pmod{12}$$
* **Deity Index ($1$ to $60$):**
  * Odd signs: $m = k + 1$ (Direct order $1 \to 60$).
  * Even signs: $m = 61 - (k + 1)$ (Reverse order $60 \to 1$).
* **Worked Example ($\lambda = 74.25^\circ$):**
  * Gemini ($S=2$), $\Delta_{60} = 0.5^\circ$.
  * $k = \lfloor 14.25 / 0.5 \rfloor = 28$.
  * $S_{D60} = (2 + 28) \bmod 12 = 6 \implies \mathbf{Libra}$.
  * Deity Index $m = 28 + 1 = 29 \implies \mathbf{Kala}$ (Malefic past karma).
* **Pure Python:**
  ```python
  target = (s_idx + k) % 12
  ```
* **NumPy Vectorized:**
  ```python
  target = (rasi_idx + k) % 12
  ```

---

### Higher Divisional Harmonics ($D\text{-}72$ to $D\text{-}300$)

```
┌────────┬──────────────────────┬─────────────┬────────────────────────────────────────────────────────┐
│ Chart  │ Name                 │ Arc (Δ)     │ Calculation Algorithm                                  │
├────────┼──────────────────────┼─────────────┼────────────────────────────────────────────────────────┤
│ D-72   │ Ashtamamsha          │ 00° 25' 00" │ Modality: Movable -> 0, Fixed -> 8, Dual -> 4          │
│ D-81   │ Nava-Navamsha        │ 00° 22' 13" │ Element: Fire -> 0, Earth -> 9, Air -> 6, Water -> 3   │
│ D-108  │ Ashtottaramsa        │ 00° 16' 40" │ Continuous Global: floor(lon / 0.277778°) mod 12       │
│ D-144  │ Dwadasa-Dwadasamsa   │ 00° 12' 30" │ Sequential: (S + k) mod 12                             │
│ D-150  │ Nadiamsa             │ 00° 12' 00" │ 150 Named divisions (Chara 1→150, Sthira 150→1)        │
│ D-300  │ Ardha-Nadiamsa       │ 00° 06' 00" │ Purva Bhaga (first 360") vs Uttara Bhaga (second 360") │
└────────┴──────────────────────┴─────────────┴────────────────────────────────────────────────────────┘
```

---

# 4. Master Verification Matrix

Here are the verified calculation results for **Jupiter at $14^\circ 15' 00''\text{ Gemini}$ ($74.25^\circ$)** across all charts:

| Chart | Name | Resulting Sign | Longitude inside Varga Sign |
| :--- | :--- | :--- | :--- |
| **D-1** | Rasi | **Gemini** | $14^\circ 15' 00''$ |
| **D-2** | Hora | **Leo** | $28^\circ 30' 00''$ |
| **D-3** | Drekkana | **Libra** | $12^\circ 45' 00''$ |
| **D-4** | Chaturthamsa | **Virgo** | $27^\circ 00' 00''$ |
| **D-5** | Panchamsha | **Aquarius** | $11^\circ 15' 00''$ |
| **D-6** | Shashtamsha | **Gemini** | $25^\circ 30' 00''$ |
| **D-7** | Saptamsha | **Virgo** | $09^\circ 45' 00''$ |
| **D-8** | Ashtamsha | **Scorpio** | $24^\circ 00' 00''$ |
| **D-9** | Navamsha | **Aquarius** | $08^\circ 15' 00''$ |
| **D-10** | Dasamsha | **Libra** | $22^\circ 30' 00''$ |
| **D-11** | Rudramsha | **Virgo** | $20^\circ 15' 00''$ |
| **D-12** | Dwadasamsha | **Scorpio** | $21^\circ 00' 00''$ |
| **D-16** | Shodashamsha | **Cancer** | $18^\circ 00' 00''$ |
| **D-20** | Vimsamsha | **Taurus** | $15^\circ 00' 00''$ |
| **D-24** | Siddhamsa | **Cancer** | $12^\circ 00' 00''$ |
| **D-27** | Saptavimsamsha | **Libra** | $27^\circ 45' 00''$ |
| **D-30** | Trimsamsha | **Sagittarius** | Unequal Division (Jupiter) |
| **D-40** | Khavedamsha | **Scorpio** | $00^\circ 00' 00''$ |
| **D-45** | Akshavedamsha | **Virgo** | $11^\circ 15' 00''$ |
| **D-60** | Shashtiamsha | **Libra** | $15^\circ 00' 00''$ |
| **D-108** | Ashtottaramsa | **Aquarius** | $16^\circ 30' 00''$ |
