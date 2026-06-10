"""
app.py — Vedic Astrology Reading App
Full chart calculation using Swiss Ephemeris (Lahiri ayanamsa).
No API key required — all astrology logic is built-in.
Supports English and Tamil (தமிழ்) language toggle.
"""
import streamlit as st
from datetime import datetime, date, time
from engine import (
    cast_chart, compute_dasha, detect_yogas,
    SIGNS, PLANET_SYMBOLS, PLANET_COLORS,
    LAGNA_DESC, RASI_DESC, NAK_DESC, DASHA_EFFECTS,
    CAREER_INDICATORS, REMEDY_DB, HOUSE_THEMES,
    DASHA_ORDER, DASHA_YEARS, NAK_DEITIES, NAK_SYMBOLS,
    SIGN_LORDS, SIGN_ELEMENT, SIGN_QUALITY,
)
from panchang import (
    get_kalam_times, get_abhijit, get_today_moon, moon_effect_on_rasi,
    get_chandrashtama_days, get_good_windows, get_weekly_overview,
)

# ── Tamil translations ─────────────────────────────────────────────────────────
TAM = {
    # App title
    "app_title":        "வேத ஜோதிட வாசிப்பு",
    "app_sub":          "தென்னிந்திய ஜாதகம் · சுவிஸ் எபிமெரிஸ் · லாஹிரி அயனாம்சம்",
    # Form labels
    "full_name":        "முழு பெயர்",
    "dob":              "பிறந்த தேதி",
    "tob":              "பிறந்த நேரம் (HH:MM)",
    "pob":              "பிறந்த இடம்",
    "gender":           "பாலினம்",
    "generate":         "✨  ஜாதகம் உருவாக்கு",
    "new_reading":      "🔄  புதிய ஜாதகம்",
    "select":           "தேர்ந்தெடு",
    "male":             "ஆண்",
    "female":           "பெண்",
    "other":            "மற்றவை",
    "tob_hint":         "பிறந்த நேரம் லக்னம் துல்லியத்தை மேம்படுத்துகிறது. தெரியாவிட்டால் 12:00 பயன்படுத்தவும்.",
    "casting":          "சுவிஸ் எபிமெரிஸ் மூலம் ஜாதகம் வரைகிறது…",
    # Tab names
    "tab_overview":     "🌟 கண்ணோட்டம்",
    "tab_planets":      "🪐 கிரகங்கள்",
    "tab_houses":       "🏠 பாவங்கள்",
    "tab_dasha":        "⏳ தசை",
    "tab_career":       "💼 தொழில்",
    "tab_relationships":"💞 திருமணம்",
    "tab_yogas":        "⚖️ யோகங்கள்",
    "tab_remedies":     "🧿 பரிகாரங்கள்",
    "tab_panchang":     "📅 பஞ்சாங்கம்",
    "tab_summary":      "📊 சுருக்கம்",
    # Section titles
    "sec_lagna":        "லக்னம் — ஆளுமை",
    "sec_rasi":         "ராசி — சந்திர ராசி",
    "sec_nakshatra":    "ஜன்ம நட்சத்திரம்",
    "sec_star_profile": "நட்சத்திர விவரம்",
    "sec_nak_meaning":  "நட்சத்திர பொருள்",
    "sec_chart":        "ராசி சக்கரம் — தென்னிந்திய வடிவம்",
    "sec_planets":      "நவகிரக நிலைகள் (லாஹிரி சைடீரியல்)",
    "sec_houses":       "12 பாவங்கள் — முழு ராசி முறை",
    "sec_dasha_curr":   "தற்போதைய தசை வாசிப்பு",
    "sec_dasha_antar":  "தற்போதைய அந்தர் தசை",
    "sec_dasha_full":   "முழு விம்சோத்தரி தசை கோடு",
    "sec_career":       "தொழில் & செல்வ விதி",
    "sec_career_fields":"உங்கள் லக்னத்திற்கான சிறந்த தொழில் துறைகள்",
    "sec_career_yk":    "யோக காரகன் & தொழில் செல்வம்",
    "sec_wealth_lords": "செல்வ பாவ அதிபதிகள்",
    "sec_marriage":     "திருமணம் & கூட்டாண்மை",
    "sec_venus":        "சுக்கிரன் — திருமணத்தின் இயற்கை காரகன்",
    "sec_spouse":       "வாழ்க்கைத்துணை குறிகாட்டிகள்",
    "sec_yogas":        "யோகங்கள் & தோஷங்கள்",
    "sec_remedies":     "உங்கள் ஜாதகத்திற்கான பரிகாரங்கள்",
    "sec_daily":        "அன்றாட பரிகாரங்கள்",
    "sec_today_moon":   "இன்றைய சந்திரன்",
    "sec_kalam":        "இன்றைய கால நேரங்கள் — புதிய தொடக்கங்களை தவிர்க்கவும்",
    "sec_good_windows": "இன்றைய சிறந்த நேரங்கள்",
    "sec_14day":        "உங்கள் ராசிக்கான 14 நாள் சந்திர நாட்காட்டி",
    "sec_chandra":      "சந்திராஷ்டம நாட்கள் — அடுத்த 90 நாட்கள்",
    "sec_summary":      "முழு ஜாதக சுருக்கம்",
    "sec_all_planets":  "அனைத்து கிரக நிலைகள்",
    # Labels
    "lagna_lbl":        "லக்னம் (உதயம்)",
    "rasi_lbl":         "ராசி (சந்திர ராசி)",
    "nakshatra_lbl":    "ஜன்ம நட்சத்திரம்",
    "pada_lbl":         "நட்சத்திர பாதம்",
    "lagna_lord_lbl":   "லக்னாதிபதி",
    "nak_lord_lbl":     "நட்சத்திர அதிபதி",
    "element_lbl":      "தத்துவம்",
    "ayanamsa_lbl":     "லாஹிரி அயனாம்சம்",
    "deity_lbl":        "தேவதை",
    "symbol_lbl":       "சின்னம்",
    "lord_lbl":         "அதிபதி",
    "quality_lbl":      "குணம்",
    "curr_dasha_lbl":   "தற்போதைய தசை",
    "started_lbl":      "தொடங்கியது",
    "ends_lbl":         "முடிவு",
    "duration_lbl":     "கால அளவு",
    "upcoming_lbl":     "வரும் தசை",
    "10h_sign_lbl":     "10ம் பாவ ராசி",
    "10h_lord_lbl":     "10ம் பாவ அதிபதி",
    "planets_10h_lbl":  "10ம் பாவ கிரகங்கள்",
    "7h_sign_lbl":      "7ம் பாவ ராசி",
    "7h_lord_lbl":      "7ம் பாவ அதிபதி",
    "7h_placed_lbl":    "நிலை",
    "7h_planets_lbl":   "7ம் பாவ கிரகங்கள்",
    "sunrise_lbl":      "சூர்யோதயம்",
    "sunset_lbl":       "சூர்யாஸ்தமனம்",
    "day_lord_lbl":     "வார அதிபதி",
    "house_lbl":        "பாவம்",
    "sign_lbl":         "ராசி",
    "degree_lbl":       "பாகை",
    "planet_lbl":       "கிரகம்",
    # Planet names in Tamil
    "Sun":     "சூரியன்", "Moon":    "சந்திரன்", "Mars":    "செவ்வாய்",
    "Mercury": "புதன்",   "Jupiter": "குரு",     "Venus":   "சுக்கிரன்",
    "Saturn":  "சனி",     "Rahu":    "ராகு",     "Ketu":    "கேது",
    # Kalam names
    "rahu_kalam":    "ராகு காலம்",
    "yamagandam":    "யமகண்டம்",
    "gulika_kalam":  "குளிகை காலம்",
    "abhijit":       "அபிஜித் முகூர்த்தம்",
    # Chandrashtama
    "chandrashtama": "சந்திராஷ்டமம்",
    "active_now":    "இப்போது செயலில்",
    "no_periods":    "அடுத்த 90 நாட்களில் சந்திராஷ்டம காலம் இல்லை.",
    # Misc
    "house":         "பாவம்",
    "empty":         "காலி",
    "retrograde":    "வக்ர",
    "asc_label":     "லக்னம் ★",
    "new_reading_btn": "புதிய வாசிப்பு",
    "yoga_karaka":   "யோக காரகன்",
    "none":          "இல்லை",
    "best_time":     "சிறந்த நேரம்",
    "years":         "ஆண்டுகள்",
    "duration_h":    "காலம்",
}

