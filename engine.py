"""
engine.py — Vedic Astrology calculation engine
Uses 'ephem' library — simple pip install, works on Windows/Mac/Linux.
Lahiri ayanamsa, all 9 grahas, Vimshottari Dasha, Yoga detection.
No API key. No compilation required.
"""
import ephem
import math
import pytz
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# ── Zodiac ─────────────────────────────────────────────────────────────────────
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGNS_TAM = ['Mesha','Rishaba','Mithuna','Kataka','Simha','Kanni',
             'Thula','Vrischika','Dhanu','Makara','Kumbha','Meena']
SIGN_LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury',
              'Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
SIGN_ELEMENT = ['Fire','Earth','Air','Water','Fire','Earth',
                'Air','Water','Fire','Earth','Air','Water']
SIGN_QUALITY = ['Movable','Fixed','Dual','Movable','Fixed','Dual',
                'Movable','Fixed','Dual','Movable','Fixed','Dual']

NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula',
    'Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati',
]
NAK_LORDS    = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'] * 3
NAK_DEITIES  = [
    'Ashwini Kumaras','Yama','Agni','Prajapati','Soma','Rudra','Aditi',
    'Brihaspati','Sarpas','Pitrs','Aryaman','Bhaga','Savitar','Tvashtar',
    'Vayu','Indra-Agni','Mitra','Indra','Nirrti','Apas','Vishvedeva',
    'Vishnu','Vasus','Varuna','Aja Ekapada','Ahir Budhnya','Pushan',
]
NAK_SYMBOLS  = [
    'Horse head','Yoni','Razor','Cart','Deer head','Teardrop',
    'Quiver of arrows','Arrow','Coiled serpent','Royal throne','Fig tree',
    'Bed','Palm','Pearl','Coral bead',"Potter's wheel",'Lotus','Earring',
    'Elephant tusk','Elephant tusk','Elephant tusk','Ear','Drum',
    'Empty circle','Sword','Two-faced man','Fish',
]
NAK_QUALITY  = [
    'Laghu','Ugra','Mishra','Sthira','Mridu','Tikshna','Chara','Sthira',
    'Tikshna','Ugra','Laghu','Sthira','Laghu','Tikshna','Chara','Mishra',
    'Mridu','Tikshna','Tikshna','Ugra','Sthira','Laghu','Chara','Laghu',
    'Ugra','Sthira','Mridu',
]

DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {
    'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,
    'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17,
}

PLANET_SYMBOLS = {
    'Sun':'☉','Moon':'☽','Mars':'♂','Mercury':'☿','Jupiter':'♃',
    'Venus':'♀','Saturn':'♄','Rahu':'☊','Ketu':'☋',
}
PLANET_COLORS = {
    'Sun':'#e2a020','Moon':'#8ab4d4','Mars':'#d45050','Mercury':'#50a050',
    'Jupiter':'#c0842a','Venus':'#c060a0','Saturn':'#607080',
    'Rahu':'#6050b0','Ketu':'#b06040',
}

EXALT = {'Sun':0,'Moon':1,'Mars':9,'Mercury':5,'Jupiter':3,
         'Venus':11,'Saturn':6,'Rahu':1,'Ketu':7}
DEBIL = {'Sun':6,'Moon':7,'Mars':3,'Mercury':11,'Jupiter':9,
         'Venus':5,'Saturn':0,'Rahu':7,'Ketu':1}
