# 📍 Where to Find NEVI Awards Data

## Official Primary Sources

### 1. Joint Office of Energy and Transportation (PRIMARY SOURCE)
**URL:** https://driveelectric.gov/

**What to look for:**
- State NEVI Deployment Plans
- Quarterly Progress Reports
- Award announcements

**Navigation:**
1. Go to https://driveelectric.gov/
2. Click "State Resources" or "NEVI Formula Program"
3. Select your state (CA, TX, MS)
4. Download quarterly reports

**File types:** PDF reports, Excel spreadsheets

---

### 2. State-Specific NEVI Pages

#### California
- **Primary:** https://calsta.ca.gov/subject-areas/climate-action/nevi
- **Caltrans:** https://dot.ca.gov/programs/traffic-operations/ep/zero-emission-vehicles
- **CEC:** https://www.energy.ca.gov/programs-and-topics/programs/clean-transportation-program
- **What to look for:** 
  - Round 1, Round 2 award lists
  - Station locations
  - Timeline documents

#### Texas
- **Primary:** https://www.txdot.gov/projects/electrification.html
- **TxDOT NEVI:** Search for "Texas NEVI plan" on TxDOT website
- **What to look for:**
  - Corridor deployment plans
  - RFP award announcements
  - Construction status updates

#### Mississippi
- **Primary:** https://www.mdot.ms.gov/
- Search: "NEVI" or "Electric Vehicle Infrastructure"
- **What to look for:**
  - State plan document (submitted 2022-2023)
  - Award announcements
  - Implementation timeline

---

### 3. Federal Highway Administration (FHWA)
**URL:** https://highways.dot.gov/newsroom/president-biden-usdot-announce-5-billion-over-five-years-national-ev-charging

**Documents:**
- National progress reports
- State-by-state funding allocations
- Policy guidance

---

### 4. Alternative Fuels Data Center (What you already have)
**URL:** https://afdc.energy.gov/
**API:** https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/

**What it provides:**
- Operational status of stations
- Open dates (when stations go live)
- Location data

**What it DOESN'T provide:**
- Award dates
- Funding amounts
- NEVI-specific tags (yet)

---

## 🔍 How to Match NEVI Data to Your AFDC Dataset

### Step 1: Download State NEVI Reports
From driveelectric.gov or state DOT websites, get:
- Station name
- City/location
- Award date
- Expected completion date
- Funding amount (optional)

### Step 2: Use the Template I Created
Open: `data/nevi_awards_template.csv`

Fill in with real data from state reports:
```csv
state,station_name,city,nevi_award_date,expected_completion,nevi_round,funding_amount,actual_open_date,status,data_source,notes
CA,Tesla Supercharger - Bakersfield,Bakersfield,2023-06-15,2024-12-31,Round 1,500000,,Planned,CA Caltrans Q2 2023 Report,I-5 corridor site
```

### Step 3: Match to AFDC Data
Use fuzzy matching in Python:
```python
import pandas as pd
from fuzzywuzzy import fuzz

afdc = pd.read_csv('data/study_export_three_states.csv')
nevi = pd.read_csv('data/nevi_awards_template.csv')

# Match by state + city + similar station names
for idx, nevi_row in nevi.iterrows():
    potential_matches = afdc[
        (afdc['state'] == nevi_row['state']) &
        (afdc['city'] == nevi_row['city'])
    ]
    
    for _, afdc_row in potential_matches.iterrows():
        similarity = fuzz.ratio(
            nevi_row['station_name'].lower(),
            afdc_row['station_name'].lower()
        )
        if similarity > 80:  # 80% match
            print(f"MATCH: {nevi_row['station_name']} <-> {afdc_row['station_name']}")
```

### Step 4: Calculate Lag
```python
nevi['actual_open_date'] = pd.to_datetime(nevi['actual_open_date'])
nevi['nevi_award_date'] = pd.to_datetime(nevi['nevi_award_date'])
nevi['lag_months'] = (
    (nevi['actual_open_date'] - nevi['nevi_award_date']).dt.days / 30
).round(1)
```