ENG = {
    "app_title":        "Vedic Astrology Reading",
    "app_sub":          "South Indian Jathagam · Swiss Ephemeris · Lahiri ayanamsa · No API key required",
    "full_name":        "Full name",
    "dob":              "Date of birth",
    "tob":              "Time of birth (HH:MM 24h)",
    "pob":              "Place of birth",
    "gender":           "Gender",
    "generate":         "✨  Generate reading",
    "new_reading":      "🔄  New reading",
    "select":           "Select",
    "male":             "Male",
    "female":           "Female",
    "other":            "Other",
    "tob_hint":         "Time of birth significantly improves Lagna accuracy. Use 12:00 if unknown.",
    "casting":          "Casting chart with Swiss Ephemeris…",
    "tab_overview":     "🌟 Overview",
    "tab_planets":      "🪐 Planets",
    "tab_houses":       "🏠 Houses",
    "tab_dasha":        "⏳ Dasha",
    "tab_career":       "💼 Career",
    "tab_relationships":"💞 Relationships",
    "tab_yogas":        "⚖️ Yogas",
    "tab_remedies":     "🧿 Remedies",
    "tab_panchang":     "📅 Panchang",
    "tab_summary":      "📊 Summary",
    "sec_lagna":        "Lagna — ascendant personality",
    "sec_rasi":         "Rasi — moon sign",
    "sec_nakshatra":    "Janma nakshatra",
    "sec_star_profile": "Star profile",
    "sec_nak_meaning":  "Nakshatra meaning",
    "sec_chart":        "Rasi chart — South Indian style (fixed signs)",
    "sec_planets":      "Navagraha placements (Lahiri sidereal)",
    "sec_houses":       "12 houses — whole-sign system from lagna",
    "sec_dasha_curr":   "Current dasha reading",
    "sec_dasha_antar":  "Current antardasha",
    "sec_dasha_full":   "Full Vimshottari timeline",
    "sec_career":       "Career & wealth destiny",
    "sec_career_fields":"Best career fields for your lagna",
    "sec_career_yk":    "Yoga Karaka and career wealth",
    "sec_wealth_lords": "Wealth house lords",
    "sec_marriage":     "Marriage and partnership analysis",
    "sec_venus":        "Venus — the natural significator of marriage",
    "sec_spouse":       "Spouse indicators",
    "sec_yogas":        "Yogas and doshas detected in your chart",
    "sec_remedies":     "Planetary remedies for your chart",
    "sec_daily":        "Universal daily practices",
    "sec_today_moon":   "Today's Moon",
    "sec_kalam":        "Today's kalam timings — avoid for new starts",
    "sec_good_windows": "Best windows today for important activities",
    "sec_14day":        "14-day lunar calendar for your Rasi",
    "sec_chandra":      "Chandrashtama days — next 90 days",
    "sec_summary":      "Complete chart summary at a glance",
    "sec_all_planets":  "All planetary positions",
    "lagna_lbl":        "Lagna (ascendant)",
    "rasi_lbl":         "Rasi (moon sign)",
    "nakshatra_lbl":    "Janma nakshatra",
    "pada_lbl":         "Nakshatra pada",
    "lagna_lord_lbl":   "Lagna lord",
    "nak_lord_lbl":     "Nakshatra lord",
    "element_lbl":      "Element",
    "ayanamsa_lbl":     "Lahiri ayanamsa",
    "deity_lbl":        "Deity",
    "symbol_lbl":       "Symbol",
    "lord_lbl":         "Lord",
    "quality_lbl":      "Quality",
    "curr_dasha_lbl":   "Current dasha",
    "started_lbl":      "Started",
    "ends_lbl":         "Ends",
    "duration_lbl":     "Duration",
    "upcoming_lbl":     "Upcoming dasha",
    "10h_sign_lbl":     "10th house sign",
    "10h_lord_lbl":     "10th house lord",
    "planets_10h_lbl":  "Planets in 10H",
    "7h_sign_lbl":      "7th house sign",
    "7h_lord_lbl":      "7th house lord",
    "7h_placed_lbl":    "placed in",
    "7h_planets_lbl":   "Planets in 7H",
    "sunrise_lbl":      "Sunrise",
    "sunset_lbl":       "Sunset",
    "day_lord_lbl":     "Day lord",
    "house_lbl":        "House",
    "sign_lbl":         "Sign",
    "degree_lbl":       "Degree",
    "planet_lbl":       "Planet",
    "Sun":     "Sun",     "Moon":    "Moon",    "Mars":    "Mars",
    "Mercury": "Mercury", "Jupiter": "Jupiter", "Venus":   "Venus",
    "Saturn":  "Saturn",  "Rahu":    "Rahu",    "Ketu":    "Ketu",
    "rahu_kalam":    "Rahu Kalam",
    "yamagandam":    "Yamagandam",
    "gulika_kalam":  "Gulika Kalam",
    "abhijit":       "Abhijit Muhurta",
    "chandrashtama": "Chandrashtama",
    "active_now":    "ACTIVE NOW",
    "no_periods":    "No Chandrashtama periods found in next 90 days.",
    "house":         "house",
    "empty":         "Empty",
    "retrograde":    "℞ Retrograde",
    "asc_label":     "ASC ★",
    "new_reading_btn": "New reading",
    "yoga_karaka":   "Yoga Karaka",
    "none":          "None",
    "best_time":     "Best time",
    "years":         "years",
    "duration_h":    "duration",
}

# Tamil section titles and descriptions
LAGNA_DESC_TAM = {
    'Aries':      'தைரியம், சக்தி, முன்னோடி மனப்பான்மை. இயற்கையான தலைவர். வேகமான முடிவெடுப்பவர்.',
    'Taurus':     'பொறுமை, கலை உணர்வு, நிலையான மனம். வசதிகளை விரும்புபவர். நம்பகமான நண்பன்.',
    'Gemini':     'அறிவார்ந்த ஆர்வம், தகவல் தொடர்பு திறன், மாற்றியமைக்கும் திறன். சுறுசுறுப்பான மனம்.',
    'Cancer':     'அன்பு, உணர்வுப்பூர்வமான உள்ளுணர்வு, குடும்பப் பற்று. பாதுகாக்கும் குணம்.',
    'Leo':        'தன்னம்பிக்கை, தாராள மனப்பான்மை, தலைமைத்துவ குணம். கவுரவத்தை விரும்புபவர்.',
    'Virgo':      'விரிவான பகுப்பாய்வு, சேவை மனம், நுண்ணிய கவனிப்பு. உயர் தரத்தை விரும்புபவர்.',
    'Libra':      'நீதி, சமநிலை, கலை ஈர்ப்பு, உறவுகளில் கவனம். இயற்கையான தூதுவர்.',
    'Scorpio':    'ஆழமான உணர்வுகள், மாற்றும் சக்தி, மர்ம சக்தி. தடைகளை கடந்து எழுபவர்.',
    'Sagittarius':'தத்துவம், நம்பிக்கை, சாகசம், உண்மையை தேடுபவர். அறிவை விரும்புபவர்.',
    'Capricorn':  'ஒழுக்கம், லட்சியம், பொறுமை, கட்டமைப்பு. மெதுவாக உயர்பவர், உறுதியாக நிற்பவர்.',
    'Aquarius':   'மனிதாபிமானம், அசல் சிந்தனை, சமுதாய நலன். புரட்சிகரமான கண்ணோட்டம்.',
    'Pisces':     'இரக்கம், கற்பனை சக்தி, ஆன்மிக ஈர்ப்பு, அன்பு. உயர்ந்த படைப்பாற்றல்.',
}

RASI_DESC_TAM = {
    'Aries':      'உங்கள் உள் உலகம் உத்வேகமானது, உணர்ச்சிகரமானது, சுதந்திரமானது.',
    'Taurus':     'உங்கள் உள் மனம் நிலைத்தன்மை, அழகு, உடல் இன்பத்தை விரும்புகிறது.',
    'Gemini':     'உங்கள் மனம் அமைதியற்றது, ஆர்வமானது, எப்போதும் புதிய யோசனைகளை தேடுகிறது.',
    'Cancer':     'உங்கள் உணர்வு மையம் உணர்திறன் மிக்கது, அன்பானது, குடும்பத்தோடு பிணைந்தது.',
    'Leo':        'நீங்கள் உணர்வுகளை வெளிப்படையாக வெளிப்படுத்துகிறீர்கள், அன்பையும் கவனத்தையும் விரும்புகிறீர்கள்.',
    'Virgo':      'உங்கள் உள் உலகம் பகுப்பாய்வு மிக்கது, தூய்மையை விரும்புவது.',
    'Libra':      'நீங்கள் நல்லிணக்கத்தை தேடுகிறீர்கள் — சண்டை உங்கள் சமநிலையை குலைக்கும்.',
    'Scorpio':    'உங்கள் உணர்வு ஆழம் தீவிரமானது, தனிப்பட்டது, மாற்றத்தை ஏற்றுக்கொள்வது.',
    'Sagittarius':'உங்கள் உள் உலகம் இலட்சியவாதமானது, சாகசமானது, தத்துவ சிந்தனையில் திளைப்பது.',
    'Capricorn':  'சாதனை மூலம் உணர்வுகளை வெளிப்படுத்துகிறீர்கள் — கடமை உங்கள் வீடு.',
    'Aquarius':   'உங்கள் உள் உலகம் பற்றற்றது, இலட்சியவாதமானது, மனிதகுலத்துடன் இணைந்தது.',
    'Pisces':     'உங்கள் உணர்வு உலகம் எல்லையற்றது, பிறரை எளிதில் உள்வாங்குவது.',
}

