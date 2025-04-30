import streamlit as st
from src.profiles import load_voters, generate_reaction
import pandas as pd
import random

st.set_page_config(page_title="Political Agents", layout="wide")

# --- Custom Styles ---
st.markdown("""
    <style>
        .title {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 0.1em;
        }
        .subtitle {
            font-size: 1.2em;
            color: #555;
            margin-bottom: 1.5em;
        }
        .voter-box {
            border: 1px solid #ddd;
            padding: 1em;
            border-radius: 1em;
            background-color: #f9f9f9;
            margin-bottom: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">Political Agents</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">This app uses synthetic voter profiles—based on CESS-style survey data—to generate reactions.</div>', unsafe_allow_html=True)

# --- Load Data ---
voters_df = load_voters()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filter Voters")
    selected_party = st.selectbox("Party ID", ["All"] + sorted(voters_df["party_id"].dropna().unique()))
    selected_ideology = st.selectbox("Ideology", ["All"] + sorted(voters_df["ideology"].dropna().unique()))

# --- Apply Filters ---
filtered_df = voters_df.copy()
if selected_party != "All":
    filtered_df = filtered_df[filtered_df["party_id"] == selected_party]
if selected_ideology != "All":
    filtered_df = filtered_df[filtered_df["ideology"] == selected_ideology]

# --- Input Speech ---
speech = st.text_area("Paste your content below:", height=200)
generate = st.button("Regenerate Reactions")

# --- Show Reactions (default 3 voters)
if speech and generate:
    sampled_voters = filtered_df.sample(n=min(3, len(filtered_df)), random_state=random.randint(1, 9999))
    with st.spinner("Simulating voter reactions..."):
        for _, row in sampled_voters.iterrows():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{row['name']}** — {row['age_group']}, {row['ideology']}, {row['party_id']}")
                st.caption(f"CD: {row['congressional_district']} | Ed.: {row['education_expanded']}")
            with col2:
                reaction = generate_reaction(speech, row)
                st.markdown(f'<div class="voter-box"><strong>Reaction:</strong><br>{reaction}</div>', unsafe_allow_html=True)
