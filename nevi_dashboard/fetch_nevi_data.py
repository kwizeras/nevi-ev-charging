"""
Fetch and process NEVI (National Electric Vehicle Infrastructure) program data.

NEVI data sources:
1. DriveElectric.gov state plans: https://driveelectric.gov/state-plans
2. FHWA quarterly progress reports
3. Joint Office data

This script provides templates for processing NEVI award data and computing
deployment lags (time from award to operational).

Since NEVI data is often in PDFs, this script includes helpers for:
- Manual CSV entry
- PDF text extraction (if you want to automate)
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Template for NEVI awards data structure
NEVI_COLUMNS = [
    "state",
    "site_id", 
    "site_name",
    "location_city",
    "corridor",  # e.g., I-95, I-10
    "award_date",
    "award_amount_usd",
    "expected_operational_date",
    "actual_operational_date",
    "current_status",  # planned, under_construction, operational, delayed
    "charger_count",
    "charger_power_kw",
    "contractor",
    "utility",
    "notes",
]


def create_nevi_template():
    """Create an empty CSV template for manual NEVI data entry."""
    df = pd.DataFrame(columns=NEVI_COLUMNS)
    
    # Add example rows
    example_data = [
        {
            "state": "CA",
            "site_id": "CA-NEVI-001",
            "site_name": "Barstow Travel Center",
            "location_city": "Barstow",
            "corridor": "I-15",
            "award_date": "2023-06-15",
            "award_amount_usd": 500000,
            "expected_operational_date": "2024-06-15",
            "actual_operational_date": "2024-09-01",
            "current_status": "operational",
            "charger_count": 4,
            "charger_power_kw": 150,
            "contractor": "ChargePoint",
            "utility": "SCE",
            "notes": "Example entry - replace with real data",
        },
        {
            "state": "TX",
            "site_id": "TX-NEVI-001",
            "site_name": "Fort Stockton Plaza",
            "location_city": "Fort Stockton",
            "corridor": "I-10",
            "award_date": "2023-08-01",
            "award_amount_usd": 600000,
            "expected_operational_date": "2024-08-01",
            "actual_operational_date": None,
            "current_status": "under_construction",
            "charger_count": 4,
            "charger_power_kw": 150,
            "contractor": "EVgo",
            "utility": "Oncor",
            "notes": "Example - delayed due to interconnection",
        },
    ]
    
    df = pd.DataFrame(example_data)
    output_path = Path("data/nevi_awards_template.csv")
    df.to_csv(output_path, index=False)
    print(f"Created template: {output_path}")
    print("\nEdit this file with real NEVI award data from state plans and reports.")
    return df


def load_nevi_data(filepath: str = "data/nevi_awards.csv") -> pd.DataFrame:
    """Load NEVI awards data."""
    df = pd.read_csv(
        filepath,
        parse_dates=["award_date", "expected_operational_date", "actual_operational_date"]
    )
    return df


def compute_deployment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute deployment lag metrics:
    - expected_duration: days from award to expected operational
    - actual_duration: days from award to actual operational  
    - delay_days: actual - expected (positive = delayed)
    """
    df = df.copy()
    
    # Expected duration
    df["expected_duration_days"] = (
        df["expected_operational_date"] - df["award_date"]
    ).dt.days
    
    # Actual duration (only for operational sites)
    df["actual_duration_days"] = (
        df["actual_operational_date"] - df["award_date"]
    ).dt.days
    
    # Delay (positive = late, negative = early)
    df["delay_days"] = (
        df["actual_operational_date"] - df["expected_operational_date"]
    ).dt.days
    
    # Status flags
    df["is_operational"] = df["current_status"] == "operational"
    df["is_delayed"] = df["delay_days"] > 0
    
    return df


