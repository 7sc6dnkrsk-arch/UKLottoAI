import streamlit as st
import pandas as pd
import random
import os
from collections import Counter

st.set_page_config(page_title="UK LottoAI", page_icon="🎯", layout="wide")

DATA_PATHS = ["LotteryAI/data/lotto.csv", "data/lotto.csv"]
DATA_PATH = next((p for p in DATA_PATHS if os.path.exists(p)), None)

if DATA_PATH is None:
    st.error("lotto.csv not found.")
    st.stop()

lotto = pd.read_csv(DATA_PATH, header=None)
number_cols = [5, 6, 7, 8, 9, 10]
lotto = lotto.dropna(subset=number_cols)
lotto[number_cols] = lotto[number_cols].astype(int)
draws = lotto[number_cols].values.tolist()

all_numbers = [n for draw in draws for n in draw]
frequency = Counter(all_numbers)
recent_numbers = [n for draw in draws[-100:] for n in draw]
recent_frequency = Counter(recent_numbers)

latest_index = len(draws) - 1
last_seen = {}
for i, draw in enumerate(draws):
    for n in draw:
        last_seen[n] = i

draw_sums = [sum(draw) for draw in draws]
avg_sum = sum(draw_sums) / len(draw_sums)
most_drawn = frequency.most_common(1)[0][0]
least_drawn = min(range(1, 60), key=lambda n: frequency.get(n, 0))

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #7d0000 0%, #130303 26%, #050505 100%);
    color: white;
}

.block-container {
    padding-top: 0.7rem;
    padding-bottom: 0.5rem;
    max-width: 1550px;
}

[data-testid="stSidebar"] { display: none; }

h1,h2,h3,p,span,div,label { color: white; }

.header {
    display:grid;
    grid-template-columns: 1.5fr 0.8fr 0.9fr;
    gap:18px;
    align-items:center;
    margin-bottom:10px;
}

.logo-title {
    font-size:54px;
    font-weight:950;
    line-height:0.9;
}

