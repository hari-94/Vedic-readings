"""
panchang.py — Daily timing calculator
- Chandrashtama days (next 90 days)
- Today's good hours (Abhijit, planet hora, lucky windows)
- Rahu Kalam, Yamagandam, Gulika Kalam
- Moon sign of the day and its effect on Rasi
"""
import ephem
import math
import pytz
from datetime import datetime, timedelta, date

# ── Constants ──────────────────────────────────────────────────────────────────
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGNS_TAM = ['Mesha','Rishaba','Mithuna','Kataka','Simha','Kanni',
             'Thula','Vrischika','Dhanu','Makara','Kumbha','Meena']

NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula',
    'Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati',
]
NAK_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'] * 3

# Rahu Kalam slot number (1–8) for each day Sun=0 .. Sat=6
# Day is split into 8 equal parts from sunrise to sunset
RAHU_SLOT   = [8, 2, 7, 5, 6, 4, 3]   # Sun Mon Tue Wed Thu Fri Sat
YAMA_SLOT   = [5, 4, 3, 2, 1, 7, 6]
GULIKA_SLOT = [7, 6, 5, 4, 3, 2, 1]

# Planet hora order (Chaldean): Sun=0 Mon=1 Tue=2 Wed=3 Thu=4 Fri=5 Sat=6
# Each day starts with its ruling planet
DAY_PLANETS = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
CHALDEAN    = ['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon']
# hour 1 of each weekday is ruled by:
HORA_START  = {0:'Sun',1:'Moon',2:'Mars',3:'Mercury',4:'Jupiter',5:'Venus',6:'Saturn'}

PLANET_SYMBOLS = {
    'Sun':'☉','Moon':'☽','Mars':'♂','Mercury':'☿',
    'Jupiter':'♃','Venus':'♀','Saturn':'♄','Rahu':'☊','Ketu':'☋',
}

# Moon sign relationship to natal Rasi: 1–12 positions
MOON_TRANSIT_EFFECTS = {
    1:  ('Janma',      'neutral',  'Moon in your own Rasi. Mixed — introspective, cautious. Avoid new starts.'),
    2:  ('Sampat',     'good',     'Moon in 2H from Rasi. Wealth and food gains. Good for financial dealings.'),
    3:  ('Vipat',      'bad',      'Moon in 3H. Danger, accidents, obstacles. Travel with care.'),
    4:  ('Kshema',     'good',     'Moon in 4H. Comfort, prosperity, and domestic happiness. Auspicious.'),
    5:  ('Pratyak',    'bad',      'Moon in 5H. Obstacles and reversals. Avoid starting new ventures.'),
    6:  ('Sadhana',    'good',     'Moon in 6H. Success over enemies, good health. Auspicious for work.'),
    7:  ('Naidhana',   'bad',      'Moon in 7H. Danger, loss, disputes. Exercise caution in all dealings.'),
    8:  ('Mitra',      'good',     'Moon in 8H. Friendly, supportive energy. Good for partnerships.'),
    9:  ('Parama Mitra','good',    'Moon in 9H. Best position. Fortune, dharma, blessings. Highly auspicious.'),
    10: ('Karma',      'neutral',  'Moon in 10H. Career activity. Moderate — ongoing work is fine.'),
    11: ('Labha',      'good',     'Moon in 11H. Gains, income, and wishes fulfilled. Very auspicious.'),
    12: ('Vyaya',      'bad',      'Moon in 12H. Expenditure, losses, and fatigue. Rest and conserve energy.'),
}

# Chandrashtama = Moon in 8th from Rasi → position 8 in above table
# But classical Tamil astrology also counts 16th and 22nd nakshatras as janma-related

GOOD_ACTIVITIES = {
    'good':     ['Starting new projects','Business meetings','Job interviews',
                 'Property dealings','Marriage discussions','Travel','Investments','Medical procedures'],
    'neutral':  ['Routine work','Follow-ups','Meetings already scheduled','Study','Meditation'],
    'bad':      ['Avoid new starts','No major financial decisions','Postpone surgery if possible',
                 'No important travel','No signing contracts','Rest and introspect'],
}

