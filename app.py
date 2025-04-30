import streamlit as st
from src.profiles import load_voters, generate_reaction
import pandas as pd
import random
import math

st.set_page_config(page_title="Political Agents", layout="wide")

# --- Define Party Colors ---
PARTY_COLORS = {
    "Democrat": "#007bff",
    "Republican": "#dc3545",
    "Independent": "#6c757d",
}
DEFAULT_PARTY_COLOR = "#adb5bd"


# --- Helper Function for Visualization ---
def create_party_viz_html(df, grid_size=100):
    """Generates HTML for party distribution dots in a grid (dots below labels)."""
    if df.empty:
        return "<small>No voters match the current filters.</small>"

    # --- Data Preparation ---
    party_col = 'party_id'
    df = df.copy()
    df['display_party'] = df[party_col].replace({
        'Democratic Party': 'Democrat',
        'Republican Party': 'Republican',
    }).fillna('Unknown')
    main_parties = ['Democrat', 'Republican', 'Independent']
    df['display_party'] = df['display_party'].apply(
        lambda x: x if x in main_parties else 'Independent'
    )
    counts = df['display_party'].value_counts()
    total_filtered = len(df)

    # --- Scaling for Grid ---
    dots_data = {}
    dot_order = ['Democrat', 'Republican', 'Independent']
    remaining_dots = grid_size

    if total_filtered <= grid_size:
        for party in dot_order:
            dots_data[party] = counts.get(party, 0)
        actual_dots_shown = total_filtered
    else:
        actual_dots_shown = grid_size
        proportions = {party: counts.get(party, 0) / total_filtered for party in dot_order}
        calculated_dots = 0
        for party in dot_order[:-1]:
            num_dots = int(round(proportions[party] * grid_size))
            dots_data[party] = num_dots
            calculated_dots += num_dots
        dots_data[dot_order[-1]] = grid_size - calculated_dots

    # --- HTML Generation ---
    html = f"<div class='viz-container'>"
    html += f"<div class='viz-header'><b>Sample Size</b> ({total_filtered} voters represented in {actual_dots_shown} dots):</div>"
    html += "<div class='viz-content'>" # This div no longer needs flex

    # Labels Part
    labels_html = "<div class='viz-labels'>" # Added bottom margin via CSS
    for party in dot_order:
        count = counts.get(party, 0) # Show real count in label
        color = PARTY_COLORS.get(party, DEFAULT_PARTY_COLOR)
        # Removed percentage display
        labels_html += f"<div class='label-item'><span class='dot-label' style='background-color: {color};'></span> {party}: {count}</div>"
    labels_html += "</div>"
    html += labels_html

    # Dot Grid Part
    dots_html = "<div class='dot-grid'>"
    for party in dot_order:
        num_dots_to_show = dots_data.get(party, 0)
        color = PARTY_COLORS.get(party, DEFAULT_PARTY_COLOR)
        dots_html += f'<span class="dot" style="background-color: {color};" title="{party}"></span>' * num_dots_to_show
    dots_html += "</div>"
    html += dots_html

    html += "</div></div>"
    return html


