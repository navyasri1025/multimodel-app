import json
import streamlit as st
import streamlit.components.v1 as components
from concurrent.futures import ThreadPoolExecutor, as_completed
from main import ask, MODELS

st.set_page_config(
    page_title="Multi-Model Comparison Tool",
    page_icon="🚀",
    layout="wide",
)

# ── Session state ──────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── CSS custom properties: dark (default) ───────────────────────── */
:root {
    --bg-app:           linear-gradient(160deg, #0d1117 0%, #161b22 100%);
    --bg-card:          #161b22;
    --bg-input:         #0d1117;
    --bg-metric:        #161b22;
    --bg-err:           #160b0b;
    --c-border:         #30363d;
    --c-err-bdr:        #5a1e1e;
    --c-err-top:        #ef4444;
    --c-err-text:       #ef4444;
    --c-err-pill:       rgba(239,68,68,0.12);
    --c-text1:          #e6edf3;
    --c-text2:          #c9d1d9;
    --c-text3:          #6e7681;
    --c-divider:        #21262d;
    --c-statrow:        #1c2128;
    --c-scroll:         #2d333b;
    --c-scroll-hov:     #3d444d;
    --c-banner-sub:     #8b949e;
    --c-pill-blue-bg:   rgba(59,130,246,0.12);
    --c-pill-blue:      #3b82f6;
    --c-pill-green-bg:  rgba(34,197,94,0.12);
    --c-pill-green:     #22c55e;
    --c-pill-orange-bg: rgba(249,115,22,0.12);
    --c-pill-orange:    #f97316;
    --c-pill-purple-bg: rgba(168,85,247,0.12);
    --c-pill-purple:    #a855f7;
    --shadow-card:      none;
}

/* ── Light theme overrides ───────────────────────────────────────── */
[data-theme="light"] {
    --bg-app:           linear-gradient(160deg, #f0f4f8 0%, #ffffff 100%);
    --bg-card:          #ffffff;
    --bg-input:         #ffffff;
    --bg-metric:        #f6f8fa;
    --bg-err:           #fff2f2;
    --c-border:         #d0d7de;
    --c-err-bdr:        rgba(207,34,46,0.2);
    --c-err-top:        #cf222e;
    --c-err-text:       #cf222e;
    --c-err-pill:       rgba(207,34,46,0.08);
    --c-text1:          #0d1117;
    --c-text2:          #24292f;
    --c-text3:          #57606a;
    --c-divider:        #d0d7de;
    --c-statrow:        #eaeef2;
    --c-scroll:         #c8d0d8;
    --c-scroll-hov:     #b0bac4;
    --c-banner-sub:     #57606a;
    --c-pill-blue-bg:   rgba(9,105,218,0.08);
    --c-pill-blue:      #0969da;
    --c-pill-green-bg:  rgba(26,127,55,0.08);
    --c-pill-green:     #1a7f37;
    --c-pill-orange-bg: rgba(130,80,11,0.08);
    --c-pill-orange:    #7d4e00;
    --c-pill-purple-bg: rgba(130,80,214,0.08);
    --c-pill-purple:    #6639ba;
    --shadow-card:      0 2px 10px rgba(0,0,0,0.07);
}

/* ── Base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"], [data-testid] {
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: var(--bg-app) !important;
    transition: background 0.3s ease !important;
}
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] { display: none; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px;
}

/* ── Banner ──────────────────────────────────────────────────────── */
.banner {
    text-align: center;
    padding: 2.6rem 1rem 2rem 1rem;
    margin-bottom: 1.6rem;
}
.banner-title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 50%, #ff7b72 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}
.banner-sub {
    font-size: 17px;
    color: var(--c-banner-sub);
    margin: 0;
    font-weight: 400;
    transition: color 0.3s ease;
}

/* ── Inputs ──────────────────────────────────────────────────────── */
label, .stTextArea label, .stMultiSelect label {
    color: var(--c-text1) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    transition: color 0.3s ease !important;
}
textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--c-border) !important;
    color: var(--c-text1) !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease !important;
}
textarea:focus { border-color: #58a6ff !important; }
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border-color: var(--c-border) !important;
    border-radius: 10px !important;
    color: var(--c-text1) !important;
    transition: background 0.3s ease, border-color 0.3s ease !important;
}
[data-baseweb="popover"] [data-baseweb="menu"] {
    background: var(--bg-card) !important;
    border-color: var(--c-border) !important;
}
[data-baseweb="option"] {
    background: var(--bg-card) !important;
    color: var(--c-text1) !important;
}

