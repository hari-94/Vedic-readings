"""
engine.py — Vedic Astrology calculation engine
Uses 'ephem' library — simple pip install, works on Windows/Mac/Linux.
Lahiri ayanamsa, all 9 grahas, Vimshottari Dasha, Yoga detection.
No API key. No compilation required.
"""
import ephem
import math
import pytz
import time as _time
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder

# ── Offline city database — no API, no rate limits ────────────────────────────
_CITIES = {
    # Tamil Nadu
    'chennai':(13.0827,80.2707),'madras':(13.0827,80.2707),
    'coimbatore':(11.0168,76.9558),'madurai':(9.9252,78.1198),
    'tiruchirappalli':(10.7905,78.7047),'trichy':(10.7905,78.7047),
    'salem':(11.6643,78.1460),'tirunelveli':(8.7139,77.7567),
    'vellore':(12.9165,79.1325),'erode':(11.3410,77.7172),
    'thoothukudi':(8.7642,78.1348),'tuticorin':(8.7642,78.1348),
    'thanjavur':(10.7870,79.1378),'tiruppur':(11.1085,77.3411),
    'kanchipuram':(12.8185,79.6947),'cuddalore':(11.7447,79.7689),
    'nagapattinam':(10.7672,79.8449),'kumbakonam':(10.9617,79.3845),
    'dindigul':(10.3624,77.9695),'karur':(10.9601,78.0766),
    'rajapalayam':(9.4535,77.5564),'sivakasi':(9.4536,77.7979),
    'nagercoil':(8.1833,77.4119),'hosur':(12.7409,77.8253),
    'ooty':(11.4102,76.6950),'kodaikanal':(10.2381,77.4892),
    'pondicherry':(11.9416,79.8083),'puducherry':(11.9416,79.8083),
    'villupuram':(11.9401,79.4861),'tiruvannamalai':(12.2253,79.0747),
    'chidambaram':(11.3993,79.6931),'mayiladuthurai':(11.1019,79.6519),
    'sirkazhi':(11.2333,79.7500),'thirunageswaram':(10.9450,79.4192),
    'keezhperumpallam':(11.1667,79.7167),'tiruvarur':(10.7667,79.6333),
    'ariyalur':(11.1400,79.0800),'perambalur':(11.2330,78.8800),
    'dharmapuri':(12.1278,78.1580),'krishnagiri':(12.5186,78.2137),
    'namakkal':(11.2189,78.1674),'tirupathur':(12.4964,78.5704),
    'ranipet':(12.9310,79.3330),'tenkasi':(8.9600,77.3150),
    'virudhunagar':(9.5851,77.9630),'kallakurichi':(11.7380,78.9610),
    'tirupattur':(12.4964,78.5704),'ambur':(12.7920,78.7170),
    # Karnataka
    'bangalore':(12.9716,77.5946),'bengaluru':(12.9716,77.5946),
    'mysore':(12.2958,76.6394),'hubli':(15.3647,75.1240),
    'mangalore':(12.9141,74.8560),'belgaum':(15.8497,74.4977),
    'gulbarga':(17.3297,76.8343),'davangere':(14.4644,75.9218),
    'bellary':(15.1394,76.9214),'bijapur':(16.8302,75.7100),
    'shimoga':(13.9299,75.5681),'tumkur':(13.3379,77.1173),
    'raichur':(16.2120,77.3566),'bidar':(17.9133,77.5108),
    'udupi':(13.3409,74.7421),'hassan':(13.0068,76.0996),
    # Andhra Pradesh & Telangana
    'hyderabad':(17.3850,78.4867),'vijayawada':(16.5062,80.6480),
    'visakhapatnam':(17.6868,83.2185),'vizag':(17.6868,83.2185),
    'tirupati':(13.6288,79.4192),'guntur':(16.3067,80.4365),
    'nellore':(14.4426,79.9865),'kurnool':(15.8281,78.0373),
    'warangal':(17.9689,79.5941),'nizamabad':(18.6725,78.0941),
    'karimnagar':(18.4386,79.1288),'rajahmundry':(17.0005,81.8040),
    # Kerala
    'thiruvananthapuram':(8.5241,76.9366),'trivandrum':(8.5241,76.9366),
    'kochi':(9.9312,76.2673),'cochin':(9.9312,76.2673),
    'kozhikode':(11.2588,75.7804),'calicut':(11.2588,75.7804),
    'thrissur':(10.5276,76.2144),'kollam':(8.8932,76.6141),
    'palakkad':(10.7867,76.6548),'alappuzha':(9.4981,76.3388),
    'malappuram':(11.0730,76.0740),'kannur':(11.8745,75.3704),
    'kottayam':(9.5916,76.5222),'idukki':(9.9189,77.1025),
    # Maharashtra
    'mumbai':(19.0760,72.8777),'pune':(18.5204,73.8567),
    'nagpur':(21.1458,79.0882),'nashik':(19.9975,73.7898),
    'aurangabad':(19.8762,75.3433),'solapur':(17.6805,75.9064),
    'kolhapur':(16.7050,74.2433),'amravati':(20.9374,77.7796),
    'thane':(19.2183,72.9781),'navi mumbai':(19.0368,73.0158),
    # Gujarat
    'ahmedabad':(23.0225,72.5714),'surat':(21.1702,72.8311),
    'vadodara':(22.3072,73.1812),'rajkot':(22.3039,70.8022),
    'bhavnagar':(21.7645,72.1519),'jamnagar':(22.4707,70.0577),
    # North India
    'delhi':(28.6139,77.2090),'new delhi':(28.6139,77.2090),
    'jaipur':(26.9124,75.7873),'lucknow':(26.8467,80.9462),
    'kanpur':(26.4499,80.3319),'agra':(27.1767,78.0081),
    'varanasi':(25.3176,82.9739),'patna':(25.5941,85.1376),
    'allahabad':(25.4358,81.8463),'prayagraj':(25.4358,81.8463),
    'meerut':(28.9845,77.7064),'ghaziabad':(28.6692,77.4538),
    'noida':(28.5355,77.3910),'faridabad':(28.4089,77.3178),
    'gurgaon':(28.4595,77.0266),'gurugram':(28.4595,77.0266),
    'chandigarh':(30.7333,76.7794),'amritsar':(31.6340,74.8723),
    'ludhiana':(30.9010,75.8573),'jalandhar':(31.3260,75.5762),
    'bhopal':(23.2599,77.4126),'indore':(22.7196,75.8577),
    'jabalpur':(23.1815,79.9864),'gwalior':(26.2183,78.1828),
    'jodhpur':(26.2389,73.0243),'kota':(25.2138,75.8648),
    'ajmer':(26.4499,74.6399),'udaipur':(24.5854,73.7125),
    'kolkata':(22.5726,88.3639),'calcutta':(22.5726,88.3639),
    'siliguri':(26.7271,88.3953),'durgapur':(23.5204,87.3119),
    'ranchi':(23.3441,85.3096),'jamshedpur':(22.8046,86.2029),
    'bhubaneswar':(20.2961,85.8245),'cuttack':(20.4625,85.8830),
    'raipur':(21.2514,81.6296),'bilaspur':(22.0797,82.1391),
    'dehradun':(30.3165,78.0322),'haridwar':(29.9457,78.1642),
    'rishikesh':(30.0869,78.2676),'shimla':(31.1048,77.1734),
    'jammu':(32.7266,74.8570),'srinagar':(34.0837,74.7973),
    'leh':(34.1526,77.5771),'guwahati':(26.1445,91.7362),
    'imphal':(24.8170,93.9368),'shillong':(25.5788,91.8933),
    'aizawl':(23.7307,92.7173),'kohima':(25.6751,94.1086),
    'agartala':(23.8315,91.2868),'gangtok':(27.3389,88.6065),
    'panaji':(15.4909,73.8278),'goa':(15.2993,74.1240),
    'bareilly':(28.3670,79.4304),'moradabad':(28.8386,78.7733),
    'aligarh':(27.8974,78.0880),'gorakhpur':(26.7606,83.3732),
    # USA
    'new york':(40.7128,-74.0060),'los angeles':(34.0522,-118.2437),
    'chicago':(41.8781,-87.6298),'houston':(29.7604,-95.3698),
    'phoenix':(33.4484,-112.0740),'philadelphia':(39.9526,-75.1652),
    'san antonio':(29.4241,-98.4936),'san diego':(32.7157,-117.1611),
    'dallas':(32.7767,-96.7970),'san jose':(37.3382,-121.8863),
    'austin':(30.2672,-97.7431),'san francisco':(37.7749,-122.4194),
    'seattle':(47.6062,-122.3321),'denver':(39.7392,-104.9903),
    'washington':(38.9072,-77.0369),'boston':(42.3601,-71.0589),
    'las vegas':(36.1699,-115.1398),'miami':(25.7617,-80.1918),
    'atlanta':(33.7490,-84.3880),'portland':(45.5051,-122.6750),
    'minneapolis':(44.9778,-93.2650),'new orleans':(29.9511,-90.0715),
    'edwards':(39.6453,-106.9201),'vail':(39.6433,-106.3781),
    'columbus':(39.9612,-82.9988),'charlotte':(35.2271,-80.8431),
    'indianapolis':(39.7684,-86.1581),'nashville':(36.1627,-86.7816),
    'memphis':(35.1495,-90.0490),'louisville':(38.2527,-85.7585),
    'baltimore':(39.2904,-76.6122),'milwaukee':(43.0389,-87.9065),
    'albuquerque':(35.0844,-106.6504),'tucson':(32.2226,-110.9747),
    'fresno':(36.7378,-119.7871),'sacramento':(38.5816,-121.4944),
    'salt lake city':(40.7608,-111.8910),'reno':(39.5296,-119.8138),
    # UK
    'london':(51.5074,-0.1278),'birmingham':(52.4862,-1.8904),
    'leeds':(53.8008,-1.5491),'glasgow':(55.8642,-4.2518),
    'edinburgh':(55.9533,-3.1883),'manchester':(53.4808,-2.2426),
    'liverpool':(53.4084,-2.9916),'bristol':(51.4545,-2.5879),
    'sheffield':(53.3811,-1.4701),'leicester':(52.6369,-1.1398),
    # Europe
    'paris':(48.8566,2.3522),'berlin':(52.5200,13.4050),
    'madrid':(40.4168,-3.7038),'rome':(41.9028,12.4964),
    'amsterdam':(52.3676,4.9041),'brussels':(50.8503,4.3517),
    'vienna':(48.2082,16.3738),'zurich':(47.3769,8.5417),
    'stockholm':(59.3293,18.0686),'oslo':(59.9139,10.7522),
    'copenhagen':(55.6761,12.5683),'helsinki':(60.1699,24.9384),
    'warsaw':(52.2297,21.0122),'prague':(50.0755,14.4378),
    'budapest':(47.4979,19.0402),'bucharest':(44.4268,26.1025),
    'athens':(37.9838,23.7275),'lisbon':(38.7169,-9.1399),
    'barcelona':(41.3851,2.1734),'milan':(45.4654,9.1859),
    # Asia Pacific
    'tokyo':(35.6762,139.6503),'osaka':(34.6937,135.5023),
    'beijing':(39.9042,116.4074),'shanghai':(31.2304,121.4737),
    'hong kong':(22.3193,114.1694),'singapore':(1.3521,103.8198),
    'dubai':(25.2048,55.2708),'abu dhabi':(24.4539,54.3773),
    'riyadh':(24.7136,46.6753),'jeddah':(21.4858,39.1925),
    'bangkok':(13.7563,100.5018),'kuala lumpur':(3.1390,101.6869),
    'jakarta':(6.2088,106.8456),'manila':(14.5995,120.9842),
    'seoul':(37.5665,126.9780),'taipei':(25.0330,121.5654),
    'karachi':(24.8607,67.0011),'lahore':(31.5204,74.3587),
    'islamabad':(33.6844,73.0479),'dhaka':(23.8103,90.4125),
    'colombo':(6.9271,79.8612),'kathmandu':(27.7172,85.3240),
    # Oceania & Americas
    'sydney':(-33.8688,151.2093),'melbourne':(-37.8136,144.9631),
    'brisbane':(-27.4698,153.0251),'perth':(-31.9505,115.8605),
    'toronto':(43.6532,-79.3832),'vancouver':(49.2827,-123.1207),
    'montreal':(45.5017,-73.5673),'calgary':(51.0447,-114.0719),
    'cairo':(30.0444,31.2357),'johannesburg':(-26.2041,28.0473),
    'nairobi':(-1.2921,36.8219),'lagos':(6.5244,3.3792),
    'sao paulo':(-23.5505,-46.6333),'buenos aires':(-34.6037,-58.3816),
    'mexico city':(19.4326,-99.1332),'bogota':(4.7110,-74.0721),
    'lima':(-12.0464,-77.0428),'santiago':(-33.4489,-70.6693),
}