NAK_DESC_TAM = {
    'Ashwini':         'வேகமான தொடக்கங்கள், குணமளிக்கும் சக்தி, முன்னோடி ஆவி.',
    'Bharani':         'தீவிர மாற்றம், படைப்பாற்றல், பிறருக்காக சுமை தாங்கும் குணம்.',
    'Krittika':        'கூர்மையான அறிவு, சுத்திகரிக்கும் நெருப்பு, ஊடுருவும் தெளிவு.',
    'Rohini':          'புலன் இன்பம், படைப்பு வளம், வலுவான பொருள் விருப்பங்கள்.',
    'Mrigashira':      'அமைதியற்ற தேடல் — எப்போதும் உண்மை, அழகு, சரியான துணையை தேடுபவர்.',
    'Ardra':           'புயல் மற்றும் மாற்றம் — கொந்தளிப்பு புத்துயிரையும் ஆழமான அறிவையும் கொண்டுவருகிறது.',
    'Punarvasu':       'செழிப்பின் மீண்டும் வருகை — அதிதி தேவியின் நட்சத்திரம். நீங்கள் எப்போதும் மீண்டு எழுவீர்கள். ஸ்ரீ ராமரின் ஜன்ம நட்சத்திரம்.',
    'Pushya':          'ஊட்டம், தர்மம், ஆன்மிக பக்தி. அனைத்திலும் மிகவும் சுபமான நட்சத்திரம்.',
    'Ashlesha':        'மர்மகரமான பாம்பு சக்தி — கூர்மை, ஊடுருவும், மனோதத்துவ திறன்.',
    'Magha':           'ராஜ சிம்மாசனம் — முன்னோர் சக்தி, பெருமை, இயற்கையான தலைமை.',
    'Purva Phalguni':  'இன்பம், ஓய்வு, படைப்பாற்றல், வாழ்வின் தாரளமான அனுபவம்.',
    'Uttara Phalguni': 'கண்ணியத்துடன் சேவை. அதிர்ஷ்டமானவர், கண்ணியமானவர்.',
    'Hasta':           'திறமையான கைகள் — கைவேலை, குணமளித்தல், துல்லியம், புத்திசாலித்தனம்.',
    'Chitra':          'அழகின் புத்திசாலி கட்டிடக்கலைஞர் — கலை, துல்லியம், பரிபூரணத்தை விரும்புவது.',
    'Swati':           'சுதந்திரமானவர், சுதந்திர ஆவி, வணிக திறன் மிக்கவர், காற்றில் சுடர் போல் மாற்றியமைக்கக்கூடியவர்.',
    'Vishakha':        'இலக்கு நோக்கி கவனம் செலுத்துபவர் — தீவிர கவனத்தால் வெற்றி.',
    'Anuradha':        'அர்ப்பணிப்பு, விசுவாசம், சமூக திறன். ஆழமான நட்பு மற்றும் ஒழுங்கமைக்கப்பட்ட அமைப்புகள்.',
    'Jyeshtha':        'மூத்தோர் ஞானம், பாதுகாக்கும் சக்தி, மறைந்த வலிமை.',
    'Mula':            'வேர் ஆராய்ச்சி — எல்லாவற்றின் அடிப்படைக்கு செல்கிறது.',
    'Purva Ashadha':   'வெல்ல முடியாத சக்தி, நீரால் சுத்திகரிப்பு, வலுவான விடாமுயற்சி.',
    'Uttara Ashadha':  'இறுதி வெற்றி — நீதியின் மூலம் நிலையான வெற்றி.',
    'Shravana':        'கேட்டல், கற்றல், அறிவின் மூலம் உலகை இணைத்தல்.',
    'Dhanishtha':      'சமுதாயத்தின் மூலம் செல்வம், தாளம் மற்றும் வளம்.',
    'Shatabhisha':     'குணமளித்தல், மர்மம், தனி ஆன்மிக சக்தி.',
    'Purva Bhadrapada':'தீவிர மாற்றம் — மற்றப்படமான அறிவுடன் தூய்மையற்றதை எரிக்கிறது.',
    'Uttara Bhadrapada':'ஆழம், ஞானம், முனிவரின் பொறுமை.',
    'Revati':          'பயணத்தின் முடிவு — இரக்கம், நிறைவு, ஆன்மிக மூடல்.',
}

DASHA_EFFECTS_TAM = {
    'Ketu':    'ஆன்மிக பற்றின்மை, கர்ம தூய்மை, மறைவான சாஸ்திரங்களில் ஆர்வம். உடல் நலனில் கவனம் தேவை.',
    'Venus':   'பொருள் செழிப்பு, ஆடம்பரம், உறவுகள், கலை வெற்றி. மிகவும் வசதியான மகாதசை.',
    'Sun':     'அதிகாரம், தொழில் அங்கீகாரம், அரசாங்க விவகாரங்கள், தந்தை தொடர்பான விஷயங்கள்.',
    'Moon':    'உணர்வு அனுபவங்கள், பயணம், பொது வாழ்க்கை, தாயின் உடல்நலன்.',
    'Mars':    'சக்தி, லட்சியம், சொத்து, நிலம், சகோதர தொடர்பான விஷயங்கள்.',
    'Rahu':    'தீவிர லட்சியம், வெளிநாட்டு தொடர்புகள், திடீர் ஆதாயம் மற்றும் நஷ்டம். கர்ம தீவிரம்.',
    'Jupiter': 'ஞானம், தர்மம், பிள்ளைகள், உயர்கல்வி, அதிர்ஷ்டம். மிகவும் சுபமான தசை.',
    'Saturn':  'ஒழுக்கம், கடின உழைப்பு, கர்ம கடன் திருப்பம், மெதுவான ஆனால் நிரந்தர வெகுமதி.',
    'Mercury': 'அறிவு, தகவல் தொடர்பு, வர்த்தகம், வணிகம், பகுப்பாய்வு வெற்றி.',
}

HOUSE_THEMES_TAM = [
    'சுயம், ஆளுமை, ஆரோக்கியம், உடல் மற்றும் முதல் தோற்றம்',
    'செல்வம், பேச்சு, குடும்பம், சேமிப்பு மற்றும் உணவு',
    'தைரியம், சகோதரர், குறுகிய பயணம், தொடர்பு மற்றும் சுயமுயற்சி',
    'வீடு, தாய், சொத்து, கல்வி, உணர்வு பாதுகாப்பு மற்றும் வாகனங்கள்',
    'அறிவு, பிள்ளைகள், படைப்பாற்றல், முதலீடு மற்றும் முன்னோர் புண்ணியம்',
    'எதிரிகள், கடன், நோய், அன்றாட வேலை, சேவை மற்றும் தடைகள்',
    'திருமணம், கூட்டாண்மை, வணிக உறவுகள் மற்றும் வெளிநாட்டு தொடர்புகள்',
    'ஆயுள், மாற்றம், பரம்பரை, மறைந்த விஷயங்கள் மற்றும் திடீர் நிகழ்வுகள்',
    'அதிர்ஷ்டம், தந்தை, உயர்கல்வி, நீண்ட பயணம், தர்மம் மற்றும் யாத்திரை',
    'தொழில், பொது வாழ்க்கை, தகுதி, அதிகாரம், வாழ்க்கைத்தொழில் மற்றும் அரசாங்கம்',
    'வருமானம், ஆதாயம், மூத்த சகோதரர், சமூக வலைப்பின்னல், நம்பிக்கைகள் மற்றும் விருப்பங்கள் நிறைவேறுதல்',
    'வெளிநாடு, ஆன்மிக விடுதலை, மறைந்த செலவு மற்றும் மோட்சம்',
]

def T(key):
    """Get translation for current language."""
    lang = st.session_state.get("lang", "English")
    return TAM.get(key, key) if lang == "தமிழ்" else ENG.get(key, key)

def is_tamil():
    return st.session_state.get("lang", "English") == "தமிழ்"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vedic Astrology Reading",
    page_icon="🔯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:760px}
html,body,[class*="css"]{font-family:'Segoe UI',sans-serif}

