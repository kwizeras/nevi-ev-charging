"""
Fetch EV charging station data from AFDC (Alternative Fuels Data Center) API.
This script pulls all U.S. electric charging stations and saves to CSV.

AFDC API docs: https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/

To get a free API key: https://developer.nrel.gov/signup/
"""

import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NREL_API_KEY = os.getenv("NREL_API_KEY")
BASE_URL = "https://developer.nrel.gov/api/alt-fuel-stations/v1.json"

# All U.S. states + DC
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]


def fetch_stations_for_state(state: str, api_key: str) -> list:
    """Fetch all EV stations for a single state."""
    params = {
        "api_key": api_key,
        "fuel_type": "ELEC",
        "state": state,
        "status": "all",  # E=available, P=planned, T=temp unavailable
        "access": "public",
        "limit": "all",
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        stations = data.get("fuel_stations", [])
        print(f"  {state}: {len(stations)} stations")
        return stations
    except requests.RequestException as e:
        print(f"  {state}: ERROR - {e}")
        return []


def fetch_all_stations(api_key: str) -> pd.DataFrame:
    """Fetch stations for all U.S. states and return as DataFrame."""
    all_stations = []
    
    print("Fetching EV charging stations from AFDC API...")
    print("-" * 50)
    
    for state in US_STATES:
        stations = fetch_stations_for_state(state, api_key)
        all_stations.extend(stations)
    
    print("-" * 50)
    print(f"Total stations fetched: {len(all_stations)}")
    
    df = pd.DataFrame(all_stations)
    return df


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and add useful derived columns."""
    
    # Key columns to keep (AFDC returns many fields)
    keep_cols = [
        "id", "station_name", "street_address", "city", "state", "zip",
        "latitude", "longitude", "status_code",
        "open_date", "expected_date",
        "ev_connector_types", "ev_dc_fast_num", "ev_level1_evse_num", "ev_level2_evse_num",
        "ev_network", "ev_pricing", "facility_type",
        "owner_type_code", "access_code", "access_days_time",
        "nrel_network", "updated_at",
    ]
    
    # Keep only columns that exist
    existing_cols = [c for c in keep_cols if c in df.columns]
    df = df[existing_cols].copy()
    
    # Parse dates
    for date_col in ["open_date", "expected_date", "updated_at"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    # Derive charger type category
    def classify_charger(row):
        dcfc = row.get("ev_dc_fast_num", 0) or 0
        l2 = row.get("ev_level2_evse_num", 0) or 0
        l1 = row.get("ev_level1_evse_num", 0) or 0
        if dcfc > 0:
            return "DCFC"
        elif l2 > 0:
            return "Level 2"
        elif l1 > 0:
            return "Level 1"
        return "Unknown"
    
    df["charger_type"] = df.apply(classify_charger, axis=1)
    
    # Total ports
    df["total_ports"] = (
        df["ev_dc_fast_num"].fillna(0).astype(int) +
        df["ev_level2_evse_num"].fillna(0).astype(int) +
        df["ev_level1_evse_num"].fillna(0).astype(int)
    )
    
    # Status description
    status_map = {
        "E": "Available",
        "P": "Planned",
        "T": "Temporarily Unavailable",
    }
    df["status"] = df["status_code"].map(status_map).fillna("Unknown")
    
    # Year opened (for time series)
    if "open_date" in df.columns:
        df["open_year"] = df["open_date"].dt.year
    
    # Days since opened (for lag analysis)
    if "open_date" in df.columns:
        df["days_since_open"] = (datetime.now() - df["open_date"]).dt.days
    
    return df


def main():
    if not NREL_API_KEY or NREL_API_KEY == "your_nrel_api_key_here":
        print("ERROR: Please set NREL_API_KEY in .env file")
        print("Get a free key at: https://developer.nrel.gov/signup/")
        return
    
    # Fetch data
    df_raw = fetch_all_stations(NREL_API_KEY)
    
    if df_raw.empty:
        print("No data fetched. Check API key and network connection.")
        return
    
    # Clean and enrich
    df = clean_and_enrich(df_raw)
    
    # Save to CSV
    output_path = "data/afdc_stations.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} stations to {output_path}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)
    print(f"Total stations: {len(df):,}")
    print(f"States covered: {df['state'].nunique()}")
    print(f"\nBy charger type:")
    print(df["charger_type"].value_counts().to_string())
    print(f"\nBy status:")
    print(df["status"].value_counts().to_string())
    print(f"\nTop 10 states by station count:")
    print(df["state"].value_counts().head(10).to_string())


if __name__ == "__main__":
    main()