# ── Lahiri ayanamsa ────────────────────────────────────────────────────────────
def _lahiri(year: float) -> float:
    return 22.460148 + (year - 1900) * 0.013611 + (year - 1900)**2 * 0.000001

# ── Moon sidereal longitude for a UTC datetime ────────────────────────────────
def _moon_sid_lon(utc_dt: datetime) -> float:
    obs = ephem.Observer()
    obs.date  = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    obs.epoch = obs.date
    m = ephem.Moon(); m.compute(obs)
    ec = ephem.Ecliptic(m, epoch=obs.date)
    year_frac = utc_dt.year + (utc_dt.timetuple().tm_yday - 1) / 365.25
    ayan = _lahiri(year_frac)
    return (math.degrees(ec.lon) - ayan) % 360

# ── Sunrise / Sunset (local naive datetime) ───────────────────────────────────
def get_sunrise_sunset(for_date: date, lat: float, lon: float, tz_str: str):
    obs = ephem.Observer()
    obs.lat     = str(lat)
    obs.lon     = str(lon)
    obs.horizon = '-0:34'
    obs.date    = for_date.strftime('%Y/%m/%d 12:00:00')
    sun = ephem.Sun()
    try:
        rise_e = obs.next_rising(sun,  start=obs.date - 0.6)
        set_e  = obs.next_setting(sun, start=rise_e)
    except Exception:
        tz_obj = pytz.timezone(tz_str)
        base   = datetime.combine(for_date, datetime.min.time())
        return base.replace(hour=6), base.replace(hour=18)
    tz_obj   = pytz.timezone(tz_str)
    rise_loc = pytz.utc.localize(ephem.Date(rise_e).datetime()).astimezone(tz_obj).replace(tzinfo=None)
    set_loc  = pytz.utc.localize(ephem.Date(set_e).datetime()).astimezone(tz_obj).replace(tzinfo=None)
    return rise_loc, set_loc

# ── Kalam timings ─────────────────────────────────────────────────────────────
def get_kalam_times(for_date: date, lat: float, lon: float, tz_str: str) -> dict:
    sunrise, sunset = get_sunrise_sunset(for_date, lat, lon, tz_str)
    day_secs  = (sunset - sunrise).total_seconds()
    slot_secs = day_secs / 8

    # Python weekday: Mon=0 … Sun=6  →  Sun=0 … Sat=6
    dow_py  = datetime.combine(for_date, datetime.min.time()).weekday()
    dow_sun = (dow_py + 1) % 7

    def slot(n):
        s = sunrise + timedelta(seconds=slot_secs * (n - 1))
        e = s + timedelta(seconds=slot_secs)
        return s, e

    rk_s, rk_e = slot(RAHU_SLOT[dow_sun])
    yg_s, yg_e = slot(YAMA_SLOT[dow_sun])
    gk_s, gk_e = slot(GULIKA_SLOT[dow_sun])

    return {
        'sunrise':  sunrise,
        'sunset':   sunset,
        'rahu_kalam':   (rk_s, rk_e),
        'yamagandam':   (yg_s, yg_e),
        'gulika_kalam': (gk_s, gk_e),
        'day_lord':     DAY_PLANETS[dow_py],
        'dow_sun':      dow_sun,
    }

# ── Abhijit Muhurta (midday auspicious window) ────────────────────────────────
def get_abhijit(for_date: date, lat: float, lon: float, tz_str: str):
    """Abhijit = 24 minutes centred on solar noon. Most auspicious daily window."""
    sunrise, sunset = get_sunrise_sunset(for_date, lat, lon, tz_str)
    noon = sunrise + (sunset - sunrise) / 2
    return noon - timedelta(minutes=24), noon + timedelta(minutes=24)

# ── Planet hora for a given datetime ─────────────────────────────────────────
def get_planet_hora(dt: datetime, lat: float, lon: float, tz_str: str) -> str:
    """Return the planet ruling the current hora (1-hour window)."""
    sunrise, _ = get_sunrise_sunset(dt.date(), lat, lon, tz_str)
    dow_py  = dt.weekday()
    dow_sun = (dow_py + 1) % 7
    start_planet = HORA_START[dow_sun]
    start_idx = CHALDEAN.index(start_planet)
    elapsed_hours = max(0, (dt - sunrise).total_seconds() / 3600)
    hora_num = int(elapsed_hours) % 24
    hora_planet = CHALDEAN[(start_idx + hora_num) % 7]
    return hora_planet

