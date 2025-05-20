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

# Configure basic logging for error tracking within this module.
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom Exception for missing columns.
# This could ideally be in a shared exceptions module if the project grows.
class MissingColumnsError(Exception):
    """Custom exception raised when essential columns are missing from the voter data."""
    pass

# --- Gemini API Configuration ---
# Attempt to configure the Gemini API key from Streamlit secrets.
# This block ensures that the API is configured upon module import.
try:
    if "GEMINI_API_KEY" not in st.secrets:
        logging.error("GEMINI_API_KEY not found in Streamlit secrets. Reaction generation will fail.")
        # Application behavior depends on how critical reaction generation is.
        # For now, it logs an error; subsequent API calls will fail.
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e: # Catch any other unexpected errors during configuration.
    logging.error(f"Error configuring Gemini API: {e}. Reaction generation may be affected.")


# ESSENTIAL_COLUMNS: Defines the list of column names that are considered
# critical for the application's functionality, particularly for constructing
# prompts for the AI model and for data display.
ESSENTIAL_COLUMNS = [
    'name', 'age', 'congressional_district', 'ideology', 'party_id',
    'income', 'education_expanded', 'race_expanded', 'voted_2020',
    'vote_intention_2024'
]

@st.cache_data # Streamlit decorator to cache the result of this function.
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
    except FileNotFoundError:
        # Let this exception propagate to be handled by the caller (app.py)
        # which will then raise a more specific VoterDataNotFoundError.
        logging.error("sample_voter_file.csv not found.")
        raise

    # Validate that all essential columns are present in the DataFrame.
    missing_cols = [col for col in ESSENTIAL_COLUMNS if col not in df.columns]
    if missing_cols:
        error_msg = f"Missing essential columns in voter data: {', '.join(missing_cols)}"
        logging.error(error_msg)
        raise MissingColumnsError(error_msg)
    return df

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
    # --- Model Preparation and API Key Check ---
    try:
        # Crucially check if the API key was successfully configured.
        if not genai.API_KEY: # genai.API_KEY is None if not configured
            logging.error("Gemini API key not configured. Cannot generate reaction.")
            return "Error: API key not configured. Reaction generation unavailable."

        # Initialize the generative model.
        # Using 'gemini-1.0-pro' as a robust choice. 'gemini-2.0-flash' could be an alternative.
        model = genai.GenerativeModel('gemini-1.0-pro')
    except Exception as e:
        logging.error(f"Error initializing GenerativeModel: {e}")
        return "An error occurred while preparing the reaction generator. Please try again later."

    # --- Prompt Construction and Data Validation ---
    # Safeguard: Validate that voter_row contains essential columns.
    # This is a secondary check; `load_voters` should ensure data integrity.
    # Default to 'N/A' if a key is missing or value is NaN, with a warning.
    for col in ESSENTIAL_COLUMNS:
        if col not in voter_row or pd.isna(voter_row[col]):
            logging.warning(
                f"Missing or NaN value for essential column '{col}' in voter row: "
                f"{voter_row.get('name', 'Unknown Voter')}. Using 'N/A'."
            )
            voter_row[col] = 'N/A' # Provide a default value for prompt construction.

    # Construct the prompt for the language model.
    # The prompt provides context about the voter's profile and the speech.
    # .get(col, 'N/A') is used for robust access to voter_row fields.
    prompt = f"""
You are simulating a voter named {voter_row.get('name', 'N/A')}, age {voter_row.get('age', 'N/A')}, in district {voter_row.get('congressional_district', 'N/A')}.
They are a {voter_row.get('ideology', 'N/A')} {voter_row.get('party_id', 'N/A')}, income: {voter_row.get('income', 'N/A')}, education: {voter_row.get('education_expanded', 'N/A')}, race: {voter_row.get('race_expanded', 'N/A')}.
They voted in 2020: {voter_row.get('voted_2020', 'N/A')} and their 2024 intention is: {voter_row.get('vote_intention_2024', 'N/A')}.

Given this speech:
\"\"\"{speech}\"\"\"

What is their likely emotional and political reaction in 2–3 sentences?
"""
    # --- API Call and Response Handling ---
    try:
        response = model.generate_content(prompt)
        # Extract the text part of the response.
        reaction = response.text.strip()
    except Exception as e:
        # Log detailed error information for debugging.
        logging.error(f"Error during Gemini API call for voter {voter_row.get('name', 'Unknown Voter')}: {e}")
        # If available, log specific feedback from the API (e.g., safety blocks).
        if hasattr(response, 'prompt_feedback'):
            logging.error(f"Gemini response feedback: {response.prompt_feedback}")
        # Return a generic error message to the user.
        reaction = "An error occurred while generating the reaction. Please try again later or contact support if the issue persists."

    return reaction