---

## 📊 Example Data You're Looking For

### From California Quarterly Report (Example):
```
Station: ChargePoint - Sacramento I-80 Rest Area
Location: Sacramento, CA
Award Date: June 15, 2023
Expected Completion: December 31, 2024
Award Amount: $485,000
Status as of Q4 2024: "Construction underway, interconnection pending"
```

### What You Record:
```csv
state,station_name,city,nevi_award_date,expected_completion,status,data_source
CA,ChargePoint - Sacramento I-80 Rest Area,Sacramento,2023-06-15,2024-12-31,In Construction,CA Caltrans Q4 2024 Report
```

---

## 🎯 Realistic Expectations for NEVI Data

### ✅ What You CAN Find:
- Award announcements (2023-2024)
- Planned locations
- Expected completion dates
- Current status (planned, construction, operational)

### ⚠️ What's HARD to Find:
- Exact operational dates for brand-new stations
- Detailed bottleneck breakdowns (permit vs interconnection)
- Real-time construction status

### 💡 Solution for Your Paper:
**If NEVI operational data is sparse:**
1. **Report what's available:** "As of March 2026, X of Y NEVI Round 1 awards are operational"
2. **Use expected dates:** Compare award dates to expected completion (shows planned timeline)
3. **Cite data limitation:** "Many 2023-2024 awards remain in deployment, limiting sample size for lag analysis"
4. **Use general timelines:** "Based on industry reports, median DCFC deployment takes 12-18 months"

---

## 📝 Suggested Data Collection Workflow

### Week 1: Initial Search (2-3 hours)
1. Visit driveelectric.gov
2. Download CA, TX, MS quarterly reports
3. Skim for "award" or "completion" tables
4. Record 10-15 stations per state in template

### Week 2: Verification (1-2 hours)
1. Cross-reference with AFDC database
2. Check if any NEVI-awarded stations are now "Available" in AFDC
3. Calculate lag for operational ones

### Week 3: Analysis (1 hour)
1. Calculate median lag
2. Compare by state
3. Report % still pending vs operational

---

## 💡 Alternative: Use Aggregate Data

If station-level matching is too time-consuming, you can use **aggregate reporting**:

**From state reports:**
- "California awarded 150 NEVI sites in Round 1 (2023)"
- "As of Q4 2024, 42 are operational (28%)"
- "Median timeline from award to operation: 14 months"

**From your AFDC data:**
- "California has 2,767 DCFC stations total (March 2026)"
- "80% opened 2020-2026 (post-IRA acceleration)"

**Combined insight:**
"While NEVI-funded stations represent [X%] of recent CA deployment, operational lag data remains limited due to reporting timelines."

---

## ✅ Final Recommendation for Your Paper

**Include in Methodology (Section 4.1):**
```
NEVI award data was collected from quarterly progress reports published 
by state transportation departments and the Joint Office of Energy and 
Transportation (driveelectric.gov). Due to limited reporting on 
post-award timelines as of March 2026, the quantitative lag analysis 
is constrained to [n=XX] stations across California, Texas, and 
Mississippi with documented award and operational dates.
```

**Include in Limitations (Section 4.3):**
```
As many NEVI awards were granted in 2023-2024, a substantial portion 
remain in pre-operational phases (permitting, construction, 
interconnection). This right-censored data limits the sample size for 
operational lag analysis, necessitating supplementation with industry 
timeline estimates from RMI (2022) and NREL (2023) reports.
```

---

## 🚀 Next Steps

1. **Visit driveelectric.gov now**
2. **Download 2-3 state reports**
3. **Fill in `nevi_awards_template.csv` with real data**
4. **Come back if you need help matching or analyzing**

Let me know once you have some data and I'll help you merge it with the AFDC dataset!