/* ── Compare button ──────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #1f6feb, #388bfd) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.7rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border-radius: 30px !important;
    box-shadow: 0 4px 20px rgba(31,111,235,0.35) !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

/* ── Summary metrics ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-metric) !important;
    border: 1px solid var(--c-border) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.1rem !important;
    transition: background 0.3s ease, border-color 0.3s ease !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--c-text3) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    transition: color 0.3s ease !important;
}
[data-testid="stMetricValue"] {
    color: var(--c-text1) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    transition: color 0.3s ease !important;
}

/* ── Model cards ─────────────────────────────────────────────────── */
.model-card {
    background: var(--bg-card);
    border: 1px solid var(--c-border);
    border-radius: 16px;
    padding: 1.4rem 1.4rem 1.2rem 1.4rem;
    height: 520px;
    display: flex;
    flex-direction: column;
    border-top-width: 3px;
    border-top-style: solid;
    margin-bottom: 0.5rem;
    box-shadow: var(--shadow-card);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease,
                background-color 0.3s ease;
}
.model-card:hover { transform: translateY(-4px); }
.card-blue   { border-top-color: #3b82f6; }
.card-green  { border-top-color: #22c55e; }
.card-orange { border-top-color: #f97316; }
.card-purple { border-top-color: #a855f7; }
.card-blue:hover   { border-color: #3b82f6; box-shadow: 0 8px 32px rgba(59,130,246,0.18); }
.card-green:hover  { border-color: #22c55e; box-shadow: 0 8px 32px rgba(34,197,94,0.18); }
.card-orange:hover { border-color: #f97316; box-shadow: 0 8px 32px rgba(249,115,22,0.18); }
.card-purple:hover { border-color: #a855f7; box-shadow: 0 8px 32px rgba(168,85,247,0.18); }

.card-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border-radius: 20px;
    padding: 0.22rem 0.8rem;
    margin-bottom: 0.55rem;
    transition: background 0.3s ease, color 0.3s ease;
}
.badge-blue   { background: var(--c-pill-blue-bg);   color: var(--c-pill-blue); }
.badge-green  { background: var(--c-pill-green-bg);  color: var(--c-pill-green); }
.badge-orange { background: var(--c-pill-orange-bg); color: var(--c-pill-orange); }
.badge-purple { background: var(--c-pill-purple-bg); color: var(--c-pill-purple); }

.card-info { display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 1rem; }
.card-info-row {
    font-size: 0.76rem;
    color: var(--c-text3);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.35rem;
    transition: color 0.3s ease;
}
.card-info-row span.ci-icon { font-size: 0.78rem; }

/* ── Answer area ─────────────────────────────────────────────────── */
.card-answer {
    font-size: 0.88rem;
    color: var(--c-text2);
    line-height: 1.75;
    overflow-y: auto;
    flex: 1;
    min-height: 0;
    padding-right: 8px;
    margin-bottom: 1rem;
    transition: color 0.3s ease;
}
.card-answer::-webkit-scrollbar { width: 3px; }
.card-answer::-webkit-scrollbar-track { background: transparent; }
.card-answer::-webkit-scrollbar-thumb {
    background: var(--c-scroll);
    border-radius: 4px;
}
.card-answer::-webkit-scrollbar-thumb:hover { background: var(--c-scroll-hov); }

.card-rule {
    border: none;
    border-top: 1px solid var(--c-divider);
    margin: 0 0 0.85rem 0;
    flex-shrink: 0;
    transition: border-color 0.3s ease;
}

/* ── Flat metric rows ────────────────────────────────────────────── */
.stats-row { display: flex; flex-direction: column; gap: 0; flex-shrink: 0; }
.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.38rem 0;
    border-bottom: 1px solid var(--c-statrow);
    transition: border-color 0.3s ease;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { font-size: 0.73rem; color: var(--c-text3); font-weight: 500; transition: color 0.3s ease; }
.stat-value { font-size: 0.82rem; color: var(--c-text1); font-weight: 600; transition: color 0.3s ease; }

/* ── Error card ──────────────────────────────────────────────────── */
.error-card {
    background: var(--bg-err);
    border: 1px solid var(--c-err-bdr);
    border-top: 3px solid var(--c-err-top);
    border-radius: 16px;
    padding: 1.3rem;
    height: 520px;
    display: flex;
    flex-direction: column;
    margin-bottom: 0.5rem;
    transition: background 0.3s ease, border-color 0.3s ease;
}
.error-badge {
    display: inline-block;
    background: var(--c-err-pill);
    color: var(--c-err-text);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border-radius: 20px;
    padding: 0.22rem 0.8rem;
    margin-bottom: 0.5rem;
    transition: background 0.3s ease, color 0.3s ease;
}
.error-reason {
    font-size: 0.85rem;
    color: var(--c-err-text);
    margin-top: 0.4rem;
    font-family: 'SFMono-Regular', monospace;
    word-break: break-word;
    line-height: 1.5;
    transition: color 0.3s ease;
}

/* ── Divider ─────────────────────────────────────────────────────── */
hr { border-color: var(--c-divider) !important; margin: 1rem 0 !important; transition: border-color 0.3s ease !important; }
</style>
""", unsafe_allow_html=True)

MODEL_META = {
    "openai/gpt-4o-mini": {
        "color": "blue", "emoji": "🔵", "label": "GPT-4o Mini",
        "info": [("⚡", "Fast"), ("💰", "Low Cost"), ("🧠", "Good Reasoning")],
    },
    "meta-llama/llama-3.3-70b-instruct": {
        "color": "green", "emoji": "🟢", "label": "Llama 3.3 70B",
        "info": [("⚡", "Medium"), ("💰", "Medium Cost"), ("🧠", "Excellent Coding")],
    },
    "mistralai/mistral-large-2512": {
        "color": "orange", "emoji": "🟠", "label": "Mistral Large 3",
        "info": [("⚡", "Medium"), ("💰", "Higher Cost"), ("🧠", "Strong Reasoning")],
    },
    "qwen/qwen-2.5-72b-instruct": {
        "color": "purple", "emoji": "🟣", "label": "Qwen 2.5 72B",
        "info": [("⚡", "Medium"), ("💰", "Medium Cost"), ("🧠", "Excellent Math & Coding")],
    },
}

# ── Theme toggle (injected into parent document via 0-height iframe) ───────────
def inject_theme_toggle() -> None:
    components.html("""
<script>
(function() {
  var p = window.parent;
  var d = p.document;

  // Read saved theme
  var theme = 'dark';
  try { theme = p.localStorage.getItem('ma-theme') || 'dark'; } catch(e) {}

  // Apply to document immediately so there's no flash
  d.documentElement.setAttribute('data-theme', theme);

  // Tear down any previous toggle instance (Streamlit reruns this)
  ['ma-toggle', 'ma-toggle-wrap', 'ma-toggle-style'].forEach(function(id) {
    var el = d.getElementById(id);
    if (el) el.remove();
  });

  // ── Stylesheet ──────────────────────────────────────────────────
  var css = d.createElement('style');
  css.id = 'ma-toggle-style';
  css.textContent = [
    '#ma-toggle-wrap {',
    '  position: fixed;',
    '  top: 12px;',
    '  left: 16px;',
    '  z-index: 99999;',
    '}',

    '#ma-pill {',
    '  position: relative;',
    '  display: flex;',
    '  align-items: center;',
    '  padding: 3px;',
    '  border-radius: 50px;',
    '  border: 1px solid #30363d;',
    '  background: #0d1117;',
    '  box-shadow:',
    '    0 2px 16px rgba(0,0,0,0.45),',
    '    inset 0 1px 0 rgba(255,255,255,0.04);',
    '  transition:',
    '    background 0.3s ease,',
    '    border-color 0.3s ease,',
    '    box-shadow 0.3s ease;',
    '}',
    '#ma-pill.lm {',
    '  background: #f6f8fa;',
    '  border-color: #d0d7de;',
    '  box-shadow:',
    '    0 2px 12px rgba(0,0,0,0.08),',
    '    inset 0 1px 0 rgba(255,255,255,0.9);',
    '}',

    /* sliding indicator */
    '#ma-ind {',
    '  position: absolute;',
    '  top: 3px;',
    '  border-radius: 44px;',
    '  background: #21262d;',
    '  box-shadow:',
    '    0 1px 8px rgba(0,0,0,0.5),',
    '    0 0 0 1px rgba(255,255,255,0.06),',
    '    0 0 14px rgba(88,166,255,0.10);',
    '  pointer-events: none;',
    '  transition:',
    '    left 0.3s cubic-bezier(0.4,0,0.2,1),',
    '    width 0.3s cubic-bezier(0.4,0,0.2,1),',
    '    background 0.3s ease,',
    '    box-shadow 0.3s ease;',
    '}',
    '#ma-pill.lm #ma-ind {',
    '  background: #ffffff;',
    '  box-shadow:',
    '    0 1px 8px rgba(0,0,0,0.12),',
    '    0 0 0 1px rgba(0,0,0,0.06),',
    '    0 0 12px rgba(9,105,218,0.08);',
    '}',

    /* segment buttons */
    '.ma-seg {',
    '  position: relative;',
    '  z-index: 2;',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 5px;',
    '  padding: 6px 14px;',
    '  border-radius: 44px;',
    '  border: none;',
    '  background: transparent;',
    '  cursor: pointer;',
    '  font-size: 11px;',
    '  font-weight: 600;',
    '  letter-spacing: 0.03em;',
    '  color: #484f58;',
    '  font-family: Inter,-apple-system,BlinkMacSystemFont,sans-serif;',
    '  white-space: nowrap;',
    '  user-select: none;',
    '  transition: color 0.25s ease;',
    '}',
    '.ma-seg:focus-visible {',
    '  outline: 2px solid #58a6ff;',
    '  outline-offset: 2px;',
    '}',
    '.ma-seg .ma-ico { font-size: 13px; line-height: 1; }',

    /* inactive hover */
    '#ma-pill:not(.lm) .ma-seg:hover { color: #8b949e; }',
    '#ma-pill.lm .ma-seg { color: #8c959f; }',
    '#ma-pill.lm .ma-seg:hover { color: #57606a; }',

    /* active label */
    '.ma-seg.on { color: #e6edf3; }',
    '#ma-pill.lm .ma-seg.on { color: #0d1117; }',
  ].join('\n');
  d.head.appendChild(css);

  // ── DOM structure ────────────────────────────────────────────────
  var wrap = d.createElement('div');
  wrap.id = 'ma-toggle-wrap';
  wrap.setAttribute('role', 'group');
  wrap.setAttribute('aria-label', 'Theme selector');

  var pill = d.createElement('div');
  pill.id = 'ma-pill';
  if (theme === 'light') pill.classList.add('lm');

  var ind = d.createElement('div');
  ind.id = 'ma-ind';
  pill.appendChild(ind);

  function makeBtn(icon, label, value) {
    var b = d.createElement('button');
    b.className = 'ma-seg' + (theme === value ? ' on' : '');
    b.setAttribute('aria-label', label);
    b.setAttribute('aria-pressed', String(theme === value));
    b.dataset.value = value;
    b.innerHTML =
      '<span class="ma-ico" aria-hidden="true">' + icon + '</span>' +
      '<span>' + label + '</span>';
    return b;
  }

  var lightBtn = makeBtn('☀️', 'Light', 'light');
  var darkBtn  = makeBtn('🌙', 'Dark',  'dark');
  pill.appendChild(lightBtn);
  pill.appendChild(darkBtn);
  wrap.appendChild(pill);
  d.body.appendChild(wrap);

  // ── Indicator positioning ────────────────────────────────────────
  function moveIndicator(activeBtn) {
    ind.style.left   = activeBtn.offsetLeft + 'px';
    ind.style.width  = activeBtn.offsetWidth + 'px';
    ind.style.height = activeBtn.offsetHeight + 'px';
  }

  // Defer one frame so layout is complete
  requestAnimationFrame(function() {
    moveIndicator(theme === 'light' ? lightBtn : darkBtn);
  });

  // ── Apply theme ──────────────────────────────────────────────────
  function applyTheme(next) {
    d.documentElement.setAttribute('data-theme', next);
    try { p.localStorage.setItem('ma-theme', next); } catch(e) {}

    var isLight = next === 'light';
    pill.classList.toggle('lm', isLight);

    [lightBtn, darkBtn].forEach(function(b) {
      var active = b.dataset.value === next;
      b.classList.toggle('on', active);
      b.setAttribute('aria-pressed', String(active));
    });

    moveIndicator(isLight ? lightBtn : darkBtn);

    // Broadcast to all child iframes (charts etc.)
    d.querySelectorAll('iframe').forEach(function(f) {
      try { f.contentWindow.postMessage({ maTheme: next }, '*'); } catch(e) {}
    });
  }

  lightBtn.addEventListener('click', function() { applyTheme('light'); });
  darkBtn.addEventListener('click',  function() { applyTheme('dark');  });
})();
</script>
""", height=0, scrolling=False)


# ── Skeleton HTML (shown while API calls run) ──────────────────────────────────
def build_skeleton_html(n: int) -> str:
    card = """
    <div style="height:520px;background:#161b22;border:1px solid #30363d;
                border-radius:16px;padding:1.3rem;border-top:3px solid #2d333b;overflow:hidden;">
      <div class="sh" style="height:22px;width:90px;border-radius:20px;margin-bottom:14px;"></div>
      <div class="sh" style="height:10px;width:55%;border-radius:4px;margin-bottom:6px;"></div>
      <div class="sh" style="height:10px;width:38%;border-radius:4px;margin-bottom:6px;"></div>
      <div class="sh" style="height:10px;width:46%;border-radius:4px;margin-bottom:22px;"></div>
      <div class="sh" style="height:200px;width:100%;border-radius:8px;margin-bottom:20px;"></div>
      <div style="border-top:1px solid #21262d;margin-bottom:16px;"></div>
      <div class="sh" style="height:12px;width:100%;border-radius:4px;margin-bottom:10px;"></div>
      <div class="sh" style="height:12px;width:100%;border-radius:4px;margin-bottom:10px;"></div>
      <div class="sh" style="height:12px;width:100%;border-radius:4px;"></div>
    </div>"""
    cols = "".join(f'<div>{card}</div>' for _ in range(n))
    return f"""
<style>
@keyframes sk {{
  0%   {{ background-position: -600px 0; }}
  100% {{ background-position:  600px 0; }}
}}
.sh {{
  background: linear-gradient(90deg, #1c2128 0%, #2d333b 50%, #1c2128 100%);
  background-size: 1200px 100%;
  animation: sk 1.4s ease infinite;
}}
</style>
<div style="display:grid;grid-template-columns:repeat({n},1fr);gap:1rem;margin:1rem 0;">
  {cols}
</div>"""


# ── Performance Analytics charts (Recharts via CDN) ────────────────────────────
_COLOR_MAP = {
    "openai/gpt-4o-mini":                "#3b82f6",
    "meta-llama/llama-3.3-70b-instruct": "#22c55e",
    "mistralai/mistral-large-2512":      "#f97316",
    "qwen/qwen-2.5-72b-instruct":        "#a855f7",
}

def render_charts(results: list) -> None:
    ok = [r for r in results if r and r["latency"] is not None]
    if not ok:
        return

    n = len(ok)
    chart_data = [
        {
            "name":         MODEL_META.get(r["model"], {}).get("label", r["model"]).split()[0],
            "full_name":    MODEL_META.get(r["model"], {}).get("label", r["model"]),
            "latency":      round(r["latency"], 3),
            "cost_display": round(r["cost"] * 1_000_000, 4),
            "tokens":       r["tokens"] or 0,
            "color":        _COLOR_MAP.get(r["model"], "#8b949e"),
        }
        for r in ok
    ]
    data_js = json.dumps(chart_data)

    def skel_card(heights):
        bars = "".join(
            f'<div class="sb" style="height:{h}%;animation-delay:{i*0.12:.2f}s"></div>'
            for i, h in enumerate(heights[:n])
        )
        return f'<div class="sk-card"><div class="sk-title"></div><div class="sk-bars">{bars}</div></div>'

    skeleton = (
        skel_card([62, 88, 44, 71]) +
        skel_card([50, 74, 91, 38]) +
        skel_card([73, 57, 80, 66])
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}

/* ── Theme tokens ── */
:root {{
  --bg:      #0d1117;
  --bg-card: #161b22;
  --c-bdr:   #30363d;
  --c-grid:  #21262d;
  --c-text3: #6e7681;
  --c-text1: #e6edf3;
  --c-tip-bg:#0d1117;
  --c-tip-bdr:#30363d;
}}
.light {{
  --bg:      #f0f4f8;
  --bg-card: #ffffff;
  --c-bdr:   #d0d7de;
  --c-grid:  #eaeef2;
  --c-text3: #57606a;
  --c-text1: #0d1117;
  --c-tip-bg:#ffffff;
  --c-tip-bdr:#d0d7de;
}}

html,body{{
  background:var(--bg);
  font-family:Inter,-apple-system,sans-serif;
  color:var(--c-text1);
  overflow:hidden;
  transition:background 0.3s ease;
}}

/* grid */
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:0 1px 2px;}}
@media(max-width:680px){{
  .grid{{grid-template-columns:repeat(2,1fr);}}
  .grid > *:last-child{{grid-column:1/-1;}}
}}
@media(max-width:400px){{.grid{{grid-template-columns:1fr;}}}}

/* Skeleton */
@keyframes sh{{0%{{background-position:-500px 0}}100%{{background-position:500px 0}}}}
.sk-card{{
  background:var(--bg-card);border:1px solid var(--c-bdr);border-radius:12px;
  padding:12px 12px 10px;height:220px;display:flex;flex-direction:column;
  transition:background 0.3s ease,border-color 0.3s ease;
}}
.sk-title{{
  height:9px;width:72px;border-radius:3px;margin-bottom:16px;
  background:linear-gradient(90deg,#1c2128,#2d333b,#1c2128);
  background-size:1000px;animation:sh 1.3s ease infinite;
}}
.sk-bars{{display:flex;align-items:flex-end;gap:10px;flex:1;padding:0 2px 2px;}}
.sb{{
  flex:1;border-radius:4px 4px 0 0;
  background:linear-gradient(90deg,#1c2128,#2d333b,#1c2128);
  background-size:1000px;animation:sh 1.3s ease infinite;
}}

/* Chart card */
.card{{
  background:var(--bg-card);border:1px solid var(--c-bdr);border-radius:12px;
  padding:12px 10px 4px 10px;height:220px;
  transition:background 0.3s ease,border-color 0.3s ease;
}}
.title{{
  font-size:10px;font-weight:700;color:var(--c-text3);
  letter-spacing:.07em;text-transform:uppercase;
  margin-bottom:8px;padding-left:2px;
  transition:color 0.3s ease;
}}

/* Tooltip */
.tip{{
  background:var(--c-tip-bg);border:1px solid var(--c-tip-bdr);border-radius:8px;
  padding:7px 11px;font-size:11px;line-height:1.55;pointer-events:none;
  transition:background 0.3s ease;
}}
.tip-name{{color:var(--c-text3);font-weight:500;margin-bottom:2px;}}
.tip-val{{font-weight:700;font-size:12px;}}
</style>
</head>
<body>

<div class="grid" id="skel">{skeleton}</div>
<div id="mount" style="display:none"></div>

<script>
const DATA = {data_js};

// Apply initial theme from parent localStorage
(function() {{
  try {{
    var t = window.parent.localStorage.getItem('ma-theme') || 'dark';
    if (t === 'light') document.body.classList.add('light');
  }} catch(e) {{}}
}})();

// Listen for theme changes from parent
window.addEventListener('message', function(ev) {{
  if (ev.data && ev.data.maTheme) {{
    if (ev.data.maTheme === 'light') document.body.classList.add('light');
    else document.body.classList.remove('light');
  }}
}});

function fitHeight() {{
  try {{ window.frameElement.style.height = (document.documentElement.scrollHeight + 2) + 'px'; }}
  catch(e) {{}}
}}

function load(src, cb) {{
  var s = document.createElement('script');
  s.src = src; s.crossOrigin = 'anonymous'; s.onload = cb;
  document.head.appendChild(s);
}}

load('https://unpkg.com/react@18/umd/react.production.min.js', function() {{
  load('https://unpkg.com/react-dom@18/umd/react-dom.production.min.js', function() {{
    load('https://unpkg.com/recharts@2.12.7/umd/Recharts.js', function() {{

      var R = window.Recharts;
      var e = React.createElement;

      function getCSS(name) {{
        return getComputedStyle(document.body).getPropertyValue(name).trim();
      }}

      function Tip(props) {{
        var active = props.active, payload = props.payload, unit = props.unit;
        if (!active || !payload || !payload.length) return null;
        var d = payload[0];
        return e('div', {{className:'tip'}},
          e('div', {{className:'tip-name'}}, d.payload.full_name),
          e('div', {{className:'tip-val', style:{{color:d.fill}}}}, d.value + ' ' + unit)
        );
      }}

      function Chart(props) {{
        var title = props.title, dataKey = props.dataKey, unit = props.unit;
        var gridColor = getCSS('--c-grid') || '#21262d';
        var tickColor = getCSS('--c-text3') || '#6e7681';
        return e('div', {{className:'card'}},
          e('div', {{className:'title'}}, title),
          e(R.ResponsiveContainer, {{width:'100%', height:178}},
            e(R.BarChart, {{
              data: DATA,
              margin: {{top:4, right:8, left:-22, bottom:0}},
              barCategoryGap: '36%'
            }},
              e(R.CartesianGrid, {{strokeDasharray:'3 3', stroke:gridColor, vertical:false}}),
              e(R.XAxis, {{
                dataKey: 'name',
                tick: {{fill:tickColor, fontSize:11}},
                axisLine: false, tickLine: false
              }}),
              e(R.YAxis, {{
                tick: {{fill:tickColor, fontSize:11}},
                axisLine: false, tickLine: false, width: 44
              }}),
              e(R.Tooltip, {{
                cursor: {{fill:'rgba(128,128,128,0.08)'}},
                content: function(p) {{ return e(Tip, Object.assign({{}}, p, {{unit:unit}})); }}
              }}),
              e(R.Bar, {{
                dataKey: dataKey,
                radius: [5,5,0,0],
                maxBarSize: 48,
                animationDuration: 650,
                animationEasing: 'ease-out'
              }},
                DATA.map(function(d,i){{ return e(R.Cell, {{key:i, fill:d.color}}); }})
              )
            )
          )
        );
      }}

      function App() {{
        React.useEffect(function() {{
          requestAnimationFrame(function() {{ setTimeout(fitHeight, 60); }});
          window.addEventListener('resize', fitHeight);
          return function() {{ window.removeEventListener('resize', fitHeight); }};
        }}, []);
        return e('div', {{className:'grid'}},
          e(Chart, {{title:'⚡ Latency',  dataKey:'latency',      unit:'s'}}),
          e(Chart, {{title:'💰 Cost',     dataKey:'cost_display', unit:'µ$'}}),
          e(Chart, {{title:'🔤 Tokens',   dataKey:'tokens',       unit:'tok'}})
        );
      }}

      document.getElementById('skel').style.display = 'none';
      var mount = document.getElementById('mount');
      mount.style.display = 'block';
      ReactDOM.createRoot(mount).render(e(App, null));
    }});
  }});
}});
</script>
</body>
</html>"""

    components.html(html, height=228, scrolling=False)


# ── Inject theme toggle ────────────────────────────────────────────────────────
inject_theme_toggle()

# ── Banner ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
    <div class="banner-title">🚀 Multi-Model Comparison Tool</div>
    <div class="banner-sub">Compare AI models based on answer quality, speed and cost using OpenRouter.</div>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
question = st.text_area(
    "Enter your question",
    placeholder="e.g. What is Artificial Intelligence?",
    height=120,
)

selected_models = st.multiselect(
    "🤖  Models to compare",
    options=MODELS,
    default=MODELS,
    format_func=lambda m: f"{MODEL_META.get(m, {}).get('emoji', '🤖')}  {MODEL_META.get(m, {}).get('label', m)}",
)

_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    run = st.button("🚀  Compare Models", use_container_width=True)

# ── Run parallel requests ──────────────────────────────────────────────────────
if run:
    if not question.strip():
        st.warning("Please enter a question before comparing.")
    elif not selected_models:
        st.warning("Please select at least one model.")
    else:
        def _call(model):
            result = ask(question.strip(), model)
            return {
                "model":   model,
                "answer":  result[0],
                "latency": result[1],
                "cost":    result[2],
                "tokens":  result[3] if len(result) > 3 else None,
            }

        skel_slot = st.empty()
        skel_slot.markdown(build_skeleton_html(len(selected_models)), unsafe_allow_html=True)

        with st.spinner("Querying all models in parallel — please wait…"):
            ordered = [None] * len(selected_models)
            with ThreadPoolExecutor(max_workers=len(selected_models)) as pool:
                future_to_idx = {pool.submit(_call, m): i
                                 for i, m in enumerate(selected_models)}
                for future in as_completed(future_to_idx):
                    ordered[future_to_idx[future]] = future.result()

        skel_slot.empty()
        st.session_state.results       = ordered
        st.session_state.last_question = question.strip()

# ── Display results ────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Summary bar ────────────────────────────────────────────────────────────
    ok = [r for r in results if r and r["latency"] is not None]
    if ok:
        fastest  = min(ok, key=lambda r: r["latency"])
        cheapest = min(ok, key=lambda r: r["cost"])
        total_tok = sum(r["tokens"] for r in ok if r["tokens"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⚡ Fastest",
                  MODEL_META.get(fastest["model"], {}).get("label", fastest["model"]),
                  f"{fastest['latency']:.2f}s")
        c2.metric("💰 Cheapest",
                  MODEL_META.get(cheapest["model"], {}).get("label", cheapest["model"]),
                  f"${cheapest['cost']:.6f}")
        c3.metric("🔢 Total Tokens", f"{total_tok:,}")
        c4.metric("✅ Models Queried", f"{len(ok)} / {len(results)}")

        st.markdown("<hr>", unsafe_allow_html=True)

    # ── Performance Analytics ──────────────────────────────────────────────────
    render_charts(results)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Model cards ────────────────────────────────────────────────────────────
    cols = st.columns(len(results))

    for col, r in zip(cols, results):
        if r is None:
            continue
        meta   = MODEL_META.get(r["model"], {"color": "blue", "emoji": "🤖", "label": r["model"]})
        color  = meta["color"]
        failed = r["latency"] is None

        with col:
            if failed:
                info_rows = "".join(
                    f'<div class="card-info-row"><span class="ci-icon">{icon}</span>{text}</div>'
                    for icon, text in meta.get("info", [])
                )
                st.markdown(f"""
                <div class="error-card">
                    <span class="error-badge">❌ Model Unavailable</span>
                    <div class="card-info" style="margin-top:0.4rem;">{info_rows}</div>
                    <div class="error-reason">{r['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                preview  = r["answer"][:400] + "…" if len(r["answer"]) > 400 else r["answer"]
                lat_str  = f"{r['latency']:.2f}s"
                cost_str = f"${r['cost']:.6f}"
                tok_str  = str(r["tokens"]) if r["tokens"] is not None else "—"
                info_rows = "".join(
                    f'<div class="card-info-row"><span class="ci-icon">{icon}</span>{text}</div>'
                    for icon, text in meta.get("info", [])
                )

                st.markdown(f"""
                <div class="model-card card-{color}">
                    <span class="card-badge badge-{color}">{meta['emoji']} {meta['label']}</span>
                    <div class="card-info">{info_rows}</div>
                    <div class="card-answer">{preview}</div>
                    <hr class="card-rule">
                    <div class="stats-row">
                        <div class="stat-row">
                            <span class="stat-label">⚡ Latency</span>
                            <span class="stat-value">{lat_str}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">💰 Cost</span>
                            <span class="stat-value">{cost_str}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">🔢 Tokens</span>
                            <span class="stat-value">{tok_str}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