def summarize_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Compute state-level NEVI deployment summary."""
    summary = df.groupby("state").agg(
        total_sites=("site_id", "count"),
        operational_sites=("is_operational", "sum"),
        total_award_usd=("award_amount_usd", "sum"),
        avg_expected_duration=("expected_duration_days", "mean"),
        avg_actual_duration=("actual_duration_days", "mean"),
        avg_delay_days=("delay_days", "mean"),
        delayed_sites=("is_delayed", "sum"),
    ).reset_index()
    
    summary["pct_operational"] = (
        summary["operational_sites"] / summary["total_sites"] * 100
    ).round(1)
    
    summary["pct_delayed"] = (
        summary["delayed_sites"] / summary["operational_sites"] * 100
    ).round(1)
    
    return summary


def merge_with_afdc(nevi_df: pd.DataFrame, afdc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Attempt to match NEVI sites with AFDC stations.
    
    Matching strategies:
    1. Exact match on coordinates (if available)
    2. Fuzzy match on name + city + state
    3. Manual matching via site_id
    """
    # For now, simple merge by state to add AFDC context
    afdc_summary = afdc_df.groupby("state").agg(
        afdc_total_stations=("id", "count"),
        afdc_dcfc_stations=("charger_type", lambda x: (x == "DCFC").sum()),
    ).reset_index()
    
    merged = nevi_df.merge(afdc_summary, on="state", how="left")
    return merged


def generate_lag_report(df: pd.DataFrame) -> str:
    """Generate a text report on deployment lags for the paper."""
    metrics = compute_deployment_metrics(df)
    summary = summarize_by_state(metrics)
    
    report = []
    report.append("=" * 60)
    report.append("NEVI DEPLOYMENT LAG ANALYSIS")
    report.append("=" * 60)
    report.append("")
    
    # Overall stats
    total = len(metrics)
    operational = metrics["is_operational"].sum()
    report.append(f"Total NEVI sites tracked: {total}")
    report.append(f"Operational: {operational} ({operational/total*100:.1f}%)")
    report.append("")
    
    # Duration stats
    op_sites = metrics[metrics["is_operational"]]
    if len(op_sites) > 0:
        report.append("DEPLOYMENT DURATION (Award → Operational):")
        report.append(f"  Mean: {op_sites['actual_duration_days'].mean():.0f} days")
        report.append(f"  Median: {op_sites['actual_duration_days'].median():.0f} days")
        report.append(f"  Min: {op_sites['actual_duration_days'].min():.0f} days")
        report.append(f"  Max: {op_sites['actual_duration_days'].max():.0f} days")
        report.append("")
        
        # Delay stats
        report.append("DELAYS (vs Expected Date):")
        delayed = op_sites[op_sites["is_delayed"]]
        report.append(f"  Sites delayed: {len(delayed)} ({len(delayed)/len(op_sites)*100:.1f}%)")
        if len(delayed) > 0:
            report.append(f"  Mean delay: {delayed['delay_days'].mean():.0f} days")
            report.append(f"  Max delay: {delayed['delay_days'].max():.0f} days")
        report.append("")
    
    # State comparison
    report.append("STATE COMPARISON:")
    report.append("-" * 40)
    cols = ["state", "total_sites", "pct_operational", "avg_delay_days"]
    report.append(summary[cols].to_string(index=False))
    
    return "\n".join(report)


def main():
    # Create template if no data exists
    nevi_path = Path("data/nevi_awards.csv")
    
    if not nevi_path.exists():
        print("No NEVI data found. Creating template...")
        create_nevi_template()
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("""
1. Gather NEVI data from these sources:
   - State NEVI plans: https://driveelectric.gov/state-plans
   - FHWA quarterly reports
   - State DOT websites (many publish project trackers)

2. Copy data/nevi_awards_template.csv to data/nevi_awards.csv

3. Fill in real data for the states you're analyzing
   (Start with CA, TX, MS for your 3-state comparison)

4. Run this script again to generate analysis
""")
        return
    
    # Load and analyze
    print("Loading NEVI data...")
    df = load_nevi_data(str(nevi_path))
    
    print("\nComputing metrics...")
    df = compute_deployment_metrics(df)
    
    print("\n" + generate_lag_report(df))
    
    # Save enriched data
    output_path = Path("data/nevi_awards_enriched.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved enriched data to: {output_path}")


if __name__ == "__main__":
    main()