OWN   = {'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[5,2],
         'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]}
FRIEND = {
    'Sun':   ['Moon','Mars','Jupiter'],
    'Moon':  ['Sun','Mercury'],
    'Mars':  ['Sun','Moon','Jupiter'],
    'Mercury':['Sun','Venus'],
    'Jupiter':['Sun','Moon','Mars'],
    'Venus': ['Mercury','Saturn'],
    'Saturn':['Mercury','Venus'],
}
YOGA_KARAKA = {
    'Aries':['Saturn'],'Taurus':['Saturn'],'Gemini':['Venus'],
    'Cancer':['Mars'],'Leo':['Mars'],'Virgo':['Venus'],
    'Libra':['Saturn'],'Scorpio':['Jupiter'],'Sagittarius':['Mars'],
    'Capricorn':['Venus'],'Aquarius':['Venus'],'Pisces':['Mars','Saturn'],
}

PLANET_NATURE = {
    'Sun':    'Atmakaraka — soul, authority, government, father, health, vitality.',
    'Moon':   'Manokaraka — mind, mother, emotions, public life, domestic happiness.',
    'Mars':   'Bhumikaraka — courage, land, siblings, energy, ambition, and conflict.',
    'Mercury':'Buddhikaraka — intellect, communication, trade, technology, analysis.',
    'Jupiter':'Putrakaraka — wisdom, dharma, children, fortune, teachers, expansion.',
    'Venus':  'Kalatrakaraka — relationships, beauty, luxury, arts, marital happiness.',
    'Saturn': 'Ayushkaraka — karma, discipline, longevity, service, delayed rewards.',
    'Rahu':   'Shadow planet — foreign influence, ambition, illusion, unconventional paths.',
    'Ketu':   'Shadow planet — spirituality, detachment, past karma, liberation.',
}
HOUSE_THEMES = [
    'Self, personality, health, physical body, and first impressions',
    'Wealth, speech, family, accumulated savings, and food',
    'Courage, siblings, short journeys, communication, and self-effort',
    'Home, mother, property, education, emotional security, and vehicles',
    'Intelligence, children, creativity, investments, and past-life merit',
    'Enemies, debts, diseases, daily work, service, and obstacles overcome',
    'Marriage, partnerships, business relationships, and foreign connections',
    'Longevity, transformation, inheritance, hidden matters, and sudden events',
    'Fortune, father, higher learning, long journeys, dharma, and pilgrimage',
    'Career, public life, status, authority, profession, and government',
    'Income, gains, elder siblings, social networks, hopes, and desires fulfilled',
    'Foreign lands, spiritual liberation, hidden expenditure, and moksha',
]
LAGNA_DESC = {
    'Aries':     'Courageous, energetic, pioneering, and independent. Natural leader with competitive drive. Impulsive but recovers fast.',
    'Taurus':    'Patient, sensual, artistic, and grounded. Strong aesthetic sense and love of comfort. Stubborn but deeply reliable.',
    'Gemini':    'Intellectually curious, communicative, adaptable, and witty. Restless mind that loves connecting ideas and people.',
    'Cancer':    'Nurturing, emotionally perceptive, intuitive, and devoted to family. Career linked to care, food, or protection.',
    'Leo':       'Confident, generous, creative, and dignified. Natural authority and dramatic flair. Seeks recognition.',
    'Virgo':     'Analytical, perfectionist, service-oriented, and detail-focused. Excellent problem-solver with high standards.',
    'Libra':     'Diplomatic, balanced, aesthetically gifted, and relationship-focused. Natural mediator. Struggles with indecisiveness.',
    'Scorpio':   'Intense, perceptive, transformative, powerfully secretive. Deep emotional intelligence. Regenerates after every setback.',
    'Sagittarius':'Philosophical, optimistic, adventurous, and truth-seeking. Loves learning and expansion. Can overextend.',
    'Capricorn': 'Disciplined, ambitious, patient, and structured. Rises slowly but solidly. Deeply responsible and hardworking.',
    'Aquarius':  'Humanitarian, original, unconventional, and intellectual. Community-focused visionary. Can be emotionally detached.',
    'Pisces':    'Compassionate, imaginative, spiritual, and deeply empathetic. Highly creative. Needs firm boundaries.',
}
RASI_DESC = {
    'Aries':  'Your inner world is impulsive, passionate, and fiercely independent.',
    'Taurus': 'Your inner world craves stability, beauty, and sensory comfort.',
    'Gemini': 'Your mind is restless, curious, constantly switching between ideas.',
    'Cancer': 'Your emotional core is sensitive, nurturing, and family-rooted.',
    'Leo':    'You feel emotions dramatically and seek warmth and creative expression.',
    'Virgo':  'Your inner world is analytical, discerning, and perfectionist.',
    'Libra':  'You seek harmony internally — conflict disturbs your balance deeply.',
    'Scorpio':'Your emotional depths are intense, private, and transformative.',
    'Sagittarius':'Your inner world is idealistic, adventurous, and philosophically restless.',
    'Capricorn':'You feel emotion through achievement — duty and responsibility are home.',
    'Aquarius':'Your inner world is detached, idealistic, and humanitarian.',
    'Pisces': 'Your emotional world is boundless, empathetic, and easily absorbs others.',
}
NAK_DESC = {
    'Ashwini':         'Swift beginnings, healing energy, and pioneering spirit.',
    'Bharani':         'Intense transformation, creativity, and willingness to carry burdens.',
    'Krittika':        'Sharp intellect, purifying fire, and penetrating clarity.',
    'Rohini':          'Sensual abundance, creative richness, and strong material desires.',
    'Mrigashira':      'Restless seeker — always searching for truth, beauty, or the perfect companion.',
    'Ardra':           'Storm and transformation — turbulence brings renewal and deep intelligence.',
    'Punarvasu':       "Return of prosperity — ruled by Aditi, the boundless cosmic mother. You always bounce back. Lord Rama's own birth star.",
    'Pushya':          'Nourishment, dharma, and spiritual devotion. The most auspicious nakshatra.',
    'Ashlesha':        'Mystical serpent energy — sharp, penetrating, psychic, and possessive.',
    'Magha':           'Royal throne — ancestral power, pride, and natural leadership.',
    'Purva Phalguni':  'Pleasure, relaxation, creativity, and generous enjoyment of life.',
    'Uttara Phalguni': 'Service with grace and responsibility. Fortunate and dignified.',
    'Hasta':           'Skillful hands — craft, healing, precision, and cleverness.',
    'Chitra':          'Brilliant architect of beauty — artistic, precise, and drawn to perfection.',
    'Swati':           'Independent, free-spirited, commercially gifted, and adaptable.',
    'Vishakha':        'Goal-oriented and purposeful — victory through intense focus.',
    'Anuradha':        'Devoted, loyal, and socially gifted. Deep friendships and organised systems.',
    'Jyeshtha':        'Elder wisdom, protective power, and hidden strength.',
    'Mula':            'Root investigation — gets to the foundation of everything.',
    'Purva Ashadha':   'Invincible energy, purification through water, and strong perseverance.',
    'Uttara Ashadha':  'Final victory — lasting success through righteousness.',
    'Shravana':        'Listening, learning, and connecting the world through knowledge.',
    'Dhanishtha':      'Wealth through community, rhythm, and abundance.',
    'Shatabhisha':     'Healing, mystery, and solitary spiritual power.',
    'Purva Bhadrapada':'Intense transformation — burning away impurity with otherworldly intelligence.',
    'Uttara Bhadrapada':'Depth, wisdom, and the patience of the sage.',
    'Revati':          "Journey's end — compassion, completion, and spiritual closure.",
}
DASHA_EFFECTS = {
    'Ketu':    'Spiritual detachment, past-karma clearing, interest in the occult. Health needs attention. Favours moksha-seeking.',
    'Venus':   'Material prosperity, luxury, relationships, and artistic success. One of the most comfortable Mahadashas.',
    'Sun':     'Authority, career recognition, government dealings, and father matters. Ego and health of eyes need care.',
    'Moon':    'Emotional experiences, travel, public life, and mother\'s health. Mood fluctuations are common.',
    'Mars':    'Energetic drive, ambition, property and real estate, and sibling themes. Accidents need care.',
    'Rahu':    'Intense ambition, foreign connections, and unexpected gains and losses. Unconventional paths and karmic intensity.',
    'Jupiter': 'Wisdom, dharma, children, higher education, fortune, and spiritual growth. Generally the most auspicious period.',
    'Saturn':  'Discipline, hard work, karmic debts repaid, and slow but permanent rewards. Integrity brings extraordinary gains.',
    'Mercury': 'Intellect, communication, trade, business, and analytical success. Writing and technology flourish.',
}
CAREER_INDICATORS = {
    'Aries':       ['Military, police, surgery, sports, engineering, entrepreneurship'],
    'Taurus':      ['Finance, banking, arts, music, luxury goods, real estate, agriculture'],
    'Gemini':      ['Communication, media, writing, teaching, IT, sales, marketing'],
    'Cancer':      ['Hospitality, healthcare, food, real estate, nursing, public service'],
    'Leo':         ['Government, politics, entertainment, management, education, leadership'],
    'Virgo':       ['Accounting, medicine, analysis, research, editing, data science'],
    'Libra':       ['Law, diplomacy, fashion, consulting, HR, design, relationships management'],
    'Scorpio':     ['Research, investigation, psychology, surgery, finance, occult sciences'],
    'Sagittarius': ['Law, philosophy, teaching, travel, publishing, religion, sports'],
    'Capricorn':   ['Administration, management, government, engineering, mining'],
    'Aquarius':    ['Technology, social work, innovation, science, aviation, IT'],
    'Pisces':      ['Medicine, arts, spiritual work, charity, film, photography, marine'],
}
REMEDY_DB = {
    'Sun':     ('Sunday',    'Om Suryaya Namah (108x)',       'Offer red flowers to rising sun. Donate wheat.'),
    'Moon':    ('Monday',    'Om Chandraya Namah (108x)',     'Offer white flowers and milk to Shiva. Fast on Mondays.'),
    'Mars':    ('Tuesday',   'Om Angarakaya Namah (108x)',    'Visit Hanuman temple. Offer red flowers. Donate red lentils.'),
    'Mercury': ('Wednesday', 'Om Budhaya Namah (108x)',       'Offer green leaves and moong dal. Feed parrots.'),
    'Jupiter': ('Thursday',  'Om Gurave Namah (108x)',        'Offer yellow flowers and turmeric. Donate yellow cloth.'),
    'Venus':   ('Friday',    'Om Shukraya Namah (108x)',      'Offer white flowers to Lakshmi. Light camphor lamp.'),
    'Saturn':  ('Saturday',  'Om Shanicharaya Namah (108x)',  'Feed sesame seeds to crows. Light sesame oil lamp.'),
    'Rahu':    ('Saturday',  'Om Rahave Namah (108x)',        'Visit Thirunageswaram temple. Offer blue/black flowers.'),
    'Ketu':    ('Tuesday',   'Om Ketave Namah (108x)',        'Visit Keezhperumpallam temple. Offer kusha grass.'),
}

# ── Lahiri ayanamsa ────────────────────────────────────────────────────────────
def lahiri_ayanamsa(year: float) -> float:
    """Lahiri ayanamsa accurate to ~0.02° for 1900–2100."""
    return 22.460148 + (year - 1900) * 0.013611 + (year - 1900)**2 * 0.000001

# ── Geocoding ──────────────────────────────────────────────────────────────────
def get_coordinates(place: str):
    geo = Nominatim(user_agent="vedic_astro_v3")
    loc = geo.geocode(place, timeout=10)
    if not loc:
        raise ValueError(
            f"Place not found: '{place}'. "
            "Try adding the country — e.g. 'Chennai, Tamil Nadu, India'."
        )
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=loc.latitude, lng=loc.longitude) or "Asia/Kolkata"
    return loc.latitude, loc.longitude, tz_str, loc.address

