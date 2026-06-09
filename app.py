"""
app.py — Vedic Astrology Reading App
Full chart calculation using Swiss Ephemeris (Lahiri ayanamsa).
No API key required — all astrology logic is built-in.
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
        "🌟 Overview", "🪐 Planets", "🏠 Houses",
        "⏳ Dasha", "💼 Career", "💞 Relationships",
        "⚖️ Yogas", "🧿 Remedies", "📅 Panchang", "📊 Summary"
    ])

    # ── TAB 1: Overview ───────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="metric-row">' + "".join([
            metric(chart['lagna_tamil'], "Lagna (ascendant)"),
            metric(chart['rasi_tamil'],  "Rasi (moon sign)"),
            metric(chart['nakshatra'],   "Janma nakshatra"),
            metric(f"Pada {chart['pada']}", "Nakshatra pada"),
        ]) + '</div>', unsafe_allow_html=True)

        st.markdown('<div class="metric-row">' + "".join([
            metric(chart['lagna_lord'],           "Lagna lord"),
            metric(chart['nakshatra_lord'],        "Nakshatra lord"),
            metric(chart['lagna_element'],         "Element"),
            metric(f"{chart['ayanamsa']}°",        "Lahiri ayanamsa"),
        ]) + '</div>', unsafe_allow_html=True)

        sec_title("Lagna — ascendant personality")
        reading_text(LAGNA_DESC.get(chart['lagna'], ''))

        sec_title(f"Rasi — {chart['rasi']} moon sign")
        reading_text(RASI_DESC.get(chart['rasi'], ''))

        sec_title(f"Janma nakshatra — {chart['nakshatra']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card">
              <div class="sec-title">Star profile</div>
              <div class="reading-text">
                <b style="color:#e2c887">Deity:</b> {chart['nakshatra_deity']}<br>
                <b style="color:#e2c887">Symbol:</b> {chart['nakshatra_symbol']}<br>
                <b style="color:#e2c887">Lord:</b> {chart['nakshatra_lord']}<br>
                <b style="color:#e2c887">Quality:</b> {chart['nakshatra_quality']}<br>
                <b style="color:#e2c887">Pada:</b> {chart['pada']}
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card">
              <div class="sec-title">Nakshatra meaning</div>
              <div class="reading-text">{NAK_DESC.get(chart['nakshatra'], '')}</div>
            </div>""", unsafe_allow_html=True)

        yk = chart.get('yoga_karaka', [])
        if yk:
            info_box(f"⭐ <b>Yoga Karaka:</b> {', '.join(yk)} — the most powerful benefic planet(s) for {chart['lagna']} lagna. Their Dasha periods bring exceptional career and wealth results.")

    # ── TAB 2: Planets ────────────────────────────────────────────────────────
    with tabs[1]:
        sec_title("Navagraha placements (Lahiri sidereal)")
        for name_p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
            pl = p[name_p]
            sym   = pl['symbol']
            color = pl.get('color','#888')
            ret   = '<span class="p-ret">℞ Retrograde</span>' if pl.get('retrograde') else ''
            dg    = pl.get('dignity','')
            dg_cls = {'Exalted ↑':'dg-ex','Debilitated ↓':'dg-db','Own sign ★':'dg-own','Friendly +':'dg-fr'}.get(dg,'')
            dg_html = f'<span class="p-dignity {dg_cls}">{dg}</span>' if dg else ''
            house_theme = HOUSE_THEMES[pl['house']-1]

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
        sec_title("12 houses — whole-sign system from lagna")
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

        st.markdown('<div class="metric-row">' + "".join([
            metric(f"{d['lord']} Mahadasha", "Current period"),
            metric(d['start'].strftime('%Y'), "Started"),
            metric(d['end'].strftime('%Y'),   "Ends"),
            metric(f"{d['years']} yrs",        "Duration"),
        ]) + '</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="dasha-block current dasha-cur">
          <div class="dasha-name">{d['symbol']} {d['lord']} Mahadasha</div>
          <div class="dasha-period">{d['start'].strftime('%b %Y')} — {d['end'].strftime('%b %Y')}</div>
          <div class="dasha-text">{DASHA_EFFECTS.get(d['lord'],'')}</div>
        </div>""", unsafe_allow_html=True)

        sec_title(f"Current antardasha — {ad['lord']} within {d['lord']} Mahadasha")
        st.markdown(f"""
        <div class="dasha-block">
          <div class="dasha-name" style="color:#79c0ff">{ad['symbol']} {ad['lord']} Antardasha</div>
          <div class="dasha-period">{ad['start'].strftime('%b %Y')} — {ad['end'].strftime('%b %Y')}</div>
          <div class="dasha-text">{DASHA_EFFECTS.get(ad['lord'],'')}</div>
        </div>""", unsafe_allow_html=True)

        sec_title("Full Vimshottari timeline")
        now = datetime.now()
        for d_item in dasha['timeline']:
            is_cur = d_item['start'] <= now <= d_item['end']
            cls = "dasha-block current dasha-cur" if is_cur else "dasha-block"
            nc  = f'<span style="font-size:.65rem;background:#2a1f0a;color:#e2c887;padding:1px 6px;border-radius:8px;margin-left:8px">NOW</span>' if is_cur else ''
            st.markdown(f"""
            <div class="{cls}">
              <div class="dasha-name">{d_item['symbol']} {d_item['lord']} Mahadasha{nc}</div>
              <div class="dasha-period">{d_item['start'].strftime('%Y')} — {d_item['end'].strftime('%Y')} · {d_item['years']} years</div>
              <div class="dasha-text">{DASHA_EFFECTS.get(d_item['lord'],'')}</div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 5: Career ─────────────────────────────────────────────────────────
    with tabs[4]:
        sec_title("Career house analysis")
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

        sec_title("Best career fields for your lagna")
        fields = CAREER_INDICATORS.get(chart['lagna'], ['Versatile — many fields suit this chart'])
        for f in fields:
            st.markdown(f'<div class="reading-text">• {f}</div>', unsafe_allow_html=True)

        sec_title("Yoga Karaka and career wealth")
        yk = chart.get('yoga_karaka', [])
        if yk:
            for y in yk:
                yp = p[y]
                reading_text(f"<b style='color:#e2c887'>{y}</b> is your Yoga Karaka — placed in house {yp['house']} ({yp['sign']}). "
                             f"Its Dasha period is your peak career and wealth window. "
                             f"Current Dasha: {dasha['current']['lord']}. "
                             f"Yoga Karaka Dasha starts: {next((d_item['start'].strftime('%Y') for d_item in dasha['timeline'] if d_item['lord']==y), 'see timeline')}.")

        sec_title("Wealth house lords")
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

        sec_title("Marriage and partnership analysis")
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

        sec_title("Venus — the natural significator of marriage")
        ven = p['Venus']
        reading_text(f"Venus is in <b>{ven['sign']}</b>, house <b>{ven['house']}</b>, nakshatra <b>{ven['nakshatra']}</b>. "
                     f"Dignity: {ven.get('dignity','Neutral')}. Venus placement reveals the aesthetic of relationships and the kind of partner attracted.")

        sec_title("Spouse indicators")
        reading_text(f"7th lord <b>{h7_lord}</b> in house {p[h7_lord]['house']} ({p[h7_lord]['sign']}) "
                     f"suggests the partner will carry themes of the {p[h7_lord]['house']}th house — {HOUSE_THEMES[p[h7_lord]['house']-1]}.")

    # ── TAB 7: Yogas ─────────────────────────────────────────────────────────
    with tabs[6]:
        sec_title("Yogas and doshas detected in your chart")
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
        sec_title("Planetary remedies for your chart")
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

        sec_title("Universal daily practices")
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
        sec_title("Today's kalam timings — avoid for new starts")
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

            kalam_rows = [
                ('☀️ Abhijit Muhurta',  ab_s,  ab_e,  '#56d364','#0d2010', 'Best time of day — solar noon window, universally auspicious.'),
                ('☊ Rahu Kalam',        rk_s,  rk_e,  '#f85149','#2d1a1a', 'Avoid starting anything new. Ongoing work is fine.'),
                ('⚰ Yamagandam',        yg_s,  yg_e,  '#f85149','#2d1a1a', 'Death time of Yama. No new ventures, travel, or money dealings.'),
                ('♄ Gulika Kalam',      gk_s,  gk_e,  '#e3b341','#1e1600', 'Saturn\'s hour — activities repeat. Avoid loans and funeral rites.'),
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
        sec_title("Best windows today for important activities")
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
        sec_title("14-day lunar calendar for your Rasi")
        try:
            overview = get_weekly_overview(rasi_idx, lat, lon_coord, tz_str)
            for day in overview:
                q   = day['quality']
                col = {'good':'#56d364','neutral':'#e3b341','bad':'#f85149'}.get(q,'#8b949e')
                bg  = {'good':'#0d2010','neutral':'#1e1600','bad':'#2d1a1a'}.get(q,'#161b22')
                chandra_badge = '<span style="font-size:.65rem;background:#2d1a1a;color:#f85149;padding:1px 6px;border-radius:8px;margin-left:6px">Chandrashtama</span>' if day['is_chandrashtama'] else ''
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {col}33;border-radius:8px;
                  padding:.55rem 1rem;margin-bottom:.4rem;
                  display:flex;align-items:center;gap:1rem">
                  <div style="width:44px;text-align:center;flex-shrink:0">
                    <div style="font-size:.78rem;font-weight:600;color:{col}">{day['day']}</div>
                    <div style="font-size:.7rem;color:#8b949e">{day['date'].strftime('%d %b')}</div>
                  </div>
                  <div style="flex:1">
                    <span style="font-size:.82rem;font-weight:600;color:{col}">{day['name']}</span>
                    {chandra_badge}
                    <span style="font-size:.72rem;color:#8b949e;margin-left:8px">☽ {day['sign']} · {day['nakshatra']}</span>
                    <div style="font-size:.75rem;color:#8b949e;margin-top:2px">{day['desc']}</div>
                  </div>
                  <div style="width:10px;height:10px;border-radius:50%;background:{col};flex-shrink:0"></div>
                </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Weekly overview error: {e}")

        # ── Chandrashtama next 90 days ────────────────────────────────────────
        sec_title("Chandrashtama days — next 90 days")
        st.markdown(f'<div class="info-box">Moon transits the 8th sign from your Rasi ({chart["rasi"]}) — this is your Chandrashtama sign: <b>{SIGNS[(rasi_idx+7)%12]}</b>. Avoid auspicious beginnings, major decisions, and surgeries during these ~2.5 day windows.</div>', unsafe_allow_html=True)
        try:
            with st.spinner("Calculating Chandrashtama dates..."):
                c_days = get_chandrashtama_days(rasi_idx, lat, lon_coord, tz_str, days=90)
            if c_days:
                for c in c_days:
                    now_loc = datetime.now()
                    is_now  = c['start'] <= now_loc <= c['end']
                    bg = '#3d0000' if is_now else '#2d1a1a'
                    border = '#ff4444' if is_now else '#f8514966'
                    now_badge = '<span style="font-size:.65rem;background:#ff4444;color:#fff;padding:1px 6px;border-radius:8px;margin-left:6px">ACTIVE NOW</span>' if is_now else ''
                    dur = c['end'] - c['start']
                    hrs = int(dur.total_seconds()//3600)
                    st.markdown(f"""
                    <div style="background:{bg};border:1px solid {border};border-radius:8px;
                      padding:.65rem 1rem;margin-bottom:.45rem;display:flex;align-items:center;gap:1rem">
                      <div style="flex:1">
                        <div style="font-size:.85rem;font-weight:600;color:#f85149">
                          {c['start'].strftime('%a, %d %b %Y  %I:%M %p')} → {c['end'].strftime('%d %b  %I:%M %p')}
                          {now_badge}
                        </div>
                        <div style="font-size:.75rem;color:#8b949e;margin-top:2px">
                          ☽ Moon in {c['sign']} · {c['nakshatra']} · ~{hrs}h duration
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No Chandrashtama periods found in next 90 days.")
        except Exception as e:
            st.warning(f"Chandrashtama calculation error: {e}")

    # ── TAB 10: Summary ───────────────────────────────────────────────────────
    with tabs[9]:
        sec_title("Complete chart summary at a glance")
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

        sec_title("All planetary positions")
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
st.markdown("""
<div class="hero">
  <div class="hero-icon">🔯</div>
  <h1>Vedic Astrology Reading</h1>
  <p>South Indian Jathagam · Swiss Ephemeris · Lahiri ayanamsa · No API key required</p>
</div>""", unsafe_allow_html=True)

if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

if st.session_state.chart_data is None:
    with st.form("birth_form"):
        c1, c2 = st.columns(2)
        with c1:
            inp_name   = st.text_input("Full name", placeholder="e.g. Hari Vardhan")
            inp_dob    = st.date_input("Date of birth",
                                       value=date(1990, 6, 15),
                                       min_value=date(1900,1,1),
                                       max_value=date.today())
            inp_pob    = st.text_input("Place of birth", placeholder="e.g. Cuddalore, Tamil Nadu, India")
        with c2:
            inp_tob    = st.text_input("Time of birth (HH:MM 24h)", placeholder="e.g. 14:30  or  06:15")
            inp_gender = st.selectbox("Gender", ["","Male","Female","Other"],
                                      format_func=lambda x: "Select" if x=="" else x)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Time of birth significantly improves Lagna accuracy. Use 12:00 if unknown.")

        go = st.form_submit_button("✨  Generate reading")

    if go:
        if not inp_name.strip():
            st.error("Please enter your full name.")
        elif not inp_pob.strip():
            st.error("Please enter your place of birth.")
        else:
            tob_parsed = None
            if inp_tob.strip():
                try:
                    h, m = inp_tob.strip().split(":")
                    tob_parsed = time(int(h), int(m))
                except Exception:
                    st.warning("Time not recognised — using 12:00 noon.")

            dob_dt = datetime.combine(
                inp_dob,
                tob_parsed if tob_parsed else time(12, 0)
            )

            with st.spinner("Casting chart with Swiss Ephemeris…"):
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
                    st.info("Tip: Try adding the country to the place of birth (e.g. 'Cuddalore, Tamil Nadu, India').")

else:
    d = st.session_state.chart_data
    render_reading(d["chart"], d["dasha"], d["yogas"],
                   d["name"], d["dob"], d["tob"], d["pob"])
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄  New reading"):
        st.session_state.chart_data = None
        st.rerun()
