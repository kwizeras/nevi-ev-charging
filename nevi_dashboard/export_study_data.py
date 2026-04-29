"""
Export Study-Ready Dataset for DEVP 226 Final Project
Creates filtered subsets for paper analysis
"""

import pandas as pd
from datetime import datetime

def export_study_datasets():
    """Export multiple datasets for different analyses"""
    
    print("Loading AFDC data...")
    df = pd.read_csv('data/afdc_stations.csv')
    
    # Define column sets for different analyses
    
    # 1. CORE ANALYSIS COLUMNS (All analyses)
    core_columns = [
        'id', 'station_name', 'street_address', 'city', 'state', 'zip',
        'latitude', 'longitude',
        'charger_type', 'total_ports', 'ev_dc_fast_num', 'ev_level2_evse_num',
        'ev_network', 'owner_type_code', 'facility_type', 'access_code',
        'open_date', 'expected_date', 'open_year', 'days_since_open',
        'status', 'status_code', 'updated_at'
    ]
    
    # 2. DCFC ONLY (Your primary focus)
    print("\n1. Exporting DCFC stations only...")
    df_dcfc = df[df['charger_type'] == 'DCFC'][core_columns].copy()
    df_dcfc.to_csv('data/study_export_dcfc_only.csv', index=False)
    print(f"   [OK] Saved {len(df_dcfc):,} DCFC stations")
    
    # 3. THREE-STATE COMPARISON (CA, TX, MS)
    print("\n2. Exporting case study states (CA, TX, MS)...")
    df_three_states = df[df['state'].isin(['CA', 'TX', 'MS'])][core_columns].copy()
    df_three_states.to_csv('data/study_export_three_states.csv', index=False)
    
    # Breakdown by state
    for state in ['CA', 'TX', 'MS']:
        count = len(df_three_states[df_three_states['state'] == state])
        dcfc_count = len(df_three_states[(df_three_states['state'] == state) & 
                                         (df_three_states['charger_type'] == 'DCFC')])
        print(f"   {state}: {count:,} total ({dcfc_count:,} DCFC)")
    
    # 4. FULL DATASET (Study-ready subset)
    print("\n3. Exporting full dataset with study columns...")
    df[core_columns].to_csv('data/study_export_full.csv', index=False)
    print(f"   [OK] Saved all {len(df):,} stations")
    
    # 5. SUMMARY STATISTICS BY STATE
    print("\n4. Creating state summary statistics...")
    # Convert open_date to datetime if not already
    df_summary = df.copy()
    df_summary['open_date'] = pd.to_datetime(df_summary['open_date'], errors='coerce')
    
    state_summary = df_summary.groupby('state').agg({
        'id': 'count',
        'total_ports': 'sum',
        'ev_dc_fast_num': 'sum',
        'ev_level2_evse_num': 'sum'
    }).round(0)
    
    # Handle dates separately to avoid type errors
    date_summary = df_summary[df_summary['open_date'].notna()].groupby('state')['open_date'].agg(['min', 'max'])
    state_summary = state_summary.join(date_summary)
    
    state_summary.columns = ['total_stations', 'total_ports', 'dcfc_ports', 
                             'level2_ports', 'earliest_station', 'latest_station']
    state_summary = state_summary.sort_values('total_stations', ascending=False)
    state_summary.to_csv('data/study_state_summary.csv')
    print(f"   [OK] Saved summary for {len(state_summary)} states")
    
    # 6. NETWORK ANALYSIS
    print("\n5. Creating network operator summary...")
    network_summary = df.groupby('ev_network').agg({
        'id': 'count',
        'total_ports': 'sum',
        'ev_dc_fast_num': 'sum'
    }).sort_values('id', ascending=False).head(20)
    network_summary.columns = ['total_stations', 'total_ports', 'dcfc_ports']
    network_summary.to_csv('data/study_network_summary.csv')
    print(f"   [OK] Saved top 20 networks")
    
    # 7. TEMPORAL ANALYSIS (stations by year)
    print("\n6. Creating deployment timeline...")
    df_with_year = df[df['open_year'].notna()].copy()
    temporal = df_with_year.groupby(['open_year', 'charger_type']).size().reset_index(name='count')
    temporal_pivot = temporal.pivot(index='open_year', columns='charger_type', values='count').fillna(0)
    temporal_pivot.to_csv('data/study_deployment_timeline.csv')
    print(f"   [OK] Saved timeline from {int(df_with_year['open_year'].min())} to {int(df_with_year['open_year'].max())}")
    
    # 8. NEVI TEMPLATE (for manual data entry)
    print("\n7. Creating NEVI awards template...")
    nevi_template = pd.DataFrame({
        'state': ['CA', 'CA', 'TX', 'TX', 'MS', 'MS'],
        'station_name': ['[Enter station name from NEVI report]'] * 6,
        'city': ['[City]'] * 6,
        'nevi_award_date': ['2023-06-15', '2023-07-20', '2023-08-01', '2023-09-15', '2023-10-01', '2023-11-10'],
        'expected_completion': ['2024-12-31', '2025-01-31', '2025-02-28', '2025-03-31', '2025-06-30', '2025-08-31'],
        'nevi_round': ['Round 1'] * 6,
        'funding_amount': [0] * 6,
        'actual_open_date': [''] * 6,
        'status': ['Planned', 'Planned', 'In Construction', 'Planned', 'Planned', 'Planned'],
        'data_source': ['[State NEVI quarterly report]'] * 6,
        'notes': [''] * 6
    })
    nevi_template.to_csv('data/nevi_awards_template.csv', index=False)
    print(f"   [OK] Template created with {len(nevi_template)} example rows")
    
    print("\n" + "="*60)
    print("[SUCCESS] ALL EXPORTS COMPLETE!")
    print("="*60)
    print("\nFiles created in data/ folder:")
    print("  1. study_export_dcfc_only.csv        - DCFC stations only")
    print("  2. study_export_three_states.csv     - CA, TX, MS only")
    print("  3. study_export_full.csv             - All stations, study columns")
    print("  4. study_state_summary.csv           - Summary statistics by state")
    print("  5. study_network_summary.csv         - Top 20 network operators")
    print("  6. study_deployment_timeline.csv     - Stations by year")
    print("  7. nevi_awards_template.csv          - Template for NEVI data entry")
    
    return df

if __name__ == "__main__":
    export_study_datasets()