# --- Custom Styles ---
st.markdown("""
    <style>
        /* --- Header Styles --- */
        .title { font-size: 2.5em; font-weight: 700; margin-bottom: 0.1em; color: #333; }
        .subtitle { font-size: 1.2em; color: #555; margin-bottom: 1.5em; }

        /* --- Voter Card Styles --- */
        .voter-card {
            border: 1px solid #e0e0e0;
            padding: 1.2em;
            border-radius: 8px;
            background-color: #ffffff;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            line-height: 1.6;
        }
        .voter-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-color: #cccccc;
        }
        .voter-info {
            font-size: 0.95em;
            color: #333;
            margin-bottom: 0.8em;
        }
        .voter-name {
            font-weight: 600;
            font-size: 1.1em;
            color: #000;
        }
        .voter-details {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 1em;
        }
        .reaction-header {
            font-weight: 600;
            font-size: 1em;
            color: #111;
            margin-bottom: 0.3em;
        }

        /* --- Dot Visualization Styles --- */
        .viz-container {
            margin-top: 1em; padding: 0.8em; border: 1px solid #eee;
            border-radius: 4px; background-color: #f8f9fa;
        }
        .viz-header { font-size: 0.9em; margin-bottom: 8px; }
        .viz-content { /* No longer using flex here */ }
        .viz-labels {
             /* Removed margin-right, flex-shrink */
             margin-bottom: 10px; /* Add space between labels and grid */
        }
        .label-item { font-size: 0.85em; margin-bottom: 3px; white-space: nowrap; }
        .dot-label {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 3px; margin-right: 5px; vertical-align: middle;
        }
        .dot-grid {
            display: grid;
            grid-template-columns: repeat(10, 9px); /* 10 columns */
            gap: 2px;
            line-height: 0;
            width: fit-content; /* Make grid only as wide as needed */
            margin-left: auto;  /* Center the grid horizontally */
            margin-right: auto; /* Center the grid horizontally */
        }
        .dot {
            display: inline-block; width: 9px; height: 9px;
            border-radius: 50%; vertical-align: middle;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">Political Agents</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Fictional voter reactions based on survey profiles. Enter text below.</div>', unsafe_allow_html=True)

# --- Load Data ---
# ... (rest of the code is unchanged) ...
@st.cache_data
def cached_load_voters():
    try:
        return load_voters()
    except FileNotFoundError:
        st.error("Error: 'sample_voter_file.csv' not found. Please make sure it's in the correct directory.")
        return pd.DataFrame()

voters_df = cached_load_voters()

if voters_df.empty:
    st.stop()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filter Voters")
    if 'party_id' not in voters_df.columns or 'ideology' not in voters_df.columns:
        st.error("Error: Required columns ('party_id', 'ideology') not found in the data.")
        st.stop()

    party_options = ["All"] + sorted(voters_df["party_id"].dropna().unique())
    selected_party = st.selectbox(
        "Party ID", party_options, help="Filter voters by party affiliation."
    )

    ideology_options = ["All"] + sorted(voters_df["ideology"].dropna().unique())
    selected_ideology = st.selectbox(
        "Ideology", ideology_options, help="Filter voters by ideology."
    )

    # --- Apply Filters ---
    filtered_df = voters_df.copy()
    if selected_party != "All":
        filtered_df = filtered_df[filtered_df["party_id"] == selected_party]
    if selected_ideology != "All":
        filtered_df = filtered_df[filtered_df["ideology"] == selected_ideology]

    # --- Sidebar Visualization ---
    st.divider()
    viz_html = create_party_viz_html(filtered_df, grid_size=100)
    st.markdown(viz_html, unsafe_allow_html=True)


# --- Input Speech ---
speech = st.text_area("Paste your content below:", height=200, placeholder="Enter a political speech, news article excerpt, or statement...")
generate = st.button("Generate Reactions")
st.divider()

# --- Show Reactions (using Voter Cards) ---
if speech and generate:
    if filtered_df.empty:
        st.warning("No voters match the selected filters. Please broaden your criteria.")
    else:
        sample_size = min(3, len(filtered_df))
        sampled_voters = filtered_df.sample(n=sample_size)

        st.subheader(f"Simulated Reactions from {sample_size} Voters:")

        with st.spinner("Simulating voter reactions... this may take a moment."):
            for _, row in sampled_voters.iterrows():
                try:
                    reaction = generate_reaction(speech, row)
                except Exception as e:
                    st.error(f"Could not generate reaction for {row.get('name', 'Unknown Voter')}: {e}")
                    reaction = "Error generating reaction."

                # Display using the new Voter Card style
                card_content = f"""
                <div class="voter-card">
                    <div class="voter-name">{row.get('name', 'N/A')}</div>
                    <div class="voter-info">
                        {row.get('age_group', 'N/A')} | {row.get('ideology', 'N/A')} | {row.get('party_id', 'N/A')}
                    </div>
                    <div class="voter-details">
                        District: {row.get('congressional_district', 'N/A')} | Education: {row.get('education_expanded', 'N/A')} | Race: {row.get('race_expanded', 'N/A')} | Income: {row.get('income', 'N/A')}
                    </div>
                    <div class="reaction-header">Reaction:</div>
                    {reaction}
                </div>
                """
                st.markdown(card_content, unsafe_allow_html=True)
