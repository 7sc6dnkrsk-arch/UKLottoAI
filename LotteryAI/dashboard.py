import streamlit as st
import pandas as pd
import random
import os
from collections import Counter

st.set_page_config(
    page_title="UK LottoAI",
    page_icon="🎯",
    layout="wide"
)

DATA_PATHS = [
    "LotteryAI/data/lotto.csv",
    "data/lotto.csv"
]

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
    background: radial-gradient(circle at top, #7b0000 0%, #111 32%, #050505 100%);
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    display: none;
}

h1, h2, h3, p, span, div, label {
    color: white;
}

.header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:14px;
}

.logo-title {
    font-size:56px;
    font-weight:900;
    line-height:0.95;
}

.logo-title span {
    color:#e30613;
}

.subtitle {
    font-size:18px;
    color:#f2f2f2;
}

.red-name {
    color:#ff3333;
}

.latest-box {
    background:#f7f7f7;
    color:#111;
    border-radius:18px;
    padding:18px 28px;
    min-width:300px;
    box-shadow:0 8px 22px rgba(0,0,0,0.35);
}

.latest-box div {
    color:#111;
}

.main-grid {
    display:grid;
    grid-template-columns: 29% 35% 36%;
    gap:18px;
}

.card {
    background:rgba(8,8,8,0.88);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:18px;
    padding:18px;
    box-shadow:0 8px 25px rgba(0,0,0,0.35);
}

.strategy-card {
    display:flex;
    align-items:center;
    gap:14px;
    border:1px solid rgba(255,255,255,0.14);
    border-radius:14px;
    padding:12px;
    margin-bottom:10px;
    background:rgba(255,255,255,0.04);
}

.strategy-card.active {
    border:1px solid #e30613;
    box-shadow:0 0 16px rgba(227,6,19,0.35);
}

