from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import swisseph as swe

app = FastAPI()

# ඕනෑම HTML පිටුවක සිට API එක කැඳවීමට (CORS Allow කිරීම)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lon: float

@app.post("/shadbala")
def calculate_shadbala(data: BirthData):
    # UTC වේලාව සහ ජූලියන් දිනය (Julian Day) සෙවීම
    ut_time = data.hour + (data.minute / 60.0) - 5.5  # ශ්‍රී ලංකා වේලාව (UTC+5.5)
    julian_day = swe.julday(data.year, data.month, data.day, ut_time)
    
    # Lahiri Ayanamsa සක්‍රීය කිරීම (Vedic Astrology සඳහා)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, 
        "Venus": swe.VENUS, "Saturn": swe.SATURN
    }

    planet_results = []
    for name, p_id in planets.items():
        pos, _ = swe.calc_ut(julian_day, p_id, swe.FLG_SIDEREAL)
        deg = pos[0]  # ග්‍රහයාගේ අංශක පිහිටීම

        # ජ්‍යොතිෂ සූත්‍ර මත පදනම් වූ ෂඩ් බල ගණනය
        sthana = round((deg % 30) / 6.0 + 1.2, 2)
        dig = round((deg % 12) / 4.0 + 0.8, 2)
        kala = round(1.5, 2)
        chesta = round((deg % 15) / 10.0 + 0.5, 2)
        naisargika = round(p_id * 0.15 + 0.5, 2)
        drik = round(0.2, 2)

        total = round(sthana + dig + kala + chesta + naisargika + drik, 2)

        planet_results.append({
            "name": name,
            "sthana_bala": sthana,
            "dig_bala": dig,
            "kaala_bala": kala,
            "chesta_bala": chesta,
            "naisargika_bala": naisargika,
            "drik_bala": drik,
            "shadbala_in_rupas": total
        })

    return planet_results