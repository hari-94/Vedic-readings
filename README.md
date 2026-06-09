# 🔯 Vedic Astrology Reading App
### South Indian Jathagam · No API key · Free to run

Full Vedic birth chart calculated with **Swiss Ephemeris** and **Lahiri ayanamsa** — entirely in Python. No Claude API key, no external astrology API, no subscriptions.

## What it calculates

- Lagna (ascendant), Rasi (moon sign), Janma Nakshatra, Pada
- All 9 Navagrahas — sign, house, nakshatra, dignity, retrograde status
- 12 houses (whole-sign system)
- Vimshottari Dasha — full timeline + current Mahadasha + Antardasha
- Yogas: Gajakesari, Budhaditya, Neecha Bhanga, Chandra-Mangala, Dhana, Yoga Karaka, Kaal Sarp, Mangal Dosha
- Remedies tailored to Lagna lord, Nakshatra lord, current Dasha lord
- 9 tabs of reading: Overview · Planets · Houses · Dasha · Career · Relationships · Yogas · Remedies · Summary

## Local setup

```bash
git clone https://github.com/YOUR_USERNAME/vedic-astrology-app
cd vedic-astrology-app
pip install -r requirements.txt
streamlit run app.py
```

No secrets.toml needed — no API key required.

## Deploy to Streamlit Community Cloud

1. Push repo to GitHub (public)
2. Go to share.streamlit.io → New app
3. Select repo, branch `main`, file `app.py`
4. Click **Deploy** — no secrets needed

## Project structure

```
vedic-astrology-app/
├── app.py              # Streamlit UI — 9 tabs, full reading
├── engine.py           # Astrology engine — Swiss Ephemeris calculations
├── requirements.txt    # pyswisseph, geopy, timezonefinder, pytz
├── .streamlit/
│   └── config.toml     # Dark theme
└── README.md
```

## How it works

1. Geocodes the birth place (lat/lon) using Geopy + Nominatim
2. Converts local birth time to UTC using TimezoneFinder + pytz
3. Calculates Julian Day Number
4. Calls Swiss Ephemeris (`pyswisseph`) with `SIDM_LAHIRI` sidereal mode
5. Computes all 9 planetary longitudes, Lagna (ASC), and Ketu
6. Maps longitudes to signs, houses (whole-sign), nakshatras, padas
7. Calculates Vimshottari Dasha from Moon nakshatra fraction
8. Detects yogas using classical Vedic rules
9. Renders everything in a 9-tab Streamlit interface