.strategy-icon {
    width:58px;
    height:58px;
    border-radius:50%;
    background:radial-gradient(circle at 30% 25%, #ff7777, #e30613 52%, #740000 100%);
    display:flex;
    justify-content:center;
    align-items:center;
    font-size:28px;
    box-shadow: inset -8px -10px 14px rgba(0,0,0,0.45), 0 5px 14px rgba(0,0,0,0.5);
}

.generate-btn {
    background:linear-gradient(180deg,#ff2020,#b00000);
    border-radius:14px;
    padding:18px;
    text-align:center;
    font-size:20px;
    font-weight:900;
    margin-top:12px;
    box-shadow:0 8px 20px rgba(227,6,19,0.35);
}

.machine {
    text-align:center;
    min-height:560px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}

.machine-title {
    font-size:22px;
    font-weight:900;
    margin-bottom:8px;
}

.machine-body {
    width:340px;
    height:340px;
    border-radius:50%;
    margin:10px auto;
    background:
        radial-gradient(circle at 28% 24%, rgba(255,255,255,0.9), rgba(255,255,255,0.08) 15%, transparent 28%),
        radial-gradient(circle at center, rgba(255,255,255,0.17), rgba(227,6,19,0.25) 45%, rgba(0,0,0,0.8) 100%);
    border:8px solid rgba(255,255,255,0.35);
    box-shadow:
        inset 0 0 35px rgba(255,255,255,0.25),
        inset 0 0 90px rgba(227,6,19,0.25),
        0 0 28px rgba(227,6,19,0.55);
    position:relative;
    overflow:hidden;
}

.mini-ball {
    position:absolute;
    width:42px;
    height:42px;
    border-radius:50%;
    background:radial-gradient(circle at 30% 25%, white 0%, #fff 20%, #ff3333 24%, #e30613 60%, #680000 100%);
    color:#111;
    font-weight:900;
    font-size:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow: inset -6px -8px 10px rgba(0,0,0,0.45), 0 4px 10px rgba(0,0,0,0.5);
    animation: floatBall 2.8s infinite ease-in-out;
}

@keyframes floatBall {
    0% { transform: translate(0,0) rotate(0deg); }
    50% { transform: translate(8px,-12px) rotate(18deg); }
    100% { transform: translate(0,0) rotate(0deg); }
}

.lottery-ball {
    display:inline-flex;
    justify-content:center;
    align-items:center;
    width:48px;
    height:48px;
    margin:4px;
    border-radius:50%;
    background:
        radial-gradient(circle at 30% 24%, #ffffff 0%, #ffffff 20%, #ff3a3a 23%, #d90000 63%, #650000 100%);
    color:#111;
    font-size:21px;
    font-weight:900;
    box-shadow:
        inset -7px -9px 12px rgba(0,0,0,0.5),
        inset 4px 4px 10px rgba(255,255,255,0.6),
        0 5px 12px rgba(0,0,0,0.55);
}

.result-card {
    background:rgba(8,8,8,0.88);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:16px;
    padding:12px 14px;
    margin-bottom:10px;
}

.result-title {
    font-size:18px;
    font-weight:800;
    margin-bottom:6px;
}

.stars {
    color:#ffbd2e;
    font-size:18px;
}

.stats-row {
    display:grid;
    grid-template-columns: repeat(4, 1fr);
    gap:12px;
    margin-top:16px;
}

.stat-box {
    background:#f7f7f7;
    color:#111;
    border-radius:16px;
    padding:14px;
    text-align:center;
}

.stat-box div {
    color:#111;
}

.stat-value {
    font-size:28px;
    font-weight:900;
}

.warning {
    font-size:12px;
    color:#d9d9d9;
    text-align:center;
    margin-top:12px;
}

.stRadio > div {
    gap: 0.3rem;
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
    return "".join([f"<span class='lottery-ball'>{n:02d}</span>" for n in sorted(numbers)])


def score_line(numbers):
    total, odd, even, low, high, spread = features(numbers)
    sum_score = max(0, 1 - abs(total - avg_sum) / avg_sum)
    odd_score = 1 if odd == 3 else 0.75 if odd in [2, 4] else 0.4
    low_score = 1 if low == 3 else 0.75 if low in [2, 4] else 0.4
    spread_score = min(spread / 45, 1)
    return round((sum_score + odd_score + low_score + spread_score) / 4 * 100)


def lottoai_pick():
    best = None
    best_score = -1

    for _ in range(7000):
        nums = sorted(random.sample(range(1, 60), 6))
        freq_score = sum(frequency.get(n, 0) for n in nums)
        recent_score = sum(recent_frequency.get(n, 0) for n in nums) * 8
        overdue_score = sum(latest_index - last_seen.get(n, 0) for n in nums) * 0.4
        shape_score = score_line(nums) * 8
        total_score = freq_score + recent_score + overdue_score + shape_score

        if total_score > best_score:
            best_score = total_score
            best = nums

    return best


def smart_lucky_dip():
    for _ in range(5000):
        nums = sorted(random.sample(range(1, 60), 6))
        total, odd, even, low, high, spread = features(nums)

        if odd in [2, 3, 4] and low in [2, 3, 4] and avg_sum - 38 <= total <= avg_sum + 38 and spread >= 20:
            return nums

    return sorted(random.sample(range(1, 60), 6))


def balls_on_fire():
    top_pool = [n for n, _ in frequency.most_common(26)]
    return sorted(random.sample(top_pool, 6))


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

    best = None
    best_score = -1
    available = [n for n in range(1, 60) if n not in user_nums]

    for _ in range(4000):
        nums = sorted(user_nums + random.sample(available, 3))
        s = score_line(nums) + sum(frequency.get(n, 0) for n in nums) / 10

        if s > best_score:
            best_score = s
            best = nums

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


st.markdown(
    """
    <div class="header">
        <div>
            <div class="logo-title"><span>UK</span> LottoAI</div>
            <div class="subtitle">Historic UK Lotto Analytics</div>
            <div class="subtitle">Created by <span class="red-name">AR Taylor</span></div>
        </div>
        <div class="latest-box">
            <div style="font-size:14px;font-weight:800;">LATEST DRAW ADDED ✅</div>
            <div style="font-size:28px;font-weight:900;">3 Jul 2026</div>
            <div style="font-size:18px;">Draw 3,168 analysed</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


left, middle, right = st.columns([1.05, 1.35, 1.55])

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
        label_visibility="collapsed",
        index=[m[0] for m in modes].index(st.session_state.mode)
    )

    st.session_state.mode = selected

    for name, icon, desc in modes:
        active = " active" if selected == name else ""
        st.markdown(
            f"""
            <div class="strategy-card{active}">
                <div class="strategy-icon">{icon}</div>
                <div>
                    <div style="font-size:20px;font-weight:900;">{name}</div>
                    <div style="font-size:14px;color:#ddd;">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

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

    if st.button("✨ Generate Selections", use_container_width=True):
        st.session_state.lines = generate_lines(selected, user_numbers)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with middle:
    st.markdown("<div class='card machine'>", unsafe_allow_html=True)
    st.markdown("<div class='machine-title'>LET'S GET THOSE BALLS ROLLING!</div>", unsafe_allow_html=True)

    mini_positions = [
        (25, 55), (72, 82), (130, 70), (188, 92), (238, 55),
        (58, 160), (118, 148), (178, 166), (240, 150),
        (90, 230), (155, 238), (220, 224)
    ]

    machine_html = "<div class='machine-body'>"
    sample_nums = random.sample(range(1, 60), len(mini_positions))

    for idx, ((x, y), n) in enumerate(zip(mini_positions, sample_nums)):
        machine_html += f"<div class='mini-ball' style='left:{x}px;top:{y}px;animation-delay:{idx * 0.13}s;'>{n:02d}</div>"

    machine_html += "</div>"

    st.markdown(machine_html, unsafe_allow_html=True)

    best_line = st.session_state.lines[0] if st.session_state.lines else []
    st.markdown("<div style='font-size:18px;font-weight:900;'>YOUR NUMBERS ARE READY!</div>", unsafe_allow_html=True)
    st.markdown(ball_html(best_line), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    for i, line in enumerate(st.session_state.lines, start=1):
        title = "Best Selection" if i == 1 else f"Alternative {i-1}"
        confidence = score_line(line)
        stars = "★" * max(3, min(5, round(confidence / 20))) + "☆" * (5 - max(3, min(5, round(confidence / 20))))

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-title">
                    <span style="color:#ff3333;">{i}</span> &nbsp; {title}
                    <span class="stars">&nbsp; {stars}</span>
                </div>
                {ball_html(line)}
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown(
    f"""
    <div class="stats-row">
        <div class="stat-box">
            <div class="stat-value">{len(draws):,}</div>
            <div>Total Draws</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{most_drawn}</div>
            <div>Most Drawn</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{least_drawn}</div>
            <div>Least Drawn</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{round(avg_sum)}</div>
            <div>Average Sum</div>
        </div>
    </div>

    <div class="warning">
        18+ • Play responsibly • UK LottoAI is an analytics and entertainment tool. It cannot predict or guarantee lottery results.
    </div>
    """,
    unsafe_allow_html=True
)