.hero{text-align:center;padding:2rem 1rem 1.5rem;
  background:linear-gradient(135deg,#0d1117 0%,#161b22 60%,#1c2333 100%);
  border:1px solid #30363d;border-radius:16px;margin-bottom:1.5rem}
.hero-icon{font-size:2.8rem;margin-bottom:.5rem}
.hero h1{font-size:1.75rem;font-weight:600;margin:0 0 .35rem;color:#e2c887}
.hero p{font-size:.9rem;color:#8b949e;margin:0}

.profile-bar{display:flex;align-items:center;gap:1rem;
  background:#161b22;border:1px solid #30363d;border-radius:12px;
  padding:1rem 1.25rem;margin-bottom:1rem}
.avatar{width:50px;height:50px;border-radius:50%;background:#1f2d3d;
  border:1px solid #388bfd44;color:#79c0ff;font-size:1rem;font-weight:600;
  display:flex;align-items:center;justify-content:center;flex-shrink:0}
.pname{font-size:1rem;font-weight:600;color:#e6edf3;margin-bottom:3px}
.pdetails{font-size:.78rem;color:#8b949e}
.badge-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.badge{font-size:.68rem;padding:2px 9px;border-radius:20px;
  border:1px solid #30363d;background:#1c2128;color:#8b949e}
.badge-gold{background:#2a1f0a;border-color:#e2c88744;color:#e2c887}
.badge-blue{background:#0d2137;border-color:#388bfd44;color:#79c0ff}

.card{background:#161b22;border:1px solid #30363d;border-radius:12px;
  padding:1.1rem 1.25rem;margin-bottom:.9rem}
.sec-title{font-size:.72rem;font-weight:600;text-transform:uppercase;
  letter-spacing:.07em;color:#8b949e;border-bottom:1px solid #21262d;
  padding-bottom:.35rem;margin-bottom:.8rem}

.metric-row{display:flex;gap:.65rem;flex-wrap:wrap;margin-bottom:.9rem}
.metric{flex:1;min-width:110px;background:#0d1117;border:1px solid #21262d;
  border-radius:10px;padding:.65rem .9rem;text-align:center}
.metric-val{font-size:.95rem;font-weight:600;color:#e2c887;margin-bottom:2px}
.metric-lbl{font-size:.68rem;color:#8b949e;text-transform:uppercase;letter-spacing:.04em}

.planet-row{display:flex;align-items:flex-start;gap:.75rem;
  padding:.55rem 0;border-bottom:1px solid #21262d}
.planet-row:last-child{border-bottom:none}
.p-sym{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:1rem;flex-shrink:0;
  background:#1c2128;border:1px solid #30363d}
.p-name{font-size:.82rem;font-weight:600;color:#c9d1d9;margin-bottom:1px}
.p-pos{font-size:.74rem;color:#8b949e}
.p-effect{font-size:.8rem;color:#c9d1d9;margin-top:2px;line-height:1.5}
.p-ret{font-size:.65rem;color:#f0883e;margin-left:4px}
.p-dignity{font-size:.65rem;padding:1px 6px;border-radius:8px;margin-left:4px}
.dg-ex{background:#1a2d1a;color:#56d364}
.dg-db{background:#2d1a1a;color:#f85149}
.dg-own{background:#1f2a1f;color:#3fb950}
.dg-fr{background:#1a2333;color:#58a6ff}

.dasha-block{background:#0d1117;border:1px solid #30363d;
  border-left:3px solid #388bfd;border-radius:0 10px 10px 0;
  padding:.85rem 1rem;margin-bottom:.65rem}
.dasha-block.current{border-left-color:#e2c887;background:#1a1500}
.dasha-name{font-size:.95rem;font-weight:600;margin-bottom:3px}
.dasha-cur .dasha-name{color:#e2c887}
.dasha-period{font-size:.72rem;color:#8b949e;margin-bottom:.35rem}
.dasha-text{font-size:.8rem;color:#c9d1d9;line-height:1.6}

.remedy-item{display:flex;gap:.7rem;align-items:flex-start;
  padding:.65rem 0;border-bottom:1px solid #21262d}
.remedy-item:last-child{border-bottom:none}
.rem-num{width:24px;height:24px;border-radius:50%;
  background:#1a2d1a;border:1px solid #3fb950;color:#3fb950;
  font-size:.7rem;font-weight:600;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;margin-top:2px}
.rem-body{flex:1}
.rem-title{font-size:.82rem;font-weight:600;color:#e2c887;margin-bottom:2px}
.rem-text{font-size:.78rem;color:#c9d1d9;line-height:1.55}

.yoga-item{background:#0d1117;border:1px solid #21262d;
  border-radius:8px;padding:.75rem 1rem;margin-bottom:.55rem}
.yoga-name{font-size:.85rem;font-weight:600;color:#c9d1d9;margin-bottom:3px}
.yoga-type{font-size:.65rem;padding:2px 8px;border-radius:10px;margin-left:6px}
.yt-raja{background:#1f1a00;color:#e2c887}
.yt-dhana{background:#1a2d1a;color:#56d364}
.yt-dosha{background:#2d1a1a;color:#f85149}
.yt-positive{background:#1a2333;color:#58a6ff}
.yt-intelligence{background:#1a1a2d;color:#a5a0e8}
.yt-wealth{background:#1a2d1a;color:#3fb950}
.yoga-desc{font-size:.78rem;color:#8b949e;line-height:1.55;margin-top:3px}

.info-box{background:#0d2137;border-left:3px solid #388bfd;
  border-radius:0 8px 8px 0;padding:.7rem .9rem;
  font-size:.8rem;color:#79c0ff;margin-bottom:.75rem;line-height:1.6}
.warn-box{background:#1e1600;border-left:3px solid #d29922;
  border-radius:0 8px 8px 0;padding:.7rem .9rem;
  font-size:.8rem;color:#e3b341;margin-bottom:.75rem;line-height:1.6}
.success-box{background:#0d2010;border-left:3px solid #3fb950;
  border-radius:0 8px 8px 0;padding:.7rem .9rem;
  font-size:.8rem;color:#56d364;margin-bottom:.75rem;line-height:1.6}
.reading-text{font-size:.85rem;color:#c9d1d9;line-height:1.8;margin-bottom:.65rem}

.house-row{display:grid;grid-template-columns:28px 1fr;gap:.5rem;
  padding:.45rem 0;border-bottom:1px solid #21262d;align-items:start}
.house-row:last-child{border-bottom:none}
.house-num{width:24px;height:24px;border-radius:50%;background:#1c2128;
  color:#8b949e;font-size:.7rem;font-weight:600;display:flex;
  align-items:center;justify-content:center}
.house-content{font-size:.8rem;color:#c9d1d9;line-height:1.5}
.house-sign{font-weight:600;color:#e2c887}
.house-tenants{font-size:.72rem;color:#79c0ff;margin-top:1px}
.house-theme{font-size:.72rem;color:#8b949e;margin-top:1px}

div.stButton>button{background:linear-gradient(135deg,#e2c887,#c9a227);
  color:#0d1117;font-weight:700;border:none;border-radius:8px;
  padding:.55rem 1.5rem;font-size:.9rem;width:100%}
div.stButton>button:hover{opacity:.88}

.stTabs [data-baseweb="tab-list"]{gap:5px;background:transparent;
  border-bottom:1px solid #30363d}
.stTabs [data-baseweb="tab"]{background:transparent;border:1px solid #30363d;
  border-radius:8px 8px 0 0;color:#8b949e;font-size:.78rem;
  padding:.35rem .85rem}
.stTabs [aria-selected="true"]{background:#161b22 !important;
  color:#e2c887 !important;border-color:#e2c887 !important}
.stTabs [data-baseweb="tab-panel"]{background:#0d1117;border:1px solid #30363d;
  border-top:none;border-radius:0 0 10px 10px;padding:1.1rem}
</style>""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def initials(name):
    return "".join(p[0].upper() for p in name.strip().split()[:2]) or "?"

def html_badge(text, cls="badge"):
    return f'<span class="{cls}">{text}</span>'

def metric(val, lbl):
    return f'<div class="metric"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>'

def reading_text(txt):
    st.markdown(f'<div class="reading-text">{txt}</div>', unsafe_allow_html=True)

def info_box(txt):
    st.markdown(f'<div class="info-box">{txt}</div>', unsafe_allow_html=True)

def warn_box(txt):
    st.markdown(f'<div class="warn-box">{txt}</div>', unsafe_allow_html=True)

def success_box(txt):
    st.markdown(f'<div class="success-box">{txt}</div>', unsafe_allow_html=True)

def sec_title(txt):
    st.markdown(f'<div class="sec-title">{txt}</div>', unsafe_allow_html=True)

# ── Render reading ─────────────────────────────────────────────────────────────
def render_reading(chart, dasha, yogas, name, dob, tob, pob):
    p = chart['planets']
    ini = initials(name)
    dob_str = dob.strftime("%b %d, %Y")
    tob_str = tob.strftime("%I:%M %p") if tob else "Approx. noon"
    details = f"{dob_str} · {tob_str} · {pob}"

    badges = "".join([
        html_badge(f"{chart['lagna_tamil']} lagna", "badge badge-gold"),
        html_badge(f"{chart['rasi_tamil']} rasi", "badge badge-blue"),
        html_badge(f"{chart['nakshatra']} pada {chart['pada']}", "badge"),
        html_badge(f"{dasha['current']['lord']} dasha", "badge"),
    ])
    st.markdown(f"""
    <div class="profile-bar">
      <div class="avatar">{ini}</div>
      <div>
        <div class="pname">{name}</div>
        <div class="pdetails">{details}</div>
        <div class="badge-row">{badges}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs([
        T("tab_overview"), T("tab_planets"), T("tab_houses"),
        T("tab_dasha"), T("tab_career"), T("tab_relationships"),
        T("tab_yogas"), T("tab_remedies"), T("tab_panchang"), T("tab_summary")
    ])

    # ── TAB 1: Overview ───────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="metric-row">' + "".join([
            metric(chart['lagna_tamil'] if is_tamil() else chart['lagna'], T("lagna_lbl")),
            metric(chart['rasi_tamil']  if is_tamil() else chart['rasi'],  T("rasi_lbl")),
            metric(chart['nakshatra'],   T("nakshatra_lbl")),
            metric(f"{T('pada_lbl')} {chart['pada']}", T("pada_lbl")),
        ]) + '</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-row">' + "".join([
            metric(T(chart['lagna_lord']),    T("lagna_lord_lbl")),
            metric(T(chart['nakshatra_lord']), T("nak_lord_lbl")),
            metric(chart['lagna_element'],    T("element_lbl")),
            metric(f"{chart['ayanamsa']}°",   T("ayanamsa_lbl")),
        ]) + '</div>', unsafe_allow_html=True)

        # ── South Indian Rasi Chart ───────────────────────────────────────────
        sec_title(T("sec_chart"))
        lagna_idx = chart['lagna_index']

        # South Indian layout: fixed sign positions (Aries=top-row-2nd cell)
        # Grid positions 0–11 map to fixed signs 0–11 (Aries..Pisces)
        # Layout (row, col) for each sign index:
        # Pis(11) Ari(0)  Tau(1)  Gem(2)
        # Aqu(10) [center-left]   [center-right] Can(3)
        # Cap(9)  [center-left]   [center-right] Leo(4)
        # Sag(8)  Sco(7)  Lib(6)  Vir(5)
        GRID_SIGN = [
            [11, 0, 1, 2],
            [10, -1, -1, 3],
            [9,  -1, -1, 4],
            [8,  7,  6,  5],
        ]

        # Build sign→planets mapping
        sign_planets = {i: [] for i in range(12)}
        for pname in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
            si = p[pname]['sign_index']
            sym = p[pname]['symbol']
            abbr = pname[:3]
            sign_planets[si].append(f"{sym}{abbr}")

        SIGN_SHORT = ['Ari','Tau','Gem','Can','Leo','Vir',
                      'Lib','Sco','Sag','Cap','Aqu','Pis']

        def make_cell(sign_idx, is_center=False):
            if is_center:
                return '<td style="background:#0d1117;border:1px solid #21262d;width:25%;height:70px"></td>'
            is_lagna = (sign_idx == lagna_idx)
            lagna_mark = f'<div style="font-size:.55rem;color:#e2c887;letter-spacing:.05em">{T("asc_label")}</div>' if is_lagna else ''
            planets_here = sign_planets.get(sign_idx, [])
            planet_html = ""
            for pstr in planets_here:
                sym_char = pstr[0]
                p_name   = pstr[1:]
                # color by planet
                pcolor = {
                    '☉':'#e2a020','☽':'#8ab4d4','♂':'#d45050','☿':'#50a050',
                    '♃':'#c0842a','♀':'#c060a0','♄':'#8090a0','☊':'#9080c0','☋':'#c09060'
                }.get(sym_char, '#c9d1d9')
                planet_html += f'<span style="color:{pcolor};font-size:.72rem;font-weight:600;margin-right:2px">{sym_char}{p_name}</span>'

            border_style = "border:1.5px solid #e2c887" if is_lagna else "border:1px solid #30363d"
            bg_style     = "background:#1a1500" if is_lagna else "background:#161b22"

            return (
                f'<td style="{bg_style};{border_style};width:25%;height:70px;'
                f'vertical-align:top;padding:4px 5px;font-size:.65rem">'
                f'<div style="color:#8b949e;font-size:.6rem;margin-bottom:2px">{SIGN_SHORT[sign_idx]}</div>'
                f'{lagna_mark}'
                f'<div style="line-height:1.4">{planet_html}</div>'
                f'</td>'
            )

        # Build center cells with chart label
        center_html = (
            '<td colspan="2" rowspan="2" style="background:#0d1117;border:1px solid #21262d;'
            'text-align:center;vertical-align:middle;padding:8px">'
            f'<div style="font-size:.75rem;font-weight:600;color:#e2c887;margin-bottom:4px">{name}</div>'
            f'<div style="font-size:.65rem;color:#8b949e">{chart["lagna_tamil"]} Lagna</div>'
            f'<div style="font-size:.6rem;color:#8b949e">{chart["rasi_tamil"]} Rasi</div>'
            f'<div style="font-size:.6rem;color:#8b949e;margin-top:4px">{chart["nakshatra"]}</div>'
            f'<div style="font-size:.58rem;color:#8b949e">Pada {chart["pada"]}</div>'
            '</td>'
        )

        rows_html = ""
        for r, row in enumerate(GRID_SIGN):
            row_html = "<tr>"
            skip_cols = 0
            for c_idx, sign_idx in enumerate(row):
                if skip_cols > 0:
                    skip_cols -= 1
                    continue
                if sign_idx == -1:
                    if r == 1 and c_idx == 1:
                        row_html += center_html
                        skip_cols = 1
                    continue
                row_html += make_cell(sign_idx)
            row_html += "</tr>"
            rows_html += row_html

        chart_html = (
            '<div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;'
            'padding:.75rem;margin-bottom:1rem;overflow-x:auto">'
            '<table style="width:100%;border-collapse:collapse;table-layout:fixed">'
            f'{rows_html}'
            '</table>'
            '<div style="font-size:.65rem;color:#8b949e;margin-top:.5rem;text-align:center">'
            '★ = Lagna (Ascendant) &nbsp;|&nbsp; Fixed South Indian format</div>'
            '</div>'
        )
        st.markdown(chart_html, unsafe_allow_html=True)

        sec_title(T("sec_lagna"))
        reading_text((LAGNA_DESC_TAM if is_tamil() else LAGNA_DESC).get(chart['lagna'], ''))

        sec_title(f"{T('sec_rasi')} — {chart['rasi_tamil'] if is_tamil() else chart['rasi']}")
        reading_text((RASI_DESC_TAM if is_tamil() else RASI_DESC).get(chart['rasi'], ''))

        sec_title(f"{T('sec_nakshatra')} — {chart['nakshatra']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card">
              <div class="sec-title">{T("sec_star_profile")}</div>
              <div class="reading-text">
                <b style="color:#e2c887">{T("deity_lbl")}:</b> {chart['nakshatra_deity']}<br>
                <b style="color:#e2c887">{T("symbol_lbl")}:</b> {chart['nakshatra_symbol']}<br>
                <b style="color:#e2c887">{T("lord_lbl")}:</b> {T(chart['nakshatra_lord'])}<br>
                <b style="color:#e2c887">{T("quality_lbl")}:</b> {chart['nakshatra_quality']}<br>
                <b style="color:#e2c887">{T("pada_lbl")}:</b> {chart['pada']}
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            nak_desc_text = (NAK_DESC_TAM if is_tamil() else NAK_DESC).get(chart['nakshatra'], '')
            st.markdown(f"""
            <div class="card">
              <div class="sec-title">{T("sec_nak_meaning")}</div>
              <div class="reading-text">{nak_desc_text}</div>
            </div>""", unsafe_allow_html=True)

        yk = chart.get('yoga_karaka', [])
        if yk:
            yk_names = ", ".join(T(y) for y in yk)
            info_box(f"⭐ <b>{T('yoga_karaka')}:</b> {yk_names} — {'மிகவும் சக்திவாய்ந்த கிரகங்கள். இவற்றின் தசை காலத்தில் தொழில் மற்றும் செல்வ வெற்றி உச்சமடையும்.' if is_tamil() else f'the most powerful benefic planet(s) for {chart[chr(108)+(chr(97))+(chr(103))+(chr(110))+(chr(97))]} lagna. Their Dasha periods bring exceptional career and wealth results.'}")

    # ── TAB 2: Planets ────────────────────────────────────────────────────────
    with tabs[1]:
        sec_title(T("sec_planets"))
        for name_p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
            pl = p[name_p]
            sym   = pl['symbol']
            color = pl.get('color','#888')
            ret   = '<span class="p-ret">℞ Retrograde</span>' if pl.get('retrograde') else ''
            dg    = pl.get('dignity','')
            dg_cls = {'Exalted ↑':'dg-ex','Debilitated ↓':'dg-db','Own sign ★':'dg-own','Friendly +':'dg-fr'}.get(dg,'')
            dg_html = f'<span class="p-dignity {dg_cls}">{dg}</span>' if dg else ''
            house_theme = (HOUSE_THEMES_TAM if is_tamil() else HOUSE_THEMES)[pl['house']-1]

            from engine import PLANET_NATURE
            effect = PLANET_NATURE.get(name_p, '')
            house_effect = f"In house {pl['house']} — rules over {house_theme}."

            st.markdown(f"""
            <div class="planet-row">
              <div class="p-sym" style="color:{color}">{sym}</div>
              <div style="flex:1">
                <div class="p-name">{name_p} {ret}{dg_html}</div>
                <div class="p-pos">{pl['sign']} ({pl['sign_tamil']}) · {pl['degree']}° · House {pl['house']} · {pl['nakshatra']}</div>
                <div class="p-effect">{house_effect}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 3: Houses ─────────────────────────────────────────────────────────
    with tabs[2]:
        sec_title(T("sec_houses"))
        lagna_idx = chart['lagna_index']
        for h in range(1, 13):
            sign_idx = (lagna_idx + h - 1) % 12
            sign = SIGNS[sign_idx]
            sign_lord = SIGN_LORDS[sign_idx]
            tenants = [nm for nm in p if p[nm]['house'] == h]
            tenant_str = " · ".join(
                f"{p[t]['symbol']} {t}" for t in tenants
            ) if tenants else "Empty"
            theme = HOUSE_THEMES[h-1]
            st.markdown(f"""
            <div class="house-row">
              <div class="house-num">{h}</div>
              <div class="house-content">
                <span class="house-sign">{sign}</span>
                <span style="font-size:.72rem;color:#8b949e"> · Lord: {sign_lord}</span>
                <div class="house-tenants">{tenant_str}</div>
                <div class="house-theme">{theme}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 4: Dasha ─────────────────────────────────────────────────────────
    with tabs[3]:
        d = dasha['current']
        ad = dasha['current_antardasha']
        d_lord_t  = T(d['lord'])
        ad_lord_t = T(ad['lord'])
        yrs_lbl   = T("years")

        st.markdown('<div class="metric-row">' + "".join([
            metric(f"{d_lord_t} {'மகாதசை' if is_tamil() else 'Mahadasha'}", T("curr_dasha_lbl")),
            metric(d['start'].strftime('%Y'), T("started_lbl")),
            metric(d['end'].strftime('%Y'),   T("ends_lbl")),
            metric(f"{d['years']} {yrs_lbl}", T("duration_lbl")),
        ]) + '</div>', unsafe_allow_html=True)

        sec_title(T("sec_dasha_curr"))
        dasha_name_html = f"{d['symbol']} {d_lord_t} {'மகாதசை' if is_tamil() else 'Mahadasha'}"
        dasha_text = (DASHA_EFFECTS_TAM if is_tamil() else DASHA_EFFECTS).get(d['lord'],'')
        st.markdown(f"""
        <div class="dasha-block current dasha-cur">
          <div class="dasha-name">{dasha_name_html}</div>
          <div class="dasha-period">{d['start'].strftime('%b %Y')} — {d['end'].strftime('%b %Y')}</div>
          <div class="dasha-text">{dasha_text}</div>
        </div>""", unsafe_allow_html=True)

        antar_title = f"{T('sec_dasha_antar')} — {ad_lord_t}"
        sec_title(antar_title)
        ad_text = (DASHA_EFFECTS_TAM if is_tamil() else DASHA_EFFECTS).get(ad['lord'],'')
        st.markdown(f"""
        <div class="dasha-block">
          <div class="dasha-name" style="color:#79c0ff">{ad['symbol']} {ad_lord_t} {'அந்தர் தசை' if is_tamil() else 'Antardasha'}</div>
          <div class="dasha-period">{ad['start'].strftime('%b %Y')} — {ad['end'].strftime('%b %Y')}</div>
          <div class="dasha-text">{ad_text}</div>
        </div>""", unsafe_allow_html=True)

        sec_title(T("sec_dasha_full"))
        now = datetime.now()
        now_label = 'இப்போது' if is_tamil() else 'NOW'
        maha_label = 'மகாதசை' if is_tamil() else 'Mahadasha'
        for d_item in dasha['timeline']:
            is_cur   = d_item['start'] <= now <= d_item['end']
            cls      = "dasha-block current dasha-cur" if is_cur else "dasha-block"
            nc       = f'<span style="font-size:.65rem;background:#2a1f0a;color:#e2c887;padding:1px 6px;border-radius:8px;margin-left:8px">{now_label}</span>' if is_cur else ''
            d_lord_translated = T(d_item['lord'])
            d_eff    = (DASHA_EFFECTS_TAM if is_tamil() else DASHA_EFFECTS).get(d_item['lord'],'')
            d_yrs    = f"{d_item['years']} {yrs_lbl}"
            st.markdown(
                f'<div class="{cls}">'
                f'<div class="dasha-name">{d_item["symbol"]} {d_lord_translated} {maha_label}{nc}</div>'
                f'<div class="dasha-period">{d_item["start"].strftime("%Y")} — {d_item["end"].strftime("%Y")} &middot; {d_yrs}</div>'
                f'<div class="dasha-text">{d_eff}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── TAB 5: Career ─────────────────────────────────────────────────────────
    with tabs[4]:
        sec_title(T("sec_career"))
        h10_sign = SIGNS[(lagna_idx + 9) % 12]
        h10_lord = SIGN_LORDS[(lagna_idx + 9) % 12]
        h10_planets = [nm for nm in p if p[nm]['house'] == 10]
        h2_lord  = SIGN_LORDS[(lagna_idx + 1) % 12]
        h11_lord = SIGN_LORDS[(lagna_idx + 10) % 12]

        st.markdown('<div class="metric-row">' + "".join([
            metric(h10_sign,   "10th house sign"),
            metric(h10_lord,   "10th house lord"),
            metric(", ".join(h10_planets) if h10_planets else "Empty", "Planets in 10H"),
            metric(chart['lagna_lord'], "Lagna lord"),
        ]) + '</div>', unsafe_allow_html=True)

        info_box(f"<b>10th house (Karma Bhava):</b> {h10_sign} · Lord: {h10_lord} in house {p[h10_lord]['house']}. "
                 f"This is the primary career indicator in your chart.")

        sec_title(T("sec_career_fields"))
        fields = CAREER_INDICATORS.get(chart['lagna'], ['Versatile — many fields suit this chart'])
        for f in fields:
            st.markdown(f'<div class="reading-text">• {f}</div>', unsafe_allow_html=True)

        sec_title(T("sec_career_yk"))
        yk = chart.get('yoga_karaka', [])
        if yk:
            for y in yk:
                yp = p[y]
                reading_text(f"<b style='color:#e2c887'>{y}</b> is your Yoga Karaka — placed in house {yp['house']} ({yp['sign']}). "
                             f"Its Dasha period is your peak career and wealth window. "
                             f"Current Dasha: {dasha['current']['lord']}. "
                             f"Yoga Karaka Dasha starts: {next((d_item['start'].strftime('%Y') for d_item in dasha['timeline'] if d_item['lord']==y), 'see timeline')}.")

        sec_title(T("sec_wealth_lords"))
        reading_text(f"<b>2nd lord (accumulated wealth):</b> {h2_lord} in house {p[h2_lord]['house']} ({p[h2_lord]['sign']})")
        reading_text(f"<b>11th lord (income & gains):</b> {h11_lord} in house {p[h11_lord]['house']} ({p[h11_lord]['sign']})")

    # ── TAB 6: Relationships ──────────────────────────────────────────────────
    with tabs[5]:
        h7_sign  = SIGNS[(lagna_idx + 6) % 12]
        h7_lord  = SIGN_LORDS[(lagna_idx + 6) % 12]
        h7_planets = [nm for nm in p if p[nm]['house'] == 7]

        st.markdown('<div class="metric-row">' + "".join([
            metric(h7_sign,    "7th house sign"),
            metric(h7_lord,    "7th house lord"),
            metric(f"House {p[h7_lord]['house']}", f"{h7_lord} placed in"),
            metric(", ".join(h7_planets) if h7_planets else "Empty", "Planets in 7H"),
        ]) + '</div>', unsafe_allow_html=True)

        sec_title(T("sec_marriage"))
        rahu_in_7 = p['Rahu']['house'] == 7
        mars_dosha = p['Mars']['house'] in [1,2,4,7,8,12]

        if rahu_in_7:
            warn_box("Rahu in the 7th house creates intense, karmic partnerships — not a divorce yoga, but a transformation yoga. "
                     "Relationships are deeply meaningful but require conscious effort. Partner may be unconventional or from a different background.")
        if mars_dosha:
            warn_box(f"Mars in house {p['Mars']['house']} — Mangal Dosha present. "
                     "Matching horoscopes with partner and Kuja Dosha remedies recommended before marriage.")
        else:
            success_box("No Mangal Dosha — Mars placement is favorable for marriage. No special remedies needed from this angle.")

        reading_text(f"<b>7th house</b> is {h7_sign} ruled by {h7_lord}. "
                     f"{h7_lord} sits in house {p[h7_lord]['house']} ({p[h7_lord]['sign']}), "
                     f"influencing the nature of partnerships through that house's themes.")

        sec_title(T("sec_venus"))
        ven = p['Venus']
        reading_text(f"Venus is in <b>{ven['sign']}</b>, house <b>{ven['house']}</b>, nakshatra <b>{ven['nakshatra']}</b>. "
                     f"Dignity: {ven.get('dignity','Neutral')}. Venus placement reveals the aesthetic of relationships and the kind of partner attracted.")

        sec_title(T("sec_spouse"))
        reading_text(f"7th lord <b>{h7_lord}</b> in house {p[h7_lord]['house']} ({p[h7_lord]['sign']}) "
                     f"suggests the partner will carry themes of the {p[h7_lord]['house']}th house — {HOUSE_THEMES[p[h7_lord]['house']-1]}.")

    # ── TAB 7: Yogas ─────────────────────────────────────────────────────────
    with tabs[6]:
        sec_title(T("sec_yogas"))
        type_cls = {
            'Raja Yoga':'yt-raja','Dhana Yoga':'yt-dhana','Dosha':'yt-dosha',
            'Positive':'yt-positive','Intelligence Yoga':'yt-intelligence','Wealth Yoga':'yt-wealth',
        }
        for y in yogas:
            cls = type_cls.get(y['type'], 'yt-raja')
            st.markdown(f"""
            <div class="yoga-item">
              <div class="yoga-name">{y['name']}
                <span class="yoga-type {cls}">{y['type']}</span>
              </div>
              <div class="yoga-desc">{y['desc']}</div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 8: Remedies ───────────────────────────────────────────────────────
    with tabs[7]:
        sec_title(T("sec_remedies"))
        success_box("Remedies are prioritised based on: (1) your Lagna lord, (2) Nakshatra lord, (3) current Dasha lord, and (4) Yoga Karaka.")

        priority_planets = list(dict.fromkeys([
            chart['lagna_lord'],
            chart['nakshatra_lord'],
            dasha['current']['lord'],
            dasha['current_antardasha']['lord'],
        ] + chart.get('yoga_karaka', [])))

        for i, pl_name in enumerate(priority_planets[:6], 1):
            if pl_name not in REMEDY_DB:
                continue
            day, mantra, action = REMEDY_DB[pl_name]
            sym = PLANET_SYMBOLS.get(pl_name,'★')
            st.markdown(f"""
            <div class="remedy-item">
              <div class="rem-num">{i}</div>
              <div class="rem-body">
                <div class="rem-title">{sym} {pl_name} · {day}</div>
                <div class="rem-text"><b style="color:#79c0ff">Mantra:</b> {mantra}<br>
                <b style="color:#79c0ff">Action:</b> {action}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        sec_title(T("sec_daily"))
        for txt in [
            "Light a ghee or sesame oil lamp every morning before leaving home.",
            "Feed animals (especially crows on Saturday, cows on Sunday) to honor the Navagrahas.",
            "Recite the Navagraha Stotram on Sundays for general planetary protection.",
            "Practice gratitude — Punarvasu and Libra natives are blessed by thankful awareness.",
            "Donate 2–5% of income to a cause you believe in — activates Jupiter 9th house dharma.",
        ]:
            st.markdown(f'<div class="remedy-item"><div class="rem-num">✦</div><div class="rem-body"><div class="rem-text">{txt}</div></div></div>', unsafe_allow_html=True)

    # ── TAB 9: Panchang & Chandrashtama ──────────────────────────────────────
    with tabs[8]:
        rasi_idx   = chart['planets']['Moon']['sign_index']
        lat        = chart['lat']
        lon_coord  = chart['lon']
        tz_str     = chart['tz']
        lagna_lord = chart['lagna_lord']
        today_dt   = datetime.now()
        today_date = today_dt.date()

        # ── Today's moon ─────────────────────────────────────────────────────
        try:
            tmoon  = get_today_moon(lat, lon_coord, tz_str)
            effect = moon_effect_on_rasi(tmoon['sign_index'], rasi_idx)
            q_color = {'good':'#56d364','neutral':'#e3b341','bad':'#f85149'}.get(effect['quality'],'#8b949e')
            q_bg    = {'good':'#0d2010','neutral':'#1e1600','bad':'#2d1a1a'}.get(effect['quality'],'#161b22')

            st.markdown(f"""
            <div style="background:{q_bg};border:1px solid {q_color}44;border-left:3px solid {q_color};
              border-radius:0 12px 12px 0;padding:1rem 1.25rem;margin-bottom:1rem">
              <div style="font-size:.72rem;font-weight:600;text-transform:uppercase;
                letter-spacing:.07em;color:{q_color};margin-bottom:.4rem">
                Today's Moon · {tmoon['time_local'].strftime('%B %d, %Y')}
              </div>
              <div style="font-size:1rem;font-weight:600;color:#e6edf3;margin-bottom:.3rem">
                ☽ Moon in {tmoon['sign']} ({tmoon['sign_tamil']}) · {tmoon['nakshatra']}
              </div>
              <div style="font-size:.82rem;color:#c9d1d9;margin-bottom:.4rem">
                Position {effect['position']} from your Rasi · <b style="color:{q_color}">{effect['name']}</b>
              </div>
              <div style="font-size:.8rem;color:#8b949e;line-height:1.6">{effect['desc']}</div>
            </div>""", unsafe_allow_html=True)

            act_color = q_color
            acts = effect['activities']
            act_html = "".join(f'<span style="display:inline-block;font-size:.72rem;padding:2px 9px;margin:2px 3px;border-radius:10px;background:{q_bg};border:1px solid {act_color}44;color:{act_color}">{a}</span>' for a in acts)
            st.markdown(f'<div style="margin-bottom:1rem">{act_html}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"Could not load today's moon data: {e}")

        # ── Kalam timings ─────────────────────────────────────────────────────
        sec_title(T("sec_kalam"))
        try:
            kalams   = get_kalam_times(today_date, lat, lon_coord, tz_str)
            rk_s,rk_e = kalams['rahu_kalam']
            yg_s,yg_e = kalams['yamagandam']
            gk_s,gk_e = kalams['gulika_kalam']
            ab_s,ab_e = get_abhijit(today_date, lat, lon_coord, tz_str)
            sunrise   = kalams['sunrise']
            sunset    = kalams['sunset']

            st.markdown(f"""
            <div class="metric-row">
              <div class="metric"><div class="metric-val">{sunrise.strftime('%I:%M %p')}</div><div class="metric-lbl">Sunrise</div></div>
              <div class="metric"><div class="metric-val">{sunset.strftime('%I:%M %p')}</div><div class="metric-lbl">Sunset</div></div>
              <div class="metric"><div class="metric-val">{kalams['day_lord']}</div><div class="metric-lbl">Day lord</div></div>
            </div>""", unsafe_allow_html=True)

            _tam = is_tamil()
            kalam_rows = [
                (f'\u2600\ufe0f {T("abhijit")}',    ab_s, ab_e, '#56d364','#0d2010',
                 '\u0b9a\u0bbf\u0bb1\u0ba8\u0bcd\u0ba4 \u0ba8\u0bc7\u0bb0\u0bae\u0bcd \u2014 \u0b9a\u0bc2\u0bb0\u0bbf\u0baf \u0ba8\u0b9f\u0bc1 \u0ba8\u0bc7\u0bb0\u0bae\u0bcd, \u0b85\u0ba9\u0bc8\u0bb5\u0bb0\u0bc1\u0b95\u0bcd\u0b95\u0bc1\u0bae\u0bcd \u0b9a\u0bc1\u0baa\u0bae\u0bbe\u0ba9\u0ba4\u0bc1.' if _tam else 'Best time of day — solar noon window, universally auspicious.'),
                (f'\u260a {T("rahu_kalam")}',   rk_s, rk_e, '#f85149','#2d1a1a',
                 '\u0baa\u0bc1\u0ba4\u0bbf\u0baf\u0bb5\u0bb1\u0bcd\u0bb1\u0bc8 \u0ba4\u0bca\u0b9f\u0b99\u0bcd\u0b95 \u0bb5\u0bc7\u0ba3\u0bcd\u0b9f\u0bbe\u0bae\u0bcd.' if _tam else 'Avoid starting anything new. Ongoing work is fine.'),
                (f'\u26b0 {T("yamagandam")}',   yg_s, yg_e, '#f85149','#2d1a1a',
                 '\u0baf\u0bae\u0ba9\u0bbf\u0ba9\u0bcd \u0ba8\u0bc7\u0bb0\u0bae\u0bcd. \u0baa\u0bc1\u0ba4\u0bbf\u0baf \u0bae\u0bc1\u0baf\u0bb1\u0bcd\u0b9a\u0bbf\u0b95\u0bb3\u0bcd, \u0baa\u0baf\u0ba3\u0bae\u0bcd, \u0baa\u0ba3 \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1\u0b95\u0bb3\u0bcd \u0bb5\u0bc7\u0ba3\u0bcd\u0b9f\u0bbe\u0bae\u0bcd.' if _tam else 'Death time of Yama. No new ventures, travel, or money dealings.'),
                (f'\u2644 {T("gulika_kalam")}', gk_s, gk_e, '#e3b341','#1e1600',
                 '\u0b9a\u0ba9\u0bbf\u0baf\u0bbf\u0ba9\u0bcd \u0ba8\u0bc7\u0bb0\u0bae\u0bcd \u2014 \u0b9a\u0bc6\u0baf\u0bb2\u0bcd\u0b95\u0bb3\u0bcd \u0bae\u0bc0\u0ba3\u0bcd\u0b9f\u0bc1\u0bae\u0bcd \u0ba8\u0bbf\u0b95\u0bb4\u0bc1\u0bae\u0bcd.' if _tam else "Saturn's hour — activities repeat. Avoid loans and funeral rites."),
            ]
            for label, s, e, color, bg, tip in kalam_rows:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {color}33;border-left:3px solid {color};
                  border-radius:0 8px 8px 0;padding:.65rem 1rem;margin-bottom:.5rem;
                  display:flex;align-items:center;gap:1rem">
                  <div style="min-width:160px">
                    <div style="font-size:.82rem;font-weight:600;color:{color}">{label}</div>
                    <div style="font-size:.78rem;color:#c9d1d9">{s.strftime('%I:%M %p')} – {e.strftime('%I:%M %p')}</div>
                  </div>
                  <div style="font-size:.75rem;color:#8b949e;line-height:1.5">{tip}</div>
                </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Kalam calculation error: {e}")

        # ── Good windows today ────────────────────────────────────────────────
        sec_title(T("sec_good_windows"))
        try:
            good = get_good_windows(today_date, lat, lon_coord, tz_str, rasi_idx, lagna_lord)
            if good:
                for w in good:
                    q_c = '#e2c887' if w['quality']=='best' else '#56d364'
                    q_b = '#2a1f0a' if w['quality']=='best' else '#0d2010'
                    st.markdown(f"""
                    <div style="background:{q_b};border:1px solid {q_c}44;border-radius:8px;
                      padding:.65rem 1rem;margin-bottom:.5rem;display:flex;align-items:center;gap:1rem">
                      <div style="min-width:140px">
                        <div style="font-size:.82rem;font-weight:600;color:{q_c}">{w['label']}</div>
                        <div style="font-size:.78rem;color:#c9d1d9">{w['start'].strftime('%I:%M %p')} – {w['end'].strftime('%I:%M %p')}</div>
                      </div>
                      <div style="font-size:.75rem;color:#8b949e;line-height:1.5">{w['reason']}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                warn_box("No strongly auspicious windows found today. Use the Abhijit window for any necessary activities.")
        except Exception as e:
            st.warning(f"Good windows error: {e}")

        # ── 14-day weekly overview ────────────────────────────────────────────
        sec_title(T("sec_14day"))
        try:
            overview = get_weekly_overview(rasi_idx, lat, lon_coord, tz_str)
            for day in overview:
                q         = day["quality"]
                col       = {"good":"#56d364","neutral":"#e3b341","bad":"#f85149"}.get(q,"#8b949e")
                bg        = {"good":"#0d2010","neutral":"#1e1600","bad":"#2d1a1a"}.get(q,"#161b22")
                d_day     = day["day"]
                d_date    = day["date"].strftime("%d %b")
                d_name    = day["name"]
                d_sign    = day["sign"]
                d_nak     = day["nakshatra"]
                d_desc    = day["desc"]
                d_chandra = day["is_chandrashtama"]
                chandra_badge = '<span style="font-size:.65rem;background:#2d1a1a;color:#f85149;padding:1px 6px;border-radius:8px;margin-left:6px">Chandrashtama</span>' if d_chandra else ""
                html = (
                    f'<div style="background:{bg};border:1px solid {col}33;border-radius:8px;'
                    f'padding:.55rem 1rem;margin-bottom:.4rem;display:flex;align-items:center;gap:1rem">'
                    f'<div style="width:44px;text-align:center;flex-shrink:0">'
                    f'<div style="font-size:.78rem;font-weight:600;color:{col}">{d_day}</div>'
                    f'<div style="font-size:.7rem;color:#8b949e">{d_date}</div>'
                    f'</div>'
                    f'<div style="flex:1">'
                    f'<span style="font-size:.82rem;font-weight:600;color:{col}">{d_name}</span>'
                    f'{chandra_badge}'
                    f'<span style="font-size:.72rem;color:#8b949e;margin-left:8px">&#9790; {d_sign} &middot; {d_nak}</span>'
                    f'<div style="font-size:.75rem;color:#8b949e;margin-top:2px">{d_desc}</div>'
                    f'</div>'
                    f'<div style="width:10px;height:10px;border-radius:50%;background:{col};flex-shrink:0"></div>'
                    f'</div>'
                )
                st.markdown(html, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Weekly overview error: {e}")

        # ── Chandrashtama next 90 days ────────────────────────────────────────
        sec_title(T("sec_chandra"))
        st.markdown(f'<div class="info-box">Moon transits the 8th sign from your Rasi ({chart["rasi"]}) — this is your Chandrashtama sign: <b>{SIGNS[(rasi_idx+7)%12]}</b>. Avoid auspicious beginnings, major decisions, and surgeries during these ~2.5 day windows.</div>', unsafe_allow_html=True)
        try:
            with st.spinner("Calculating Chandrashtama dates..."):
                c_days = get_chandrashtama_days(rasi_idx, lat, lon_coord, tz_str, days=90)
            if c_days:
                for c in c_days:
                    now_loc   = datetime.now()
                    is_now    = c["start"] <= now_loc <= c["end"]
                    bg        = "#3d0000" if is_now else "#2d1a1a"
                    border    = "#ff4444" if is_now else "#f8514966"
                    c_start   = c["start"].strftime("%a, %d %b %Y  %I:%M %p")
                    c_end     = c["end"].strftime("%d %b  %I:%M %p")
                    c_sign    = c["sign"]
                    c_nak     = c["nakshatra"]
                    dur       = c["end"] - c["start"]
                    hrs       = int(dur.total_seconds() // 3600)
                    now_badge = '<span style="font-size:.65rem;background:#ff4444;color:#fff;padding:1px 6px;border-radius:8px;margin-left:6px">ACTIVE NOW</span>' if is_now else ""
                    html = (
                        f'<div style="background:{bg};border:1px solid {border};border-radius:8px;'
                        f'padding:.65rem 1rem;margin-bottom:.45rem;display:flex;align-items:center;gap:1rem">'
                        f'<div style="flex:1">'
                        f'<div style="font-size:.85rem;font-weight:600;color:#f85149">'
                        f'{c_start} &rarr; {c_end}{now_badge}'
                        f'</div>'
                        f'<div style="font-size:.75rem;color:#8b949e;margin-top:2px">'
                        f'&#9790; Moon in {c_sign} &middot; {c_nak} &middot; ~{hrs}h duration'
                        f'</div>'
                        f'</div></div>'
                    )
                    st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("No Chandrashtama periods found in next 90 days.")
        except Exception as e:
            st.warning(f"Chandrashtama calculation error: {e}")

    # ── TAB 10: Summary ───────────────────────────────────────────────────────
    with tabs[9]:
        sec_title(T("sec_summary"))
        data_rows = [
            ("Lagna (ascendant)", f"{chart['lagna']} ({chart['lagna_tamil']}) · {chart['lagna_degree']}°"),
            ("Lagna lord", f"{chart['lagna_lord']} in house {p[chart['lagna_lord']]['house']}"),
            ("Rasi (moon sign)", f"{chart['rasi']} ({chart['rasi_tamil']})"),
            ("Janma nakshatra", f"{chart['nakshatra']} · Pada {chart['pada']}"),
            ("Nakshatra lord", chart['nakshatra_lord']),
            ("Nakshatra deity", chart['nakshatra_deity']),
            ("Yoga Karaka", ", ".join(chart['yoga_karaka']) if chart['yoga_karaka'] else "None"),
            ("Current Mahadasha", f"{dasha['current']['lord']} · ends {dasha['current']['end'].strftime('%Y')}"),
            ("Current Antardasha", f"{dasha['current_antardasha']['lord']} · ends {dasha['current_antardasha']['end'].strftime('%b %Y')}"),
            ("Ayanamsa (Lahiri)", f"{chart['ayanamsa']}°"),
            ("Birth latitude/lon", f"{chart['lat']:.4f}° N, {chart['lon']:.4f}° E"),
            ("Timezone", chart['tz']),
        ]
        for k, v in data_rows:
            cols = st.columns([2, 3])
            cols[0].markdown(f'<div style="font-size:.78rem;color:#8b949e;padding:.3rem 0">{k}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div style="font-size:.82rem;color:#e2c887;padding:.3rem 0;font-weight:500">{v}</div>', unsafe_allow_html=True)

        sec_title(T("sec_all_planets"))
        rows = ""
        for nm in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
            pl = p[nm]
            ret = " ℞" if pl.get('retrograde') else ""
            dg  = f" · {pl['dignity']}" if pl.get('dignity') else ""
            rows += f"<tr><td style='padding:5px 8px;color:#e2c887'>{pl['symbol']} {nm}</td><td style='padding:5px 8px;color:#c9d1d9'>{pl['sign']}{ret}</td><td style='padding:5px 8px;color:#8b949e'>{pl['degree']}°</td><td style='padding:5px 8px;color:#58a6ff'>H{pl['house']}</td><td style='padding:5px 8px;color:#8b949e'>{pl['nakshatra']}{dg}</td></tr>"
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;font-size:.78rem">
          <thead><tr style="border-bottom:1px solid #30363d">
            <th style="padding:5px 8px;text-align:left;color:#8b949e">Planet</th>
            <th style="padding:5px 8px;text-align:left;color:#8b949e">Sign</th>
            <th style="padding:5px 8px;text-align:left;color:#8b949e">Degree</th>
            <th style="padding:5px 8px;text-align:left;color:#8b949e">House</th>
            <th style="padding:5px 8px;text-align:left;color:#8b949e">Nakshatra</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)


# ── Main UI ────────────────────────────────────────────────────────────────────
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ── Language toggle + Hero ─────────────────────────────────────────────────────
col_hero, col_lang = st.columns([5, 1])
with col_hero:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-icon">🔯</div>
      <h1>{T("app_title")}</h1>
      <p>{T("app_sub")}</p>
    </div>""", unsafe_allow_html=True)
with col_lang:
    st.markdown("<div style='padding-top:1.25rem'></div>", unsafe_allow_html=True)
    lang_choice = st.selectbox(
        "🌐", ["English", "தமிழ்"],
        index=0 if st.session_state.lang == "English" else 1,
        label_visibility="collapsed",
        key="lang_selector"
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

if st.session_state.chart_data is None:
    with st.form("birth_form"):
        c1, c2 = st.columns(2)
        with c1:
            inp_name   = st.text_input(T("full_name"), placeholder="e.g. Hari Vardhan")
            inp_dob    = st.date_input(T("dob"),
                                       value=date(1990, 6, 15),
                                       min_value=date(1900,1,1),
                                       max_value=date.today())
            inp_pob    = st.text_input(T("pob"), placeholder="e.g. Cuddalore, Tamil Nadu, India")
        with c2:
            inp_tob    = st.text_input(T("tob"), placeholder="e.g. 14:30  or  06:15")
            inp_gender = st.selectbox(T("gender"),
                                      ["", T("male"), T("female"), T("other")],
                                      format_func=lambda x: T("select") if x=="" else x)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption(T("tob_hint"))

        go = st.form_submit_button(T("generate"))

    if go:
        if not inp_name.strip():
            st.error(T("full_name") + " — required." if not is_tamil() else "முழு பெயர் தேவை.")
        elif not inp_pob.strip():
            st.error(T("pob") + " — required." if not is_tamil() else "பிறந்த இடம் தேவை.")
        else:
            tob_parsed = None
            if inp_tob.strip():
                try:
                    h, m = inp_tob.strip().split(":")
                    tob_parsed = time(int(h), int(m))
                except Exception:
                    st.warning("Time not recognised — using 12:00 noon." if not is_tamil() else "நேரம் புரியவில்லை — 12:00 மதியம் பயன்படுத்துகிறோம்.")

            dob_dt = datetime.combine(
                inp_dob,
                tob_parsed if tob_parsed else time(12, 0)
            )

            with st.spinner(T("casting")):
                try:
                    chart  = cast_chart(dob_dt, inp_pob.strip())
                    dasha  = compute_dasha(chart, dob_dt)
                    yogas  = detect_yogas(chart)
                    st.session_state.chart_data = {
                        "chart": chart, "dasha": dasha, "yogas": yogas,
                        "name": inp_name.strip(),
                        "dob": inp_dob, "tob": tob_parsed, "pob": inp_pob.strip(),
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Tip: Try adding the country to the place of birth (e.g. 'Cuddalore, Tamil Nadu, India')." if not is_tamil() else "குறிப்பு: இடத்தோடு நாட்டையும் சேர்க்கவும் (எ.கா. 'Cuddalore, Tamil Nadu, India').")

else:
    d = st.session_state.chart_data
    render_reading(d["chart"], d["dasha"], d["yogas"],
                   d["name"], d["dob"], d["tob"], d["pob"])
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🔄  {T('new_reading_btn')}"):
        st.session_state.chart_data = None
        st.rerun()