.logo-title span { color:#ff1717; }

.subtitle {
    font-size:17px;
    color:#f1f1f1;
}

.red-name { color:#ff3333; }

.top-box {
    background:rgba(5,5,5,0.74);
    border:1px solid rgba(255,255,255,0.2);
    border-radius:16px;
    padding:13px 18px;
    min-height:94px;
    box-shadow:0 8px 22px rgba(0,0,0,0.35);
}

.top-box-title {
    color:#eeeeee;
    font-size:13px;
    font-weight:900;
    letter-spacing:0.04em;
}

.top-box-main {
    font-size:28px;
    font-weight:950;
    margin-top:5px;
}

.top-box-sub {
    font-size:15px;
    color:#dedede;
}

.main-grid {
    display:grid;
    grid-template-columns: 30% 39% 31%;
    gap:14px;
}

.card {
    background:rgba(5,5,5,0.86);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:18px;
    padding:14px;
    box-shadow:0 8px 25px rgba(0,0,0,0.38);
}

.strategy-card {
    display:flex;
    align-items:center;
    gap:13px;
    min-height:86px;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:15px;
    padding:10px 12px;
    margin-bottom:8px;
    background:linear-gradient(145deg, rgba(255,255,255,0.04), rgba(0,0,0,0.45));
    cursor:pointer;
}

.strategy-card.active {
    border:1.5px solid #ff2020;
    box-shadow:0 0 18px rgba(255,20,20,0.5), inset 0 0 22px rgba(255,20,20,0.15);
    background:linear-gradient(145deg, rgba(130,0,0,0.6), rgba(0,0,0,0.55));
}

.strategy-icon {
    flex:0 0 62px;
    width:62px;
    height:62px;
    border-radius:50%;
    background:
        radial-gradient(circle at 30% 24%, #ffffff 0%, #ff9a9a 12%, #ff1717 42%, #8a0000 100%);
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:31px;
    box-shadow:
        inset -10px -12px 16px rgba(0,0,0,0.55),
        inset 5px 5px 12px rgba(255,255,255,0.55),
        0 7px 16px rgba(0,0,0,0.55);
}

.strategy-title {
    font-size:19px;
    font-weight:950;
}

.strategy-desc {
    font-size:13.2px;
    color:#e4e4e4;
    line-height:1.25;
}

.machine-card {
    min-height:620px;
    text-align:center;
    padding:12px 14px;
}

.machine-title {
    font-size:22px;
    font-weight:950;
    margin-bottom:6px;
}

.machine-title span { color:#ff2020; }

.machine-body {
    width:100%;
    height:390px;
    border-radius:18px;
    margin:0 auto 10px auto;
    position:relative;
    overflow:hidden;
    background:
        radial-gradient(circle at 50% 45%, rgba(255,255,255,0.18), rgba(255,0,0,0.13) 35%, rgba(0,0,0,0.84) 70%),
        radial-gradient(circle at top, rgba(255,0,0,0.25), transparent 65%);
    border:1px solid rgba(255,255,255,0.18);
    box-shadow:inset 0 0 45px rgba(255,255,255,0.09), 0 0 28px rgba(255,0,0,0.35);
}

.globe {
    position:absolute;
    left:50%;
    top:17px;
    transform:translateX(-50%);
    width:355px;
    height:355px;
    border-radius:50%;
    background:
        radial-gradient(circle at 32% 22%, rgba(255,255,255,0.85), rgba(255,255,255,0.12) 18%, transparent 32%),
        radial-gradient(circle at center, rgba(255,255,255,0.14), rgba(227,6,19,0.20) 45%, rgba(0,0,0,0.92) 100%);
    border:8px solid rgba(255,255,255,0.35);
    box-shadow:
        inset 0 0 36px rgba(255,255,255,0.24),
        inset 0 0 90px rgba(255,0,0,0.18),
        0 0 28px rgba(255,0,0,0.55);
    overflow:hidden;
}

.mini-ball {
    position:absolute;
    width:42px;
    height:42px;
    border-radius:50%;
    background:
        radial-gradient(circle at 30% 24%, #ffffff 0%, #ffffff 23%, #ff3a3a 26%, #d90000 62%, #650000 100%);
    color:#111;
    font-weight:950;
    font-size:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:
        inset -7px -9px 11px rgba(0,0,0,0.55),
        inset 4px 4px 9px rgba(255,255,255,0.6),
        0 5px 12px rgba(0,0,0,0.55);
    animation: tumble 2.4s infinite ease-in-out;
}

@keyframes tumble {
    0%   { transform: translate(0,0) rotate(0deg) scale(1); }
    25%  { transform: translate(17px,-20px) rotate(75deg) scale(1.04); }
    50%  { transform: translate(-12px,14px) rotate(155deg) scale(0.98); }
    75%  { transform: translate(14px,20px) rotate(245deg) scale(1.03); }
    100% { transform: translate(0,0) rotate(360deg) scale(1); }
}

.drawn-row {
    margin-top:8px;
    margin-bottom:10px;
}

.lottery-ball {
    display:inline-flex;
    justify-content:center;
    align-items:center;
    width:44px;
    height:44px;
    margin:3px 4px;
    border-radius:50%;
    background:
        radial-gradient(circle at 30% 24%, #ffffff 0%, #ffffff 22%, #ff3a3a 25%, #d90000 63%, #650000 100%);
    color:#111;
    font-size:19px;
    font-weight:950;
    box-shadow:
        inset -7px -9px 12px rgba(0,0,0,0.55),
        inset 4px 4px 10px rgba(255,255,255,0.6),
        0 5px 12px rgba(0,0,0,0.55);
}

.big-button-shell {
    display:block;
    width:92%;
    margin:8px auto 4px auto;
    padding:0;
    border-radius:20px;
    background:linear-gradient(180deg,#ffffff 0%,#f4f4f4 52%,#c7c7c7 100%);
    border:2px solid #ff1f1f;
    box-shadow:
        0 10px 0 #8f0000,
        0 16px 22px rgba(0,0,0,0.55),
        inset 0 4px 8px rgba(255,255,255,0.95),
        inset 0 -5px 10px rgba(0,0,0,0.22);
    text-align:center;
}

.big-button-text {
    color:#b30000;
    font-size:31px;
    font-weight:950;
    letter-spacing:0.03em;
    padding:18px 8px;
    text-shadow:0 1px 0 #ffffff;
}

.button-note {
    color:#d9d9d9;
    font-size:13px;
    margin-top:11px;
}

.result-card {
    background:rgba(5,5,5,0.85);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:15px;
    padding:9px 11px;
    margin-bottom:8px;
}

.result-title {
    font-size:16px;
    font-weight:900;
    margin-bottom:4px;
}

.stars {
    color:#ffbd2e;
    font-size:16px;
    float:right;
}

.stats-row {
    display:grid;
    grid-template-columns: repeat(6, 1fr);
    gap:8px;
    margin-top:10px;
}

.stat-box {
    background:rgba(5,5,5,0.88);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:14px;
    padding:11px;
    text-align:center;
}

.stat-label {
    color:#d6d6d6;
    font-size:12px;
}

.stat-value {
    color:#fff;
    font-size:23px;
    font-weight:950;
}

.warning {
    font-size:12px;
    color:#e0e0e0;
    text-align:center;
    margin-top:9px;
    padding:8px;
    background:rgba(120,0,0,0.5);
}

.stRadio { margin-top:-10px; margin-bottom:6px; }
.stRadio > label { display:none; }
.stRadio div[role="radiogroup"] {
    display:flex;
    flex-direction:column;
    gap:0px;
}
.stButton>button {
    width:100%;
    height:82px;
    border-radius:20px;
    background:linear-gradient(180deg,#ffffff 0%,#f4f4f4 50%,#c9c9c9 100%);
    border:2px solid #ff1f1f;
    color:#b30000;
    font-size:29px;
    font-weight:950;
    letter-spacing:0.02em;
    box-shadow:
        0 9px 0 #8f0000,
        0 15px 22px rgba(0,0,0,0.55),
        inset 0 4px 8px rgba(255,255,255,0.95),
        inset 0 -5px 10px rgba(0,0,0,0.22);
}
.stButton>button:hover {
    border:2px solid #ffffff;
    color:#e30613;
    transform:translateY(1px);
}
@media (max-width: 1000px) {
    .main-grid { grid-template-columns: 1fr; }
    .header { grid-template-columns:1fr; }
    .stats-row { grid-template-columns: repeat(2,1fr); }
}
</style>
""", unsafe_allow_html=True)


def features(numbers):
    numbers = sorted(numbers)
    total = sum(numbers)
    odd = sum(1 for n in numbers if n % 2)
    even = 6 - odd
    low = sum(1 for n in numbers if n <= 29)
    high = 6 - low
    spread = max(numbers) - min(numbers)
    return total, odd, even, low, high, spread


def ball_html(numbers):
    return "".join(f"<span class='lottery-ball'>{n:02d}</span>" for n in sorted(numbers))


def score_line(numbers):
    total, odd, even, low, high, spread = features(numbers)
    sum_score = max(0, 1 - abs(total - avg_sum) / avg_sum)
    odd_score = 1 if odd == 3 else 0.75 if odd in [2, 4] else 0.4
    low_score = 1 if low == 3 else 0.75 if low in [2, 4] else 0.4
    spread_score = min(spread / 45, 1)
    return round((sum_score + odd_score + low_score + spread_score) / 4 * 100)


def lottoai_pick():
    best, best_score = None, -1
    for _ in range(6000):
        nums = sorted(random.sample(range(1, 60), 6))
        total_score = (
            sum(frequency.get(n, 0) for n in nums)
            + sum(recent_frequency.get(n, 0) for n in nums) * 8
            + sum(latest_index - last_seen.get(n, 0) for n in nums) * 0.35
            + score_line(nums) * 8
        )
        if total_score > best_score:
            best_score, best = total_score, nums
    return best


def smart_lucky_dip():
    for _ in range(5000):
        nums = sorted(random.sample(range(1, 60), 6))
        total, odd, even, low, high, spread = features(nums)
        if odd in [2, 3, 4] and low in [2, 3, 4] and avg_sum - 38 <= total <= avg_sum + 38 and spread >= 20:
            return nums
    return sorted(random.sample(range(1, 60), 6))


def balls_on_fire():
    pool = [n for n, _ in frequency.most_common(26)]
    return sorted(random.sample(pool, 6))


def worth_a_punt():
    scores = []
    for n in range(1, 60):
        freq = frequency.get(n, 0)
        overdue = latest_index - last_seen.get(n, 0)
        scores.append((overdue * 2 - freq, n))
    pool = [n for _, n in sorted(scores, reverse=True)[:26]]
    return sorted(random.sample(pool, 6))


def complete_my_ticket(user_nums):
    user_nums = sorted(set(user_nums))
    if len(user_nums) != 3:
        return None
    best, best_score = None, -1
    available = [n for n in range(1, 60) if n not in user_nums]
    for _ in range(4000):
        nums = sorted(user_nums + random.sample(available, 3))
        s = score_line(nums) + sum(frequency.get(n, 0) for n in nums) / 10
        if s > best_score:
            best_score, best = s, nums
    return best


def generate_lines(mode, user_nums=None):
    lines = []
    for _ in range(5):
        if mode == "LottoAI Pick":
            line = lottoai_pick()
        elif mode == "Smart Lucky Dip":
            line = smart_lucky_dip()
        elif mode == "Balls on Fire":
            line = balls_on_fire()
        elif mode == "Worth a Punt":
            line = worth_a_punt()
        else:
            line = complete_my_ticket(user_nums)
        if line:
            lines.append(line)
    return lines


if "mode" not in st.session_state:
    st.session_state.mode = "LottoAI Pick"

if "lines" not in st.session_state:
    st.session_state.lines = generate_lines(st.session_state.mode)


st.markdown("""
<div class="header">
    <div>
        <div class="logo-title"><span>UK</span> LottoAI</div>
        <div class="subtitle">Historic UK Lotto Analytics</div>
        <div class="subtitle">Created by <span class="red-name">AR Taylor</span></div>
    </div>
    <div class="top-box">
        <div class="top-box-title">LATEST DRAW ADDED ✅</div>
        <div class="top-box-main">3 Jul 2026</div>
        <div class="top-box-sub">Draw 3,168 analysed</div>
    </div>
    <div class="top-box">
        <div class="top-box-title">NEXT DRAW</div>
        <div class="top-box-main">Wed / Sat</div>
        <div class="top-box-sub">Auto-update planned</div>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("<div class='main-grid'>", unsafe_allow_html=True)

left, middle, right = st.columns([1.02, 1.33, 1.05])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### CHOOSE YOUR STRATEGY")

    modes = [
        ("LottoAI Pick", "⭐", "Our best overall selection based on all historical data."),
        ("Smart Lucky Dip", "🎲", "Random numbers that still follow historical patterns."),
        ("Balls on Fire", "🔥", "Favours numbers that have appeared more frequently."),
        ("Worth a Punt", "🎯", "Favours numbers that have appeared less frequently or have longer gaps."),
        ("Complete My Ticket", "🤝", "You choose 3 numbers, LottoAI chooses the other 3."),
    ]

    selected = st.radio(
        "Strategy",
        [m[0] for m in modes],
        index=[m[0] for m in modes].index(st.session_state.mode),
        label_visibility="collapsed"
    )

    st.session_state.mode = selected

    for name, icon, desc in modes:
        active = " active" if selected == name else ""
        st.markdown(f"""
        <div class="strategy-card{active}">
            <div class="strategy-icon">{icon}</div>
            <div>
                <div class="strategy-title">{name}</div>
                <div class="strategy-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    user_numbers = None
    if selected == "Complete My Ticket":
        c1, c2, c3 = st.columns(3)
        with c1:
            n1 = st.number_input("1", 1, 59, 7)
        with c2:
            n2 = st.number_input("2", 1, 59, 18)
        with c3:
            n3 = st.number_input("3", 1, 59, 44)
        user_numbers = [int(n1), int(n2), int(n3)]

    st.markdown("</div>", unsafe_allow_html=True)

with middle:
    st.markdown("<div class='card machine-card'>", unsafe_allow_html=True)
    st.markdown("<div class='machine-title'>LET’S GET THOSE <span>BALLS</span> ROLLING!</div>", unsafe_allow_html=True)

    mini_positions = [
        (44, 58), (108, 48), (180, 68), (247, 50),
        (72, 128), (148, 128), (220, 135), (280, 130),
        (48, 205), (119, 218), (190, 214), (257, 213),
        (88, 282), (160, 285), (230, 282)
    ]

    machine_html = "<div class='machine-body'><div class='globe'>"
    sample_nums = random.sample(range(1, 60), len(mini_positions))
    for idx, ((x, y), n) in enumerate(zip(mini_positions, sample_nums)):
        machine_html += f"<div class='mini-ball' style='left:{x}px;top:{y}px;animation-delay:{idx * 0.11}s;'>{n:02d}</div>"
    machine_html += "</div></div>"
    st.markdown(machine_html, unsafe_allow_html=True)

    if st.button("GENERATE YOUR PICKS"):
        st.session_state.lines = generate_lines(selected, user_numbers)
        st.rerun()

    st.markdown("<div class='button-note'>🔒 Click to start the draw machine</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    for i, line in enumerate(st.session_state.lines, start=1):
        title = "Best Selection" if i == 1 else f"Alternative {i-1}"
        confidence = score_line(line)
        star_count = max(3, min(5, round(confidence / 20)))
        stars = "★" * star_count + "☆" * (5 - star_count)

        st.markdown(f"""
        <div class="result-card">
            <div class="result-title">
                <span style="color:#ff3333;">{i}</span> &nbsp; {title}
                <span class="stars">{stars}</span>
            </div>
            {ball_html(line)}
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


odd_total = sum(1 for n in all_numbers if n % 2)
even_total = len(all_numbers) - odd_total
low_total = sum(1 for n in all_numbers if n <= 29)
high_total = len(all_numbers) - low_total

st.markdown(f"""
<div class="stats-row">
    <div class="stat-box"><div class="stat-value">{len(draws):,}</div><div class="stat-label">TOTAL DRAWS</div></div>
    <div class="stat-box"><div class="stat-value">{most_drawn}</div><div class="stat-label">MOST DRAWN</div></div>
    <div class="stat-box"><div class="stat-value">{least_drawn}</div><div class="stat-label">LEAST DRAWN</div></div>
    <div class="stat-box"><div class="stat-value">{round(avg_sum)}</div><div class="stat-label">AVERAGE SUM</div></div>
    <div class="stat-box"><div class="stat-value">{round(odd_total / len(all_numbers) * 100)}% / {round(even_total / len(all_numbers) * 100)}%</div><div class="stat-label">ODD / EVEN</div></div>
    <div class="stat-box"><div class="stat-value">{round(low_total / len(all_numbers) * 100)}% / {round(high_total / len(all_numbers) * 100)}%</div><div class="stat-label">LOW / HIGH</div></div>
</div>

<div class="warning">
18+ • Play responsibly • UK LottoAI is an analytics and entertainment tool. It cannot predict or guarantee lottery results.
</div>
""", unsafe_allow_html=True)
