#  Chicago Crime Data — Exploratory Data Analysis (EDA)

> A complete beginner-friendly EDA project using real-world crime data from the City of Chicago.

---

##  Project Overview

This project performs end-to-end Exploratory Data Analysis on the **Chicago Crimes Dataset** — one of the most comprehensive public crime datasets in the US. The goal is to uncover patterns in crime types, timing, location, and arrest rates using Python.

**Domain:** Public Safety / Criminology  
**Tools:** Python · Pandas · Matplotlib · Seaborn  
**Dataset:** [Chicago Data Portal](https://data.cityofchicago.org/resource/ijzp-q8t2.csv)

---

##  Objectives

1. Identify the **most frequent crime types** in Chicago.
2. Discover **when** crimes peak (hour, day, month, year).
3. Find **where** crimes occur most (location, community area, map).
4. Understand the **arrest rate** across different crime types.
5. Explore **domestic vs non-domestic** crime patterns.

---

##  Project Structure

```
chicago-crime-eda/
|
├── crime_eda.py            ← Main EDA script (all analysis + plots)
├── chicago_crimes.csv      ← Downloaded dataset (auto-generated on first run)
├── plots/                  ← All saved chart images
│   ├── 6A_top10_crime_types.png
│   ├── 6B_arrest_rate.png
│   ├── 6C_crimes_by_hour.png
│   ├── 7A_arrest_rate_by_crime.png
│   ├── 7B_crimes_by_weekday.png
│   ├── 7C_domestic_vs_nondomestic.png
│   ├── 8A_yearly_crime_trend.png
│   ├── 8B_year_month_heatmap.png
│   ├── 8C_tod_by_crime_type.png
│   ├── 9A_top10_locations.png
│   ├── 9B_geographic_crime_map.png
│   └── 9C_community_areas.png
├── requirements.txt        ← Python dependencies
└── README.md               ← This file
```

---

##  Dataset Description

| Field | Description |
|---|---|
| `date` | Date and time the crime occurred |
| `primary_type` | Main category of crime (THEFT, BATTERY, etc.) |
| `description` | More specific sub-type of the crime |
| `location_description` | Where it happened (STREET, RESIDENCE, etc.) |
| `arrest` | Whether an arrest was made (True/False) |
| `domestic` | Whether it was domestic-related |
| `district` | Chicago Police district number |
| `community_area` | Chicago community area (1–77) |
| `latitude` / `longitude` | Geographic coordinates |

 Dataset is not uploaded due to size. It is automatically downloaded when running the script.

**Source:** [City of Chicago — Open Data Portal](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2)

---

##  EDA Steps Performed

| Step | Description |
|------|-------------|
| **1. Import Libraries** | Pandas, NumPy, Matplotlib, Seaborn |
| **2. Load Data** | Download 80,000 rows via Socrata API |
| **3. Understand Data** | Shape, dtypes, nulls, basic stats |
| **4. Data Cleaning** | Drop nulls, fix dtypes, remove duplicates |
| **5. Feature Engineering** | Extract hour, day, month; bucket time-of-day |
| **6. Univariate Analysis** | Crime types, arrest rate, hour distribution |
| **7. Bivariate Analysis** | Arrest by crime, weekday counts, domestic split |
| **8. Time Trends** | Yearly trend, year × month heatmap, time-of-day |
| **9. Geo/Categorical** | Location types, scatter map, community areas |
| **10. Insights** | Summary of all key findings |

---

##  Key Visualisations

| Plot | What it shows |
|------|--------------|
| Top 10 Crime Types | Which crimes happen most |
| Arrest Rate Donut | % of crimes that led to arrest |
| Crimes by Hour | When crimes peak during the day |
| Arrest Rate by Crime | Which crimes are more/less solved |
| Crimes by Weekday | Busiest days of the week |
| Domestic Split | Domestic vs non-domestic by crime type |
| Yearly Trend | How total crime changed year by year |
| Year × Month Heatmap | Seasonal patterns across all years |
| Time-of-Day Breakdown | Which crimes happen in which part of the day |
| Top 10 Locations | Where crimes happen most |
| Geographic Scatter Map | Spatial distribution across Chicago |
| Community Area Bar Chart | Highest-crime neighbourhoods |

---

##  Key Findings

-  **Theft** is the most common crime type in Chicago.
-  **Streets and residences** are the top crime locations.
-  Crime peaks in the **afternoon and evening (12 PM – 10 PM)**.
-  **Fridays and Saturdays** see the highest weekly crime counts.
-  **Summer months** (June–August) consistently show more crime.
-  The overall arrest rate is **below 25%** — most crimes go unarrested.
-  **Narcotics and weapons violations** have the highest arrest rates.
-  Crime is geographically **clustered** in specific south-side community areas.

---

##  How to Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Crime_eda
cd Crime_eda

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the analysis (auto-downloads the dataset)
python crime_eda.py

# 4. View all charts in the /plots folder
```

---

## 📦 Requirements

```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
```

Install with:
```bash
pip install pandas numpy matplotlib seaborn
```

---

##  Real-World Impact

- **City planners** can use peak-hour data to schedule police patrols.
- **Residents** can identify safer times and locations.
- **Policy makers** can target low arrest-rate crime types for reform.
- **Community organisations** can focus outreach in high-crime area.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).  
Dataset is publicly available via the City of Chicago Open Data Portal.