# ── Local → UTC ────────────────────────────────────────────────────────────────
def to_utc(dob: datetime, tz_str: str) -> datetime:
    tz = pytz.timezone(tz_str)
    return tz.localize(dob).astimezone(pytz.utc).replace(tzinfo=None)

# ── Get ecliptic longitude via ephem ──────────────────────────────────────────
def _ecl_lon(body_cls, obs, ayan):
    body = body_cls()
    body.compute(obs)
    ec = ephem.Ecliptic(body, epoch=obs.date)
    lon_trop = math.degrees(ec.lon) % 360
    lon_sid  = (lon_trop - ayan) % 360
    # retrograde check: compute 1 day later
    obs2 = ephem.Observer()
    obs2.lat = obs.lat; obs2.lon = obs.lon; obs2.epoch = obs.epoch
    obs2.date = ephem.Date(obs.date + 1)
    b2 = body_cls(); b2.compute(obs2)
    ec2 = ephem.Ecliptic(b2, epoch=obs2.date)
    lon2 = (math.degrees(ec2.lon) - ayan) % 360
    spd  = (lon2 - lon_sid + 360) % 360
    retro = (spd > 180)
    return lon_sid, retro

# ── Cast chart ─────────────────────────────────────────────────────────────────
def cast_chart(dob: datetime, place: str) -> dict:
    lat, lon, tz_str, full_address = get_coordinates(place)
    utc_dt = to_utc(dob, tz_str)

    year_frac = utc_dt.year + (utc_dt.timetuple().tm_yday - 1) / 365.25
    ayan = lahiri_ayanamsa(year_frac)

    obs = ephem.Observer()
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    obs.lat  = str(lat)
    obs.lon  = str(lon)
    obs.epoch = obs.date

    # Obliquity
    T   = (ephem.julian_date(obs.date) - 2451545.0) / 36525.0
    obl = 23.439291111 - 0.013004167 * T

    planet_classes = {
        'Sun': ephem.Sun, 'Moon': ephem.Moon, 'Mars': ephem.Mars,
        'Mercury': ephem.Mercury, 'Jupiter': ephem.Jupiter,
        'Venus': ephem.Venus, 'Saturn': ephem.Saturn,
    }
    planets = {}
    for name, cls in planet_classes.items():
        lon_sid, retro = _ecl_lon(cls, obs, ayan)
        si    = int(lon_sid // 30)
        nak_i = int(lon_sid / (360/27))
        pada  = int((lon_sid % (360/27)) / ((360/27)/4)) + 1
        planets[name] = {
            'longitude': lon_sid, 'sign': SIGNS[si], 'sign_tamil': SIGNS_TAM[si],
            'sign_index': si, 'degree': round(lon_sid % 30, 2),
            'symbol': PLANET_SYMBOLS[name], 'color': PLANET_COLORS[name],
            'retrograde': retro, 'nakshatra': NAKSHATRAS[nak_i], 'pada': pada,
        }

    # Rahu — mean ascending node of Moon via Meeus formula
    jd_val = ephem.julian_date(obs.date)
    T_val  = (jd_val - 2451545.0) / 36525.0
    rahu_trop = (125.04452 - 1934.136261*T_val + 0.0020708*T_val**2
                 + T_val**3/450000) % 360
    rahu_sid  = (rahu_trop - ayan) % 360
    r_si  = int(rahu_sid // 30)
    r_nak = int(rahu_sid / (360/27))
    planets['Rahu'] = {
        'longitude': rahu_sid, 'sign': SIGNS[r_si], 'sign_tamil': SIGNS_TAM[r_si],
        'sign_index': r_si, 'degree': round(rahu_sid % 30, 2),
        'symbol': '☊', 'color': PLANET_COLORS['Rahu'], 'retrograde': True,
        'nakshatra': NAKSHATRAS[r_nak],
        'pada': int((rahu_sid % (360/27)) / ((360/27)/4)) + 1,
    }

    # Ketu = Rahu + 180
    ketu_sid = (rahu_sid + 180) % 360
    k_si  = int(ketu_sid // 30)
    k_nak = int(ketu_sid / (360/27))
    planets['Ketu'] = {
        'longitude': ketu_sid, 'sign': SIGNS[k_si], 'sign_tamil': SIGNS_TAM[k_si],
        'sign_index': k_si, 'degree': round(ketu_sid % 30, 2),
        'symbol': '☋', 'color': PLANET_COLORS['Ketu'], 'retrograde': True,
        'nakshatra': NAKSHATRAS[k_nak],
        'pada': int((ketu_sid % (360/27)) / ((360/27)/4)) + 1,
    }

    # Lagna (whole-sign ascendant)
    ramc   = math.degrees(obs.sidereal_time())
    lat_r  = math.radians(lat)
    obl_r  = math.radians(obl)
    ramc_r = math.radians(ramc)
    asc_trop = math.degrees(math.atan2(
        math.cos(ramc_r),
        -(math.sin(ramc_r)*math.cos(obl_r) + math.tan(lat_r)*math.sin(obl_r))
    )) % 360
    asc_sid   = (asc_trop - ayan) % 360
    lagna_idx = int(asc_sid // 30)
    lagna_deg = round(asc_sid % 30, 2)

    # House positions
    for name in planets:
        h = ((planets[name]['sign_index'] - lagna_idx) % 12) + 1
        planets[name]['house'] = h

    # Dignity
    for name in planets:
        si = planets[name]['sign_index']
        if si == EXALT.get(name):
            planets[name]['dignity'] = 'Exalted ↑'
        elif si == DEBIL.get(name):
            planets[name]['dignity'] = 'Debilitated ↓'
        elif si in OWN.get(name, []):
            planets[name]['dignity'] = 'Own sign ★'
        elif SIGN_LORDS[si] in FRIEND.get(name, []):
            planets[name]['dignity'] = 'Friendly +'
        else:
            planets[name]['dignity'] = ''

    moon_lon = planets['Moon']['longitude']
    nak_idx  = int(moon_lon / (360/27))
    nak_frac = (moon_lon % (360/27)) / (360/27)
    pada     = int(nak_frac * 4) + 1

    return {
        'lat': lat, 'lon': lon, 'tz': tz_str, 'place': full_address,
        'ayanamsa': round(ayan, 4),
        'lagna': SIGNS[lagna_idx], 'lagna_tamil': SIGNS_TAM[lagna_idx],
        'lagna_index': lagna_idx, 'lagna_degree': lagna_deg,
        'lagna_lord': SIGN_LORDS[lagna_idx],
        'lagna_element': SIGN_ELEMENT[lagna_idx],
        'rasi': planets['Moon']['sign'], 'rasi_tamil': planets['Moon']['sign_tamil'],
        'rasi_lord': SIGN_LORDS[planets['Moon']['sign_index']],
        'nakshatra': NAKSHATRAS[nak_idx], 'nakshatra_index': nak_idx,
        'nakshatra_lord': NAK_LORDS[nak_idx],
        'nakshatra_deity': NAK_DEITIES[nak_idx],
        'nakshatra_symbol': NAK_SYMBOLS[nak_idx],
        'nakshatra_quality': NAK_QUALITY[nak_idx],
        'pada': pada, 'planets': planets,
        'yoga_karaka': YOGA_KARAKA.get(SIGNS[lagna_idx], []),
    }

# ── Dasha ──────────────────────────────────────────────────────────────────────
def compute_dasha(chart: dict, dob: datetime) -> dict:
    moon_lon = chart['planets']['Moon']['longitude']
    nak_idx  = chart['nakshatra_index']
    nak_lord = NAK_LORDS[nak_idx]
    nak_size = 360 / 27
    elapsed_frac = (moon_lon % nak_size) / nak_size
    start_idx = DASHA_ORDER.index(nak_lord)
    cursor = dob - timedelta(days=DASHA_YEARS[nak_lord] * elapsed_frac * 365.25)

    timeline = []
    for i in range(9):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        yrs  = DASHA_YEARS[lord]
        end  = cursor + timedelta(days=yrs * 365.25)
        timeline.append({
            'lord': lord, 'symbol': PLANET_SYMBOLS.get(lord,'★'),
            'start': cursor, 'end': end, 'years': yrs,
        })
        cursor = end

    now = datetime.now()
    current    = next((d for d in timeline if d['start'] <= now <= d['end']), timeline[0])
    ad_list    = _antardasha(current)
    current_ad = next((a for a in ad_list if a['start'] <= now <= a['end']), ad_list[0])

    return {
        'timeline': timeline, 'current': current,
        'antardasha_list': ad_list, 'current_antardasha': current_ad,
    }

def _antardasha(maha: dict) -> list:
    li = DASHA_ORDER.index(maha['lord'])
    total_days = (maha['end'] - maha['start']).days
    cursor, result = maha['start'], []
    for i in range(9):
        al   = DASHA_ORDER[(li + i) % 9]
        days = int(total_days * DASHA_YEARS[al] / 120)
        end  = cursor + timedelta(days=days)
        result.append({'lord': al, 'symbol': PLANET_SYMBOLS.get(al,'★'),
                       'start': cursor, 'end': end})
        cursor = end
    return result

# ── Yogas ──────────────────────────────────────────────────────────────────────
def detect_yogas(chart: dict) -> list:
    p     = chart['planets']
    lagna = chart['lagna_index']
    yogas = []

    def add(name, typ, desc):
        yogas.append({'name': name, 'type': typ, 'desc': desc})

    if p['Jupiter']['house'] in [1,4,7,10]:
        add('Gajakesari Yoga','Raja Yoga',
            'Jupiter in a kendra bestows wisdom, fame, prosperity, and long-lasting intellectual brilliance.')

    if p['Sun']['sign_index'] == p['Mercury']['sign_index']:
        add('Budhaditya Yoga','Intelligence Yoga',
            'Sun and Mercury conjunct — sharp intellect, eloquent communication, and professional recognition.')

    for nm in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        si = p[nm]['sign_index']
        if si == DEBIL.get(nm):
            lord = SIGN_LORDS[si]
            if p[lord]['house'] in [1,4,7,10]:
                add(f'Neecha Bhanga Raja Yoga ({nm})','Raja Yoga',
                    f'{nm} is debilitated but cancelled — {lord} is in a kendra. '
                    'Converts weakness to Raja Yoga: late-blooming but powerful.')

    if p['Moon']['house'] == p['Mars']['house']:
        add('Chandra-Mangala Yoga','Dhana Yoga',
            'Moon and Mars together — strong financial instincts, real estate gains, and business drive.')

    ll2  = SIGN_LORDS[(lagna + 1) % 12]
    ll11 = SIGN_LORDS[(lagna + 10) % 12]
    if p[ll2]['house'] in [1,2,5,9,10,11] and p[ll11]['house'] in [1,2,5,9,10,11]:
        add('Dhana Yoga','Wealth Yoga',
            f'2nd lord ({ll2}) and 11th lord ({ll11}) both well-placed — '
            'strong wealth accumulation through career and networks.')

    for yk in chart['yoga_karaka']:
        if p[yk]['house'] in [1,4,7,10,5,9]:
            add(f'Yoga Karaka — {yk}','Raja Yoga',
                f'{yk} is the Yoga Karaka for {chart["lagna"]} lagna, placed in an angular or trine house — '
                'the single most powerful career and wealth indicator in this chart.')

    r_lon = p['Rahu']['longitude']
    k_lon = p['Ketu']['longitude']
    lo, hi = sorted([r_lon, k_lon])
    non_nodes = [nm for nm in p if nm not in ('Rahu','Ketu')]
    if all(lo <= p[nm]['longitude'] <= hi for nm in non_nodes):
        add('Kaal Sarp Yoga','Dosha',
            'All planets between the Rahu-Ketu axis — karmic intensity and periodic setbacks. '
            'Dharmic living converts this to extraordinary late-life success.')
    else:
        add('No Kaal Sarp Yoga','Positive',
            'Planets distributed across both sides of the Rahu-Ketu axis — Kaal Sarp Yoga absent.')

    mh = p['Mars']['house']
    if mh in [1,2,4,7,8,12]:
        add('Mangal Dosha','Dosha',
            f'Mars in house {mh} — Mangal Dosha present. '
            'Partner chart matching and Kuja Dosha remedies recommended before marriage.')
    else:
        add('No Mangal Dosha','Positive',
            f'Mars in house {mh} — Mangal Dosha absent. No special marriage remedies needed from this angle.')

    return yogas