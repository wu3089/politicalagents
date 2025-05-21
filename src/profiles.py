"""
Handles data loading for voter profiles and generation of simulated reactions
using a generative AI model (Google Gemini).

This module is responsible for:
- Loading voter data from a CSV file ('sample_voter_file.csv').
- Validating the presence of essential columns in the voter data.
- Configuring and interacting with the Google Gemini API to generate
  text-based reactions based on voter profiles and input speech.
"""
import pandas as pd
import google.generativeai as genai
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Exception for missing columns
class MissingColumnsError(Exception):
    """Custom exception raised when essential columns are missing from the voter data."""
    pass

# --- Gemini API Configuration ---
try:
    if "GEMINI_API_KEY" not in st.secrets:
        logger.error("GEMINI_API_KEY not found in Streamlit secrets")
        st.error("Gemini API key not configured. Please check your .streamlit/secrets.toml file.")
    else:
        # Configure the API key
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    st.error(f"Error configuring Gemini API: {e}")

# ESSENTIAL_COLUMNS: Defines the list of column names that are considered
# critical for the application's functionality, particularly for constructing
# prompts for the AI model and for data display.
ESSENTIAL_COLUMNS = [
    'name', 'age', 'congressional_district', 'ideology', 'party_id',
    'income', 'education_expanded', 'race_expanded', 'voted_2020',
    'vote_intention_2024'
]

@st.cache_data
def load_voters():
    """
    Loads voter data from 'sample_voter_file.csv' and validates essential columns.

    This function reads the voter data into a pandas DataFrame. It then checks
    if all columns listed in `ESSENTIAL_COLUMNS` are present in the DataFrame.
    If the file is not found or if columns are missing, it raises an appropriate
    exception.

    Raises:
        FileNotFoundError: If 'sample_voter_file.csv' cannot be found at the
                           expected location. This is typically caught by the
                           calling function in `app.py` and re-raised as
                           `VoterDataNotFoundError`.
        MissingColumnsError: If one or more columns listed in `ESSENTIAL_COLUMNS`
                             are not found in the loaded DataFrame. The error
                             message includes the names of the missing columns.

    Returns:
        pd.DataFrame: A DataFrame containing the voter data if loading and
                      validation are successful.
    """
    try:
        df = pd.read_csv("sample_voter_file.csv")
        logger.info(f"Successfully loaded {len(df)} voters")
        return df
    except FileNotFoundError:
        logger.error("sample_voter_file.csv not found")
        raise
    except Exception as e:
        logger.error(f"Error loading voter data: {e}")
        raise

def generate_reaction(speech, voter_row):
    """
    Generates a simulated voter reaction to a given speech using the Gemini API.

    Constructs a prompt based on the voter's demographic and political profile
    (from `voter_row`) and the input `speech`. It then calls the Gemini API
    to generate a textual reaction. Includes error handling for API key issues,
    model initialization, and API call failures.

    Args:
        speech (str): The speech or text content to which the voter reacts.
        voter_row (pd.Series): A pandas Series containing the data for a single
                               voter. Expected to contain keys from `ESSENTIAL_COLUMNS`.

    Returns:
        str: A string containing the simulated voter reaction (typically 2-3 sentences).
             In case of an error during generation (e.g., API key issue, model failure),
             a user-friendly error message string is returned.
    """
    try:
        # Check if API key is configured
        if "GEMINI_API_KEY" not in st.secrets:
            return "Error: Gemini API key not configured. Please check your .streamlit/secrets.toml file."

        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Successfully initialized Gemini model")

        # Construct the prompt
        prompt = f"""
You are simulating a voter named {voter_row.get('name', 'N/A')}, age {voter_row.get('age', 'N/A')}, in district {voter_row.get('congressional_district', 'N/A')}.
They are a {voter_row.get('ideology', 'N/A')} {voter_row.get('party_id', 'N/A')}, income: {voter_row.get('income', 'N/A')}, education: {voter_row.get('education_expanded', 'N/A')}, race: {voter_row.get('race_expanded', 'N/A')}.
They voted in 2020: {voter_row.get('voted_2020', 'N/A')} and their 2024 intention is: {voter_row.get('vote_intention_2024', 'N/A')}.

Given this speech:
\"\"\"{speech}\"\"\"

What is their likely emotional and political reaction in 2–3 sentences?
"""
        # Generate the reaction
        response = model.generate_content(prompt)
        reaction = response.text.strip()
        logger.info(f"Successfully generated reaction for {voter_row.get('name', 'Unknown Voter')}")
        return reaction

    except Exception as e:
        logger.error(f"Error generating reaction: {e}")
        if hasattr(e, 'prompt_feedback'):
            logger.error(f"Gemini feedback: {e.prompt_feedback}")
        return f"Error generating reaction: {str(e)}"