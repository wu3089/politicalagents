# Political Agents

This is a simple Streamlit app that allows you to input a political speech or tweet and see simulated reactions from synthetic voter profiles. 

## Features

*   Paste any political text to analyze.
*   View simulated reactions from a sample of synthetic voters.
*   Voter profiles are based on CESS-style survey data (using `sample_voter_file.csv`).
*   Filter the available voter pool by Party ID and Ideology via the sidebar.
*   Uses Google Gemini (via `google-generativeai` library) to generate plausible reactions.
*   Simple and interactive web interface built with Streamlit.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url> # Replace with your actual repo URL
    cd politicalagents
    ```

2.  **Create and activate a virtual environment:** (Recommended)
    ```bash
    python -m venv .venv
    # On macOS/Linux
    source .venv/bin/activate
    # On Windows
    # .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Voter Data:**
    *   Ensure you have the voter data file named `sample_voter_file.csv` in the root directory of the project. If your file has a different name or location, update the path in `src/profiles.py`.

5.  **API Key Configuration:**
    *   This application requires a Google Gemini API key.
    *   Create a directory named `.streamlit` in the project root if it doesn't exist:
        ```bash
        mkdir .streamlit
        ```
    *   Create a file named `secrets.toml` inside the `.streamlit` directory:
        ```bash
        touch .streamlit/secrets.toml
        ```
    *   Add your Gemini API key to `secrets.toml` like this:
        ```toml
        GEMINI_API_KEY = "YOUR_API_KEY_HERE"
        ```
    *   **Important:** Replace `"YOUR_API_KEY_HERE"` with your actual key. The `.gitignore` file is already configured to prevent this file from being committed to Git, protecting your key.

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Interact with the app:**
    *   The application will open in your web browser.
    *   Use the sidebar to filter voters by Party ID or Ideology if desired.
    *   Paste your political speech or text into the main text area.
    *   Click the "Regenerate Reactions" button.
    *   The app will display profiles and simulated reactions for a random sample of voters matching your filters.
