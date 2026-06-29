import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import random
import os

st.set_page_config(page_title="UK LottoAI", page_icon="🎯", layout="wide")

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
    font-size:32px;
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

st.sidebar.markdown("# 🎯 UK LottoAI")
st.sidebar.caption("Created by AR Taylor")

section = st.sidebar.radio(
    "NAVIGATION",
    ["Dashboard", "Number Analysis", "Odd / Even", "About"]
)

st.sidebar.divider()
st.sidebar.markdown("## ⚙️ Selector Optimisation")
st.sidebar.caption("""
**5 = Neutral** — follows historical pattern  
Below 5 biases lower/even/smaller  
Above 5 biases higher/odd/larger
""")

frequency_bias = st.sidebar.slider("Frequency Importance", 0, 10, 5)
recent_bias = st.sidebar.slider("Recent Form Importance", 0, 10, 5)
overdue_bias = st.sidebar.slider("Overdue Importance", 0, 10, 5)
odd_even_bias = st.sidebar.slider("Odd / Even Bias", 0, 10, 5)
low_high_bias = st.sidebar.slider("Low / High Bias", 0, 10, 5)
sum_bias = st.sidebar.slider("Sum Range Bias", 0, 10, 5)
gap_bias = st.sidebar.slider("Gap Balance", 0, 10, 5)
pair_bias = st.sidebar.slider("Pair Balance", 0, 10, 5)

DATA_PATH = "LotteryAI/data/lotto.csv"

if not os.path.exists(DATA_PATH):
    st.error("lotto.csv not found in LotteryAI/data/")
    st.stop()

lotto = pd.read_csv(DATA_PATH, header=None)

number_cols = [5, 6, 7, 8, 9, 10]
lotto = lotto.dropna(subset=number_cols)
lotto[number_cols] = lotto[number_cols].astype(int)

draws = lotto[number_cols].values.tolist()

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

freq_df = pd.DataFrame({
    "Number": list(range(1, 60)),
    "Frequency": [frequency.get(n, 0) for n in range(1, 60)]
})

hot = freq_df.sort_values("Frequency", ascending=False)
cold = freq_df.sort_values("Frequency", ascending=True)

avg_sum = sum(draw_sums) / len(draw_sums)

def normalise(value, max_value):
    if max_value == 0:
        return 0
    return value / max_value

max_freq = max(frequency.values())
max_recent = max(recent_frequency.values()) if recent_frequency else 1
max_overdue = max(latest_index - last_seen.get(n, 0) for n in range(1, 60))

def number_base_score(n):
    freq_component = normalise(frequency.get(n, 0), max_freq)
    recent_component = normalise(recent_frequency.get(n, 0), max_recent)
    overdue_component = normalise(latest_index - last_seen.get(n, 0), max_overdue)

    f_weight = 1 + ((frequency_bias - 5) / 5)
    r_weight = 1 + ((recent_bias - 5) / 5)
    o_weight = 1 + ((overdue_bias - 5) / 5)

    return (
        freq_component * f_weight +
        recent_component * r_weight +
        overdue_component * o_weight
    )

def historical_pattern_score(pattern, counter):
    most_common = counter.most_common(1)[0][1]
    return counter.get(pattern, 0) / most_common

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

def score_line(numbers):
    total, odd, even, low, high, spread, consecutive_pairs, primes = line_features(numbers)

    base = sum(number_base_score(n) for n in numbers)

    odd_even_pattern = f"{odd}/{even}"
    low_high_pattern = f"{low}/{high}"

    hist_odd_even = historical_pattern_score(odd_even_pattern, odd_even_counter)
    hist_low_high = historical_pattern_score(low_high_pattern, low_high_counter)

    odd_even_direction = hist_odd_even
    low_high_direction = hist_low_high

    if odd_even_bias < 5:
        odd_even_direction += (even - odd) * 0.08
    elif odd_even_bias > 5:
        odd_even_direction += (odd - even) * 0.08

    if low_high_bias < 5:
        low_high_direction += (low - high) * 0.08
    elif low_high_bias > 5:
        low_high_direction += (high - low) * 0.08

    sum_score = 1 - abs(total - avg_sum) / avg_sum

    if sum_bias < 5:
        sum_score += (avg_sum - total) / 300
    elif sum_bias > 5:
        sum_score += (total - avg_sum) / 300

    pair_score = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            pair_score += pair_counter.get((numbers[i], numbers[j]), 0)

    pair_score = normalise(pair_score, max(pair_counter.values()))

    gap_score = spread / 58
    if gap_bias < 5:
        gap_score = 1 - gap_score

    final = (
        base * 30 +
        hist_odd_even * 20 +
        hist_low_high * 20 +
        odd_even_direction * (odd_even_bias * 4) +
        low_high_direction * (low_high_bias * 4) +
        sum_score * (sum_bias * 4) +
        gap_score * (gap_bias * 3) +
        pair_score * (pair_bias * 5)
    )

    return final

def generate_numbers():
    best_line = None
    best_score = -1

    for _ in range(8000):
        candidate = sorted(random.sample(range(1, 60), 6))
        total, odd, even, low, high, spread, consecutive_pairs, primes = line_features(candidate)

        if spread < 18:
            continue
        if consecutive_pairs > 2:
            continue

        score = score_line(candidate)

        if score > best_score:
            best_score = score
            best_line = candidate

    return best_line if best_line else sorted(random.sample(range(1, 60), 6))

def display_ball_line(numbers):
    return "".join(f"<span class='number-ball'>{n}</span>" for n in numbers)

st.markdown("# 🎯 UK LottoAI")
st.caption("Created by AR Taylor • Professional UK National Lottery Analytics Platform")
st.divider()

if section == "Dashboard":

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Total Draws", f"{len(draws):,}")
    c2.metric("Most Frequent", int(hot.iloc[0]["Number"]))
    c3.metric("Least Frequent", int(cold.iloc[0]["Number"]))
    c4.metric("Average Sum", round(avg_sum, 1))
    c5.metric("Most Common Odd / Even", odd_even_counter.most_common(1)[0][0])
    c6.metric("Most Common Low / High", low_high_counter.most_common(1)[0][0])

    lucky_dips = [generate_numbers() for _ in range(5)]

    left, right = st.columns([2, 1.3])

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("## LUCKY DIP SELECTIONS")

        for idx, numbers in enumerate(lucky_dips, start=1):
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

        if st.button("↻ Generate New Lucky Dips"):
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("## HISTORICAL SUMMARY")
        st.write(f"Odd / Even ({odd_even_counter.most_common(1)[0][0]}) — {round(odd_even_counter.most_common(1)[0][1] / len(draws) * 100, 1)}%")
        st.write(f"Low / High ({low_high_counter.most_common(1)[0][0]}) — {round(low_high_counter.most_common(1)[0][1] / len(draws) * 100, 1)}%")
        st.write(f"Average Sum — {round(avg_sum, 1)}")
        st.write(f"Total Draws Analysed — {len(draws):,}")
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
        st.markdown("## HOT & COLD NUMBERS")

        a, b = st.columns(2)

        with a:
            st.markdown("### 🔥 Hot")
            st.dataframe(hot.head(5), use_container_width=True, hide_index=True)

        with b:
            st.markdown("### ❄️ Cold")
            st.dataframe(cold.head(5), use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-box">
    ℹ️ UK LottoAI is a research and analytics platform only. It does not predict lottery results.
    All numbers are generated from historical data and user-selected optimisation criteria.
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

    It analyses historical patterns and allows selector optimisation.

    It does not increase the mathematical odds of a random lottery draw.
    """)