_TF = TimezoneFinder()
_geo_cache: dict = {}

def get_coordinates(place: str):
    """Offline city lookup — no API calls, no rate limits."""
    key = place.strip().lower()

    # Check cache first
    if key in _geo_cache:
        return _geo_cache[key]

    # Normalize: remove punctuation, split tokens
    import re
    tokens = re.sub(r'[,\.\-]', ' ', key).split()

    # 1. Exact match on full key
    if key in _CITIES:
        lat, lon = _CITIES[key]
        tz = _TF.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
        result = (lat, lon, tz, place.strip())
        _geo_cache[key] = result
        return result

    # 2. Match any token (longest token first to prioritize specificity)
    tokens_sorted = sorted(tokens, key=len, reverse=True)
    for token in tokens_sorted:
        if len(token) < 4:
            continue
        if token in _CITIES:
            lat, lon = _CITIES[token]
            tz = _TF.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
            result = (lat, lon, tz, place.strip())
            _geo_cache[key] = result
            return result

    # 3. Partial substring match
    for city_key, coords in _CITIES.items():
        for token in tokens_sorted:
            if len(token) >= 4 and (token in city_key or city_key in token):
                lat, lon = coords
                tz = _TF.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
                result = (lat, lon, tz, place.strip())
                _geo_cache[key] = result
                return result

    raise ValueError(
        f"City not found in offline database: '{place}'. "
        "Please enter coordinates manually using the expander below the form. "
        "Find your coordinates at latlong.net"
    )

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
