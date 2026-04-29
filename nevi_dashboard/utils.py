"""
Utility functions for the NEVI dashboard.
"""

import os
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str) -> str | None:
    """Look up a secret from Streamlit Cloud first, then .env / OS env."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


def load_station_data(filepath: str = "data/afdc_stations.csv") -> pd.DataFrame:
    """Load and prepare station data."""
    df = pd.read_csv(filepath, parse_dates=["open_date", "expected_date", "updated_at"])
    return df


def compute_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics by state."""
    summary = df.groupby("state").agg(
        total_stations=("id", "count"),
        dcfc_stations=("charger_type", lambda x: (x == "DCFC").sum()),
        level2_stations=("charger_type", lambda x: (x == "Level 2").sum()),
        total_ports=("total_ports", "sum"),
        dcfc_ports=("ev_dc_fast_num", "sum"),
        level2_ports=("ev_level2_evse_num", "sum"),
        available_stations=("status", lambda x: (x == "Available").sum()),
        planned_stations=("status", lambda x: (x == "Planned").sum()),
        median_open_year=("open_year", "median"),
    ).reset_index()
    
    summary["pct_dcfc"] = (summary["dcfc_stations"] / summary["total_stations"] * 100).round(1)
    summary["pct_available"] = (summary["available_stations"] / summary["total_stations"] * 100).round(1)
    
    return summary


def compute_deployment_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """Compute stations opened by year and charger type."""
    df_with_year = df[df["open_year"].notna()].copy()
    timeline = df_with_year.groupby(["open_year", "charger_type"]).size().reset_index(name="stations_opened")
    timeline["open_year"] = timeline["open_year"].astype(int)
    return timeline


def compute_network_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Compute station counts by network."""
    network = df.groupby("ev_network").agg(
        stations=("id", "count"),
        dcfc_ports=("ev_dc_fast_num", "sum"),
        level2_ports=("ev_level2_evse_num", "sum"),
    ).reset_index()
    network = network.sort_values("stations", ascending=False)
    return network


# State metadata (population, area for normalization)
STATE_METADATA = {
    "AL": {"name": "Alabama", "population": 5024279, "area_sq_mi": 52420},
    "AK": {"name": "Alaska", "population": 733391, "area_sq_mi": 665384},
    "AZ": {"name": "Arizona", "population": 7151502, "area_sq_mi": 113990},
    "AR": {"name": "Arkansas", "population": 3011524, "area_sq_mi": 53179},
    "CA": {"name": "California", "population": 39538223, "area_sq_mi": 163695},
    "CO": {"name": "Colorado", "population": 5773714, "area_sq_mi": 104094},
    "CT": {"name": "Connecticut", "population": 3605944, "area_sq_mi": 5543},
    "DE": {"name": "Delaware", "population": 989948, "area_sq_mi": 2489},
    "DC": {"name": "District of Columbia", "population": 689545, "area_sq_mi": 68},
    "FL": {"name": "Florida", "population": 21538187, "area_sq_mi": 65758},
    "GA": {"name": "Georgia", "population": 10711908, "area_sq_mi": 59425},
    "HI": {"name": "Hawaii", "population": 1455271, "area_sq_mi": 10932},
    "ID": {"name": "Idaho", "population": 1839106, "area_sq_mi": 83569},
    "IL": {"name": "Illinois", "population": 12812508, "area_sq_mi": 57914},
    "IN": {"name": "Indiana", "population": 6785528, "area_sq_mi": 36420},
    "IA": {"name": "Iowa", "population": 3190369, "area_sq_mi": 56273},
    "KS": {"name": "Kansas", "population": 2937880, "area_sq_mi": 82278},
    "KY": {"name": "Kentucky", "population": 4505836, "area_sq_mi": 40408},
    "LA": {"name": "Louisiana", "population": 4657757, "area_sq_mi": 52378},
    "ME": {"name": "Maine", "population": 1362359, "area_sq_mi": 35380},
    "MD": {"name": "Maryland", "population": 6177224, "area_sq_mi": 12406},
    "MA": {"name": "Massachusetts", "population": 7029917, "area_sq_mi": 10554},
    "MI": {"name": "Michigan", "population": 10077331, "area_sq_mi": 96714},
    "MN": {"name": "Minnesota", "population": 5706494, "area_sq_mi": 86936},
    "MS": {"name": "Mississippi", "population": 2961279, "area_sq_mi": 48432},
    "MO": {"name": "Missouri", "population": 6154913, "area_sq_mi": 69707},
    "MT": {"name": "Montana", "population": 1084225, "area_sq_mi": 147040},
    "NE": {"name": "Nebraska", "population": 1961504, "area_sq_mi": 77348},
    "NV": {"name": "Nevada", "population": 3104614, "area_sq_mi": 110572},
    "NH": {"name": "New Hampshire", "population": 1377529, "area_sq_mi": 9349},
    "NJ": {"name": "New Jersey", "population": 9288994, "area_sq_mi": 8723},
    "NM": {"name": "New Mexico", "population": 2117522, "area_sq_mi": 121590},
    "NY": {"name": "New York", "population": 20201249, "area_sq_mi": 54555},
    "NC": {"name": "North Carolina", "population": 10439388, "area_sq_mi": 53819},
    "ND": {"name": "North Dakota", "population": 779094, "area_sq_mi": 70698},
    "OH": {"name": "Ohio", "population": 11799448, "area_sq_mi": 44826},
    "OK": {"name": "Oklahoma", "population": 3959353, "area_sq_mi": 69899},
    "OR": {"name": "Oregon", "population": 4237256, "area_sq_mi": 98379},
    "PA": {"name": "Pennsylvania", "population": 13002700, "area_sq_mi": 46054},
    "RI": {"name": "Rhode Island", "population": 1097379, "area_sq_mi": 1545},
    "SC": {"name": "South Carolina", "population": 5118425, "area_sq_mi": 32020},
    "SD": {"name": "South Dakota", "population": 886667, "area_sq_mi": 77116},
    "TN": {"name": "Tennessee", "population": 6910840, "area_sq_mi": 42144},
    "TX": {"name": "Texas", "population": 29145505, "area_sq_mi": 268596},
    "UT": {"name": "Utah", "population": 3271616, "area_sq_mi": 84897},
    "VT": {"name": "Vermont", "population": 643077, "area_sq_mi": 9616},
    "VA": {"name": "Virginia", "population": 8631393, "area_sq_mi": 42775},
    "WA": {"name": "Washington", "population": 7614893, "area_sq_mi": 71298},
    "WV": {"name": "West Virginia", "population": 1793716, "area_sq_mi": 24230},
    "WI": {"name": "Wisconsin", "population": 5893718, "area_sq_mi": 65496},
    "WY": {"name": "Wyoming", "population": 576851, "area_sq_mi": 97813},
}


def enrich_with_metadata(df_summary: pd.DataFrame) -> pd.DataFrame:
    """Add population and area data for per-capita/density calculations."""
    df = df_summary.copy()
    df["state_name"] = df["state"].map(lambda x: STATE_METADATA.get(x, {}).get("name", x))
    df["population"] = df["state"].map(lambda x: STATE_METADATA.get(x, {}).get("population", None))
    df["area_sq_mi"] = df["state"].map(lambda x: STATE_METADATA.get(x, {}).get("area_sq_mi", None))
    
    df["stations_per_100k"] = (df["total_stations"] / df["population"] * 100000).round(2)
    df["dcfc_per_100k"] = (df["dcfc_stations"] / df["population"] * 100000).round(2)
    df["stations_per_1000_sqmi"] = (df["total_stations"] / df["area_sq_mi"] * 1000).round(2)
    
    return df


def get_eva_response(question: str, df: pd.DataFrame, chat_history: list = None) -> str:
    """
    Use Google Gemini to answer a natural language question about the data.
    EVA = EV Analysis Assistant
    """
    api_key = _get_secret("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "⚠️ Gemini API key not configured. Get a free key at: https://aistudio.google.com/app/apikey"
    
    # Compute summary stats for context
    summary = compute_state_summary(df)
    summary = enrich_with_metadata(summary)
    
    # Build context string
    system_context = f"""You are EVA (EV Analysis Assistant), a friendly and knowledgeable AI assistant specialized in U.S. EV charging infrastructure data. You help users understand charging station deployment, compare states, and identify trends.

