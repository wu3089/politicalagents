import pandas as pd
import google.generativeai as genai # Changed import
import streamlit as st

# Configure the Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_data
def load_voters():
    return pd.read_csv("sample_voter_file.csv")

def generate_reaction(speech, voter_row):
    # Prepare the model
    model = genai.GenerativeModel('gemini-2.0-flash') # Or another Gemini model

    prompt = f"""
You are simulating a voter named {voter_row['name']}, age {voter_row['age']}, in district {voter_row['congressional_district']}.
They are a {voter_row['ideology']} {voter_row['party_id']}, income: {voter_row['income']}, education: {voter_row['education_expanded']}, race: {voter_row['race_expanded']}.
They voted in 2020: {voter_row['voted_2020']} and their 2024 intention is: {voter_row['vote_intention_2024']}.

Given this speech:
\"\"\"{speech}\"\"\"

What is their likely emotional and political reaction in 2–3 sentences?
"""
    # Generate content using Gemini
    response = model.generate_content(prompt)

    # Extract the text response
    # Add error handling in case the response doesn't contain text
    try:
        reaction = response.text.strip()
    except Exception as e:
        st.error(f"Error generating reaction: {e}")
        # You might want to inspect 'response.prompt_feedback' or 'response.candidates'
        st.error(f"Gemini response feedback: {response.prompt_feedback}")
        reaction = "Could not generate reaction."

    return reaction