# ── Today's moon sign and effect on natal Rasi ───────────────────────────────
def get_today_moon(lat: float, lon: float, tz_str: str):
    tz_obj  = pytz.timezone(tz_str)
    now_utc = datetime.utcnow()
    now_loc = pytz.utc.localize(now_utc).astimezone(tz_obj).replace(tzinfo=None)
    lon_sid = _moon_sid_lon(now_utc)
    sign_idx = int(lon_sid // 30)
    nak_idx  = int(lon_sid / (360/27))
    return {
        'sign':      SIGNS[sign_idx],
        'sign_tamil':SIGNS_TAM[sign_idx],
        'sign_index':sign_idx,
        'degree':    round(lon_sid % 30, 2),
        'nakshatra': NAKSHATRAS[nak_idx],
        'nak_lord':  NAK_LORDS[nak_idx],
        'time_local':now_loc,
    }

def moon_effect_on_rasi(moon_sign_idx: int, rasi_idx: int) -> dict:
    pos = ((moon_sign_idx - rasi_idx) % 12) + 1
    name, quality, desc = MOON_TRANSIT_EFFECTS[pos]
    activities = GOOD_ACTIVITIES[quality]
    return {
        'position': pos,
        'name': name,
        'quality': quality,
        'desc': desc,
        'activities': activities,
        'is_chandrashtama': pos == 8,
    }

# ── Chandrashtama days (next N days) ─────────────────────────────────────────
def get_chandrashtama_days(rasi_idx: int, lat: float, lon: float,
                            tz_str: str, days: int = 90) -> list:
    """
    Scan the next `days` days and return list of Chandrashtama windows.
    Each entry: {start, end, nakshatra, nak_lord}
    Chandrashtama = Moon in 8th sign from natal Rasi.
    """
    chandra_sign = (rasi_idx + 7) % 12
    tz_obj = pytz.timezone(tz_str)
    now_utc = datetime.utcnow()
    results = []
    in_chandra = False
    entry_time = None
    entry_nak  = None

    # Scan every 2 hours (Moon moves ~1° per hour, sign = 30°)
    for h in range(days * 24 // 2 + 1):
        utc_check = now_utc + timedelta(hours=h * 2)
        lon_sid   = _moon_sid_lon(utc_check)
        cur_sign  = int(lon_sid // 30)
        nak_idx   = int(lon_sid / (360/27))

        if cur_sign == chandra_sign and not in_chandra:
            in_chandra = True
            entry_time = utc_check
            entry_nak  = NAKSHATRAS[nak_idx]

        elif cur_sign != chandra_sign and in_chandra:
            in_chandra = False
            exit_time  = utc_check
            # Convert to local
            start_loc = pytz.utc.localize(entry_time).astimezone(tz_obj).replace(tzinfo=None)
            end_loc   = pytz.utc.localize(exit_time).astimezone(tz_obj).replace(tzinfo=None)
            results.append({
                'start':    start_loc,
                'end':      end_loc,
                'nakshatra':entry_nak,
                'nak_lord': NAK_LORDS[NAKSHATRAS.index(entry_nak)] if entry_nak in NAKSHATRAS else '',
                'sign':     SIGNS[chandra_sign],
            })

    return results

# ── Good windows for a day ────────────────────────────────────────────────────
def get_good_windows(for_date: date, lat: float, lon: float,
                     tz_str: str, rasi_idx: int, lagna_lord: str) -> list:
    """Return ranked list of auspicious windows for the day."""
    kalams = get_kalam_times(for_date, lat, lon, tz_str)
    sunrise, sunset = kalams['sunrise'], kalams['sunset']
    ab_start, ab_end = get_abhijit(for_date, lat, lon, tz_str)
    rk_s, rk_e = kalams['rahu_kalam']
    yg_s, yg_e = kalams['yamagandam']
    gk_s, gk_e = kalams['gulika_kalam']

    day_lord    = kalams['day_lord']
    dow_sun     = kalams['dow_sun']
    day_secs    = (sunset - sunrise).total_seconds()
    slot_secs   = day_secs / 8

    # Hora windows for the whole day
    start_idx = CHALDEAN.index(HORA_START[dow_sun])
    hora_windows = []
    for i in range(16):  # cover day and some night
        planet = CHALDEAN[(start_idx + i) % 7]
        h_start = sunrise + timedelta(seconds=3600 * i)
        h_end   = h_start + timedelta(seconds=3600)
        if h_start >= sunset:
            break
        hora_windows.append({'planet': planet, 'start': h_start, 'end': h_end})

    # Inauspicious windows set
    bad_windows = [(rk_s, rk_e), (yg_s, yg_e), (gk_s, gk_e)]

    def overlaps_bad(s, e):
        for bs, be in bad_windows:
            if s < be and e > bs:
                return True
        return False

    windows = []

    # Abhijit — always good if not in bad window
    if not overlaps_bad(ab_start, ab_end):
        windows.append({
            'label':   'Abhijit Muhurta',
            'start':   ab_start,
            'end':     ab_end,
            'quality': 'best',
            'reason':  'Solar noon window — most universally auspicious time of any day.',
            'icon':    '☀️',
        })

    # Lagna lord hora + Nakshatra lord hora
    LAGNA_FRIENDLY = {
        'Sun':    ['Sun','Moon','Mars','Jupiter'],
        'Moon':   ['Sun','Moon','Jupiter','Mercury'],
        'Mars':   ['Sun','Moon','Mars','Jupiter'],
        'Mercury':['Sun','Mercury','Venus'],
        'Jupiter':['Sun','Moon','Mars','Jupiter'],
        'Venus':  ['Mercury','Venus','Saturn'],
        'Saturn': ['Mercury','Venus','Saturn'],
    }
    friendly = LAGNA_FRIENDLY.get(lagna_lord, [lagna_lord])

    for hw in hora_windows:
        if hw['planet'] in friendly and not overlaps_bad(hw['start'], hw['end']):
            windows.append({
                'label':   f"{PLANET_SYMBOLS.get(hw['planet'],'')} {hw['planet']} Hora",
                'start':   hw['start'],
                'end':     hw['end'],
                'quality': 'good',
                'reason':  f"{hw['planet']} hora is friendly to your {lagna_lord} lagna — good for new starts and decisions.",
                'icon':    '🌟',
            })

    # Sort by start time, deduplicate, cap at 6
    windows.sort(key=lambda x: x['start'])
    seen = set()
    unique = []
    for w in windows:
        key = w['start'].strftime('%H:%M')
        if key not in seen:
            seen.add(key)
            unique.append(w)

    return unique[:8]

# ── Weekly Chandrashtama summary ──────────────────────────────────────────────
def get_weekly_overview(rasi_idx: int, lat: float, lon: float,
                         tz_str: str) -> list:
    """Return day-by-day quality for next 14 days."""
    tz_obj  = pytz.timezone(tz_str)
    today   = datetime.now(pytz.timezone(tz_str)).date()
    result  = []
    for d in range(14):
        check_date = today + timedelta(days=d)
        # Moon at noon of this day
        noon_loc = datetime.combine(check_date, datetime.min.time()).replace(hour=12)
        noon_utc = tz_obj.localize(noon_loc).astimezone(pytz.utc).replace(tzinfo=None)
        lon_sid  = _moon_sid_lon(noon_utc)
        sign_idx = int(lon_sid // 30)
        nak_idx  = int(lon_sid / (360/27))
        effect   = moon_effect_on_rasi(sign_idx, rasi_idx)
        result.append({
            'date':      check_date,
            'day':       check_date.strftime('%a'),
            'sign':      SIGNS[sign_idx],
            'sign_tamil':SIGNS_TAM[sign_idx],
            'nakshatra': NAKSHATRAS[nak_idx],
            'quality':   effect['quality'],
            'name':      effect['name'],
            'desc':      effect['desc'],
            'position':  effect['position'],
            'is_chandrashtama': effect['is_chandrashtama'],
        })
    return result