CURRENT DATA SUMMARY:
- Total stations: {len(df):,}
- Total DCFC (DC Fast Charging) stations: {(df['charger_type'] == 'DCFC').sum():,}
- Total Level 2 stations: {(df['charger_type'] == 'Level 2').sum():,}
- States covered: {df['state'].nunique()}
- Date range: {df['open_date'].min()} to {df['open_date'].max()}

TOP 10 STATES BY STATION COUNT:
{summary.nlargest(10, 'total_stations')[['state_name', 'total_stations', 'dcfc_stations', 'stations_per_100k']].to_string(index=False)}

BOTTOM 10 STATES BY STATION COUNT:
{summary.nsmallest(10, 'total_stations')[['state_name', 'total_stations', 'dcfc_stations', 'stations_per_100k']].to_string(index=False)}

TOP 10 STATES BY DCFC PER CAPITA (per 100k people):
{summary.nlargest(10, 'dcfc_per_100k')[['state_name', 'dcfc_stations', 'dcfc_per_100k', 'population']].to_string(index=False)}

STATUS BREAKDOWN:
{df['status'].value_counts().to_string()}

NETWORK BREAKDOWN (top 10):
{df['ev_network'].value_counts().head(10).to_string()}

GUIDELINES:
- Be concise but informative
- Use specific numbers from the data
- If comparing states, mention per-capita metrics for fairness
- If the data doesn't support an answer, say so clearly
- Add relevant context about EV charging when helpful
"""
    
    try:
        # Create client with API key
        client = genai.Client(api_key=api_key)
        
        # Combine system context with user question
        full_prompt = f"{system_context}\n\nUser Question: {question}"
        
        # Generate response using the new API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )
        
        if response.text:
            return response.text
        else:
            return "⚠️ EVA received an empty response. Please try rephrasing your question."
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "resource exhausted" in error_msg.lower():
            return "⚠️ API rate limit reached. Please wait 1 minute and try again. (Free tier: 15 requests/min)"
        elif "403" in error_msg or "permission" in error_msg.lower():
            return "⚠️ API key invalid or lacks permission. Get a new key at: https://aistudio.google.com/app/apikey"
        elif "404" in error_msg:
            return f"⚠️ Model not found. Error: {error_msg}"
        else:
            return f"❌ Gemini API Error: {error_msg}"
