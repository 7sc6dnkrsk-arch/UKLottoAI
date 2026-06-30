import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random
import os

st.set_page_config(page_title="UK LottoAI", page_icon="🎯", layout="wide")

# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>
.stApp { background:#030507; color:#ffffff; }
[data-testid="stSidebar"] { background:#05080c; border-right:1px solid #222832; }
.block-container { padding-top:1.5rem; }
h1,h2,h3,h4,p,label,span,div { color:#ffffff; }

[data-testid="stMetric"] {
    background:linear-gradient(145deg,#080b10,#111821);
    border:1px solid #30363d;
    border-radius:16px;
    padding:18px;
}

[data-testid="stMetricValue"] {
    color:#39ff63;
    font-size:30px;
    font-weight:800;
}

.panel {
    background:linear-gradient(145deg,#05070a,#0e131a);
    border:1px solid #30363d;
    border-radius:18px;
    padding:24px;
    margin-bottom:18px;
}

.number-ball {
    display:inline-block;
    width:54px;
    height:54px;
    border-radius:50%;
    background:radial-gradient(circle at 30% 30%, #6fff76, #18b83a);
    color:#ffffff;
    text-align:center;
    line-height:54px;
    font-size:24px;
    font-weight:900;
    margin:5px 8px;
    box-shadow:0 0 14px rgba(57,255,99,0.35);
}

.small-note {
    color:#c7c7c7;
    font-size:14px;
}

.footer-box {
    border:1px solid #30363d;
    background:#080c12;
    border-radius:14px;
    padding:16px;
    color:#c7c7c7;
    margin-top:18px;
}

.stButton>button {
    background:#07110a;
    color:#39ff63;
    border:1px solid #39ff63;
    border-radius:10px;
    padding:0.6rem 1.5rem;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.markdown("# 🎯 UK LottoAI")
st.sidebar.caption("Created by AR Taylor")

section = st.sidebar.radio(
    "NAVIGATION",
    ["Dashboard", "Number Analysis", "Odd / Even", "About"]
)

st.sidebar.divider()

selection_mode = st.sidebar.radio(
    "🎯 Choose Your Strategy",
    [
        "⭐ LottoAI Pick",
        "🤝 Complete My Ticket",
        "🎲 Smart Lucky Dip",
        "📈 Top Trending Picks",
        "💎 Overlooked Picks"
    ]
)

st.sidebar.caption("""
**LottoAI Pick** — best overall historical selection.  
**Complete My Ticket** — you choose 3, LottoAI adds 3.  
**Smart Lucky Dip** — random but historically balanced.  
**Top Trending Picks** — favours more frequently drawn numbers.  
**Overlooked Picks** — favours less frequently drawn or longer-gap numbers.
""")

# -----------------------------
# LOAD DATA
# -----------------------------

DATA_PATH = "LotteryAI/data/lotto.csv"

if not os.path.exists(DATA_PATH):
    DATA_PATH = "data/lotto.csv"

if not os.path.exists(DATA_PATH):
    st.error("lotto.csv not found.")
    st.stop()

lotto = pd.read_csv(DATA_PATH, header=None)

number_cols = [5, 6, 7, 8, 9, 10]
lotto = lotto.dropna(subset=number_cols)
lotto[number_cols] = lotto[number_cols].astype(int)

draws = lotto[number_cols].values.tolist()

# -----------------------------
# ANALYSIS
# -----------------------------

all_numbers = []
draw_sums = []
odd_even_patterns = []
low_high_patterns = []
pair_counter = Counter()

for draw in draws:
    draw = sorted(draw)
    all_numbers.extend(draw)
    draw_sums.append(sum(draw))

    odd = sum(1 for n in draw if n % 2 != 0)
    even = 6 - odd
    odd_even_patterns.append(f"{odd}/{even}")

    low = sum(1 for n in draw if n <= 29)
    high = 6 - low
    low_high_patterns.append(f"{low}/{high}")

    for i in range(len(draw)):
        for j in range(i + 1, len(draw)):
            pair_counter[(draw[i], draw[j])] += 1

frequency = Counter(all_numbers)
recent_numbers = [n for draw in draws[-100:] for n in draw]
recent_frequency = Counter(recent_numbers)

odd_even_counter = Counter(odd_even_patterns)
low_high_counter = Counter(low_high_patterns)

latest_index = len(draws) - 1
last_seen = {}

for i, draw in enumerate(draws):
    for n in draw:
        last_seen[n] = i

avg_sum = sum(draw_sums) / len(draw_sums)

freq_df = pd.DataFrame({
    "Number": list(range(1, 60)),
    "Frequency": [frequency.get(n, 0) for n in range(1, 60)]
})

hot = freq_df.sort_values("Frequency", ascending=False)
cold = freq_df.sort_values("Frequency", ascending=True)

# -----------------------------
# HELPERS
# -----------------------------

def line_features(numbers):
    numbers = sorted(numbers)
    total = sum(numbers)
    odd = sum(1 for n in numbers if n % 2 != 0)
    even = 6 - odd
    low = sum(1 for n in numbers if n <= 29)
    high = 6 - low
    spread = max(numbers) - min(numbers)

    consecutive_pairs = sum(
        1 for a, b in zip(numbers, numbers[1:]) if b == a + 1
    )

    primes = sum(
        1 for n in numbers
        if n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
    )

    return total, odd, even, low, high, spread, consecutive_pairs, primes


def display_ball_line(numbers):
    return "".join(f"<span class='number-ball'>{n}</span>" for n in sorted(numbers))


def historical_shape_score(numbers):
    total, odd, even, low, high, spread, consecutive_pairs, primes = line_features(numbers)

    odd_even_pattern = f"{odd}/{even}"
    low_high_pattern = f"{low}/{high}"

    odd_score = odd_even_counter.get(odd_even_pattern, 0) / odd_even_counter.most_common(1)[0][1]
    low_score = low_high_counter.get(low_high_pattern, 0) / low_high_counter.most_common(1)[0][1]
    sum_score = max(0, 1 - abs(total - avg_sum) / avg_sum)
    spread_score = min(spread / 58, 1)

    penalty = 0
    if consecutive_pairs > 2:
        penalty += 0.4
    if spread < 18:
        penalty += 0.3

    return max(0, odd_score + low_score + sum_score + spread_score - penalty)


def pair_score(numbers):
    score = 0
    numbers = sorted(numbers)
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            score += pair_counter.get((numbers[i], numbers[j]), 0)
    return score


def generate_lottoai_pick():
    best_line = None
    best_score = -1

    for _ in range(10000):
        candidate = sorted(random.sample(range(1, 60), 6))

        base = sum(frequency.get(n, 0) for n in candidate)
        recent = sum(recent_frequency.get(n, 0) for n in candidate)
        overdue = sum(latest_index - last_seen.get(n, 0) for n in candidate)
        shape = historical_shape_score(candidate)
        pairs = pair_score(candidate)

        score = (
            base * 1.0 +
            recent * 12 +
            overdue * 0.6 +
            shape * 600 +
            pairs * 0.25
        )

        if score > best_score:
            best_score = score
            best_line = candidate

    return best_line


def generate_smart_lucky_dip():
    for _ in range(10000):
        candidate = sorted(random.sample(range(1, 60), 6))
        total, odd, even, low, high, spread, consecutive_pairs, primes = line_features(candidate)

        if f"{odd}/{even}" not in ["2/4", "3/3", "4/2"]:
            continue
        if f"{low}/{high}" not in ["2/4", "3/3", "4/2"]:
            continue
        if not (avg_sum - 35 <= total <= avg_sum + 35):
            continue
        if spread < 20:
            continue
        if consecutive_pairs > 2:
            continue

        return candidate

    return sorted(random.sample(range(1, 60), 6))


def generate_top_trending():
    pool = list(hot.head(25)["Number"])
    return sorted(random.sample(pool, 6))


def generate_overlooked():
    overlooked_scores = []

    for n in range(1, 60):
        freq = frequency.get(n, 0)
        overdue = latest_index - last_seen.get(n, 0)
        score = overdue * 2 - freq
        overlooked_scores.append((score, n))

    overlooked_scores.sort(reverse=True)
    pool = [n for score, n in overlooked_scores[:25]]
    return sorted(random.sample(pool, 6))


def complete_my_ticket(user_numbers):
    user_numbers = sorted(set(user_numbers))

    if len(user_numbers) != 3:
        return None

    best_line = None
    best_score = -1

    available = [n for n in range(1, 60) if n not in user_numbers]

    for _ in range(8000):
        added = random.sample(available, 3)
        candidate = sorted(user_numbers + added)

        base = sum(frequency.get(n, 0) for n in candidate)
        shape = historical_shape_score(candidate)
        pairs = pair_score(candidate)

        score = base + shape * 700 + pairs * 0.3

        if score > best_score:
            best_score = score
            best_line = candidate

    return best_line


def generate_line(mode, user_numbers=None):
    if mode == "⭐ LottoAI Pick":
        return generate_lottoai_pick()
    elif mode == "🎲 Smart Lucky Dip":
        return generate_smart_lucky_dip()
    elif mode == "📈 Top Trending Picks":
        return generate_top_trending()
    elif mode == "💎 Overlooked Picks":
        return generate_overlooked()
    elif mode == "🤝 Complete My Ticket":
        return complete_my_ticket(user_numbers)
    return generate_smart_lucky_dip()


# -----------------------------
# HEADER
# -----------------------------

st.markdown("# 🎯 UK LottoAI")
st.caption("Created by AR Taylor • Professional UK National Lottery Analytics Platform")
st.divider()

# -----------------------------
# DASHBOARD
# -----------------------------

if section == "Dashboard":

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Total Draws", f"{len(draws):,}")
    c2.metric("Most Frequent", int(hot.iloc[0]["Number"]))
    c3.metric("Least Frequent", int(cold.iloc[0]["Number"]))
    c4.metric("Average Sum", round(avg_sum, 1))
    c5.metric("Most Common Odd / Even", odd_even_counter.most_common(1)[0][0])
    c6.metric("Most Common Low / High", low_high_counter.most_common(1)[0][0])

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.markdown(f"## {selection_mode}")

    if selection_mode == "⭐ LottoAI Pick":
        st.markdown("<p class='small-note'>Best overall statistical selection using historical frequency, recent form, overdue gaps, pairings and historical shape.</p>", unsafe_allow_html=True)

    elif selection_mode == "🤝 Complete My Ticket":
        st.markdown("<p class='small-note'>Choose 3 numbers. UK LottoAI completes the remaining 3 numbers.</p>", unsafe_allow_html=True)

    elif selection_mode == "🎲 Smart Lucky Dip":
        st.markdown("<p class='small-note'>Random selections shaped by common historical draw characteristics.</p>", unsafe_allow_html=True)

    elif selection_mode == "📈 Top Trending Picks":
        st.markdown("<p class='small-note'>Favours numbers that have appeared more frequently in the historical dataset.</p>", unsafe_allow_html=True)

    elif selection_mode == "💎 Overlooked Picks":
        st.markdown("<p class='small-note'>Favours numbers that have appeared less often or have longer gaps since last appearance.</p>", unsafe_allow_html=True)

    user_numbers = None

    if selection_mode == "🤝 Complete My Ticket":
        a, b, c = st.columns(3)
        with a:
            n1 = st.number_input("Your number 1", min_value=1, max_value=59, value=7)
        with b:
            n2 = st.number_input("Your number 2", min_value=1, max_value=59, value=18)
        with c:
            n3 = st.number_input("Your number 3", min_value=1, max_value=59, value=44)

        user_numbers = [int(n1), int(n2), int(n3)]

        if len(set(user_numbers)) < 3:
            st.warning("Please enter 3 different numbers.")

    lines = []

    for _ in range(5):
        line = generate_line(selection_mode, user_numbers)
        if line is not None:
            lines.append(line)

    for idx, numbers in enumerate(lines, start=1):
        total, odd, even, low, high, spread, consecutive_pairs, primes = line_features(numbers)
        balls_html = display_ball_line(numbers)

        st.markdown(
            f"""
            <div style="margin-bottom:18px;">
                <strong>Line {idx}</strong>
                <div style="margin-top:8px;">{balls_html}</div>
                <p class="small-note">
                Sum {total} • {odd} odd / {even} even • {low} low / {high} high • Spread {spread}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("↻ Generate New Lines"):
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    left_chart, right_table = st.columns([1.5, 1])

    with left_chart:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("## NUMBER FREQUENCY (1–59)")

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.bar(freq_df["Number"], freq_df["Frequency"], color="#1f8fff")
        ax.set_facecolor("#05070a")
        fig.patch.set_facecolor("#05070a")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.set_xlabel("Number")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        st.markdown("</div>", unsafe_allow_html=True)

    with right_table:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("## NUMBER GROUPS")

        a, b = st.columns(2)

        with a:
            st.markdown("### 📈 Most Drawn")
            st.dataframe(hot.head(5), use_container_width=True, hide_index=True)

        with b:
            st.markdown("### 💎 Less Drawn")
            st.dataframe(cold.head(5), use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-box">
    ℹ️ UK LottoAI is a research and analytics platform only. It does not predict lottery results.
    All numbers are generated from historical data and selected strategy criteria.
    </div>
    """, unsafe_allow_html=True)

elif section == "Number Analysis":

    st.markdown("## Number Analysis")
    st.dataframe(freq_df.sort_values("Frequency", ascending=False), use_container_width=True)

elif section == "Odd / Even":

    st.markdown("## Odd / Even Analysis")

    split_df = pd.DataFrame(
        odd_even_counter.items(),
        columns=["Split", "Occurrences"]
    ).sort_values("Occurrences", ascending=False)

    st.dataframe(split_df, use_container_width=True)

elif section == "About":

    st.markdown("## About UK LottoAI")
    st.write("""
    **UK LottoAI** was created by **AR Taylor**.

    It is a lottery research and analytics platform.

    It analyses historical patterns and offers different number-selection strategies.

    It does not increase the mathematical odds of a random lottery draw.
    """)
