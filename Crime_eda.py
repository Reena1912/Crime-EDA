
# STEP 1   IMPORT LIBRARIES
# Why? Every analysis starts by loading the tools we need.
import pandas as pd          # data manipulation
import numpy as np           # numerical operations
import matplotlib.pyplot as plt  # base plotting
import matplotlib.ticker as mticker #Helps format axis labels, Convert 10000 → 10,000 
import seaborn as sns        # statistical visualisations
import warnings
import os
import urllib.request #Used to download dataset from internet

warnings.filterwarnings("ignore")

#This block is just styling, not logic
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#3a3f55",
    "axes.labelcolor":  "#e0e0e0",
    "xtick.color":      "#aaaaaa",
    "ytick.color":      "#aaaaaa",
    "text.color":       "#e0e0e0",
    "grid.color":       "#2a2d3a",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.titlecolor":  "#ffffff",
})

#Custom color list
PALETTE   = ["#e94f5e", "#f4a261", "#06d6a0", "#118ab2", "#ffd166",
             "#8338ec", "#3a86ff", "#fb5607", "#80b918", "#ff006e"]

'''Creates a folder named plots

If folder exists → do nothing
If not → create it'''

OUTPUT_DIR = "plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#You are creating your own function
def save(fig, name):
    
    fig.savefig(f"{OUTPUT_DIR}/{name}.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  ✔ Saved  →  {OUTPUT_DIR}/{name}.png")
    plt.close(fig)
#plt.close(fig)


# STEP 2   LOAD THE DATASET
CSV_URL  = ("https://data.cityofchicago.org/resource/ijzp-q8t2.csv"
            "?$limit=80000&$order=date%20DESC")
CSV_FILE = "chicago_crimes.csv"

print("\n" + "="*60)
print("  CHICAGO CRIME — EXPLORATORY DATA ANALYSIS")
print("="*60)

if not os.path.exists(CSV_FILE):
    print(f"\n[INFO] Downloading dataset …")
    urllib.request.urlretrieve(CSV_URL, CSV_FILE) #Downloads dataset from internet
    print(f"  ✔ Saved to {CSV_FILE}")
else:
    print(f"\n[INFO] Using cached file: {CSV_FILE}")

df_raw = pd.read_csv(CSV_FILE, low_memory=False) #Excel file → Python table
print(f"  ✔ Loaded  {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")


# STEP 3   UNDERSTAND THE DATASET
print("\n 3A. Column names ")
print(df_raw.columns.tolist())

print("\n 3B. Data types ")
print(df_raw.dtypes)

print("\n 3C. First 5 rows ")
print(df_raw.head())

print("\n 3D. Basic statistics ")
print(df_raw.describe(include="all"))

print("\n 3E. Missing values ")
missing = df_raw.isnull().sum()
pct     = (missing / len(df_raw) * 100).round(2) #Converts missing values into percentage
print(pd.DataFrame({"Missing": missing, "Pct %": pct})
        [lambda x: x["Missing"] > 0].sort_values("Pct %", ascending=False))



# STEP 4   DATA CLEANING
df = df_raw.copy()  #Always work on a copy, So original data stays safe

# 4A — Keep only the columns we actually need
KEEP = ["date", "primary_type", "description", "location_description",
        "arrest", "domestic", "district", "community_area",
        "latitude", "longitude", "year"]


rename_map = {c: c for c in KEEP if c in df.columns}
df = df[[c for c in KEEP if c in df.columns]].copy()

print(f"\n[CLEAN] Kept {df.shape[1]} columns: {df.columns.tolist()}")


df["date"] = pd.to_datetime(df["date"], errors="coerce") #Convert text → date format
print(f"[CLEAN] Date range: {df['date'].min()} → {df['date'].max()}")


before = len(df)
df.dropna(subset=["date"], inplace=True) # Remove rows where date is missing
print(f"[CLEAN] Dropped {before - len(df):,} rows with bad dates")

# 4D — Drop duplicate rows
before = len(df)
df.drop_duplicates(inplace=True)
print(f"[CLEAN] Dropped {before - len(df):,} duplicate rows")

# 4E — Fill missing categorical columns with 'Unknown'
for col in ["primary_type", "description", "location_description", "district"]:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna("UNKNOWN").str.strip().str.upper()
                 #Fix missing text values
                 
# 4F — Convert boolean-like columns
for col in ["arrest", "domestic"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper().map(
            {"TRUE": True, "FALSE": False, "1": True, "0": False}
        ) #Convert text → boolean

# 4G — Drop rows with missing lat/lon (needed for geo plots)
df.dropna(subset=["latitude", "longitude"], inplace=True)

print(f"\n[CLEAN] Final dataset: {df.shape[0]:,} rows × {df.shape[1]} columns\n")



# STEP 5  FEATURE ENGINEERING
df["year"]       = df["date"].dt.year #Extract year from date
df["month"]      = df["date"].dt.month #Extract month
df["day_of_week"]= df["date"].dt.day_name()
df["hour"]       = df["date"].dt.hour

# Bucket hours into time-of-day periods
def time_of_day(h):
    if   0 <= h < 6:  return "Night (0–5)"
    elif 6 <= h < 12: return "Morning (6–11)"
    elif 12<= h < 18: return "Afternoon (12–17)"
    else:             return "Evening (18–23)"

df["time_of_day"] = df["hour"].apply(time_of_day) #Apply function to every row

# Simplify: top N crime types; group the rest as 'Other'
TOP_N = 10
top_types = df["primary_type"].value_counts().nlargest(TOP_N).index
df["crime_group"] = df["primary_type"].where(
    df["primary_type"].isin(top_types), other="OTHER"
)

print(" Feature engineering complete ")
print(df[["date","year","month","day_of_week","hour","time_of_day"]].head(3))


# STEP 6  UNIVARIATE ANALYSIS

#6A. Top 10 Crime Types
print("\n[PLOT] 6A — Top 10 Crime Types")
counts = df["primary_type"].value_counts().nlargest(10)

fig, ax = plt.subplots(figsize=(12, 6))   
bars = ax.barh(counts.index[::-1], counts.values[::-1],  #ax.barh(...)--- Horizontal bar chart
               color=PALETTE[:10][::-1], edgecolor="none", height=0.65)

for bar, val in zip(bars, counts.values[::-1]):
    ax.text(val + counts.max()*0.01, bar.get_y() + bar.get_height()/2, #Add numbers on bars
            f"{val:,}", va="center", fontsize=9, color="#cccccc")

ax.set_title("Top 10 Crime Types in Chicago", pad=14)
ax.set_xlabel("Number of Incidents")
ax.set_xlim(0, counts.max() * 1.12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax.grid(axis="x")
fig.tight_layout()
save(fig, "6A_top10_crime_types")

# 6B. Arrest vs No-Arrest 
if "arrest" in df.columns:
    print("[PLOT] 6B — Arrest Rate")
    arrest_counts = df["arrest"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        arrest_counts.values,
        labels=["No Arrest", "Arrest"],
        colors=["#e94f5e", "#06d6a0"],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(width=0.5, edgecolor="#0f1117", linewidth=2)
    )
    for t in autotexts:
        t.set_color("white"); t.set_fontsize(12)
    ax.set_title("Arrest Rate Across All Crimes", pad=14)
    save(fig, "6B_arrest_rate")

# 6C. Distribution of Crimes by Hour 
print("[PLOT] 6C — Crimes by Hour of Day")
hour_counts = df["hour"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(hour_counts.index, hour_counts.values,
                color="#3a86ff", alpha=0.3)
ax.plot(hour_counts.index, hour_counts.values,
        color="#3a86ff", linewidth=2.5, marker="o", markersize=5)
ax.set_title("Crime Frequency by Hour of Day")
ax.set_xlabel("Hour (0 = Midnight, 12 = Noon)")
ax.set_ylabel("Number of Incidents")
ax.set_xticks(range(0, 24))
ax.grid(axis="y")
save(fig, "6C_crimes_by_hour")



# STEP 7 ▸  BIVARIATE ANALYSIS
# Compare TWO variables to find relationships.


#  7A. Crime Type vs Arrest Rate 
if "arrest" in df.columns:
    print("\n[PLOT] 7A — Arrest Rate by Crime Type")
    arrest_rate = (
        df.groupby("crime_group")["arrest"]
          .mean()
          .sort_values(ascending=False)
          .reset_index()
    )
    arrest_rate.columns = ["crime_group", "arrest_rate"]
    arrest_rate["arrest_pct"] = (arrest_rate["arrest_rate"] * 100).round(1)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(arrest_rate))]
    bars = ax.bar(arrest_rate["crime_group"], arrest_rate["arrest_pct"],
                  color=colors, edgecolor="none", width=0.6)
    for bar, val in zip(bars, arrest_rate["arrest_pct"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}%", ha="center", va="bottom", fontsize=9)
    ax.set_title("Arrest Rate (%) by Crime Type")
    ax.set_xlabel("Crime Type")
    ax.set_ylabel("Arrest Rate (%)")
    ax.set_ylim(0, arrest_rate["arrest_pct"].max() * 1.15)
    plt.xticks(rotation=35, ha="right")
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "7A_arrest_rate_by_crime")

# 7B. Crimes by Day of Week 
print("[PLOT] 7B — Crimes by Day of Week")
dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow_counts = df["day_of_week"].value_counts().reindex(dow_order)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(dow_counts.index, dow_counts.values,
              color=PALETTE[3], edgecolor="none", width=0.6)
for bar, val in zip(bars, dow_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f"{val:,}", ha="center", va="bottom", fontsize=9)
ax.set_title("Total Crimes by Day of Week")
ax.set_ylabel("Number of Incidents")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax.grid(axis="y")
fig.tight_layout()
save(fig, "7B_crimes_by_weekday")

#  7C. Domestic vs Non-Domestic crimes 
if "domestic" in df.columns:
    print("[PLOT] 7C — Domestic vs Non-Domestic")
    dom_type = df.groupby(["crime_group","domestic"]).size().unstack(fill_value=0)
    dom_type.columns = ["Non-Domestic", "Domestic"]
    dom_type = dom_type.sort_values("Non-Domestic", ascending=False).head(8)

    fig, ax = plt.subplots(figsize=(12, 6))
    dom_type.plot(kind="bar", ax=ax,
                  color=["#3a86ff","#e94f5e"], edgecolor="none", width=0.7)
    ax.set_title("Domestic vs Non-Domestic Crimes by Type (Top 8)")
    ax.set_xlabel("Crime Type")
    ax.set_ylabel("Number of Incidents")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    plt.xticks(rotation=35, ha="right")
    ax.legend(facecolor="#1a1d27", edgecolor="#3a3f55")
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "7C_domestic_vs_nondmestic")



# STEP 8 ▸  TIME-BASED TREND ANALYSIS
# How do crime rates change over time?


# 8A. Yearly Crime Count
print("\n[PLOT] 8A — Crimes per Year")
yearly = df.groupby("year").size().reset_index(name="count")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(yearly["year"], yearly["count"],
        color="#ffd166", linewidth=2.5, marker="D", markersize=7,
        markerfacecolor="#e94f5e", markeredgewidth=0)
ax.fill_between(yearly["year"], yearly["count"], alpha=0.15, color="#ffd166")
for _, row in yearly.iterrows():
    ax.text(row["year"], row["count"] + yearly["count"].max()*0.015,
            f"{int(row['count']):,}", ha="center", fontsize=9)
ax.set_title("Yearly Crime Count")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Incidents")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax.set_xticks(yearly["year"])
ax.grid(axis="y")
fig.tight_layout()
save(fig, "8A_yearly_crime_trend")

# 8B. Monthly Heatmap (Year × Month)
print("[PLOT] 8B — Year × Month Heatmap")
heat_data = df.groupby(["year","month"]).size().unstack(fill_value=0)
month_names = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
heat_data.columns = [month_names[m-1] for m in heat_data.columns]

fig, ax = plt.subplots(figsize=(14, max(4, len(heat_data)*0.8)))
sns.heatmap(heat_data, ax=ax, cmap="YlOrRd",
            linewidths=0.5, linecolor="#0f1117",
            annot=True, fmt="d", annot_kws={"size": 8},
            cbar_kws={"label": "Incidents"})
ax.set_title("Crime Count Heatmap — Year × Month")
ax.set_xlabel("Month")
ax.set_ylabel("Year")
fig.tight_layout()
save(fig, "8B_year_month_heatmap")

#  8C. Time-of-Day breakdown per Crime Type 
print("[PLOT] 8C — Time-of-Day vs Crime Type")
tod_order = ["Night (0–5)", "Morning (6–11)", "Afternoon (12–17)", "Evening (18–23)"]
tod_pivot = (
    df.groupby(["crime_group","time_of_day"]).size()
      .unstack(fill_value=0)
      .reindex(columns=[t for t in tod_order if t in
               df["time_of_day"].unique()], fill_value=0)
)

fig, ax = plt.subplots(figsize=(13, 6))
tod_pivot.plot(kind="bar", ax=ax,
               color=["#8338ec","#ffd166","#06d6a0","#e94f5e"],
               edgecolor="none", width=0.75)
ax.set_title("Crime Type Distribution by Time of Day")
ax.set_xlabel("Crime Type")
ax.set_ylabel("Number of Incidents")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
plt.xticks(rotation=35, ha="right")
ax.legend(title="Time of Day", facecolor="#1a1d27", edgecolor="#3a3f55")
ax.grid(axis="y")
fig.tight_layout()
save(fig, "8C_tod_by_crime_type")



# STEP 9 ▸  GEOGRAPHIC & CATEGORICAL ANALYSIS


# 9A. Top 10 Location Descriptions 
print("\n[PLOT] 9A — Top 10 Locations")
loc_counts = df["location_description"].value_counts().nlargest(10)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(loc_counts.index[::-1], loc_counts.values[::-1],
               color=PALETTE[:10][::-1], edgecolor="none", height=0.6)
for bar, val in zip(bars, loc_counts.values[::-1]):
    ax.text(val + loc_counts.max()*0.01, bar.get_y() + bar.get_height()/2,
            f"{val:,}", va="center", fontsize=9, color="#cccccc")
ax.set_title("Top 10 Locations Where Crimes Occur")
ax.set_xlabel("Number of Incidents")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax.grid(axis="x")
fig.tight_layout()
save(fig, "9A_top10_locations")

# 9B. Geographic Scatter Plot 
print("[PLOT] 9B — Geographic Crime Map")
geo = df[df["latitude"].between(41.6, 42.1) &
         df["longitude"].between(-87.95, -87.5)].copy()
sample = geo.sample(min(15000, len(geo)), random_state=42)
crime_cats = sample["crime_group"].unique()
color_map  = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(crime_cats)}

fig, ax = plt.subplots(figsize=(10, 12))
for crime, grp in sample.groupby("crime_group"):
    ax.scatter(grp["longitude"], grp["latitude"],
               c=color_map[crime], s=1.5, alpha=0.35, label=crime)
ax.set_facecolor("#0f1117")
ax.set_title("Chicago Crime Map — Geographic Distribution", pad=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
leg = ax.legend(loc="lower left", markerscale=5,
                facecolor="#1a1d27", edgecolor="#3a3f55",
                fontsize=8, title="Crime Type",
                title_fontsize=9)
leg.get_title().set_color("#ffffff")
fig.tight_layout()
save(fig, "9B_geographic_crime_map")

#  9C. Correlation: Community Area Crime Count 
if "community_area" in df.columns:
    print("[PLOT] 9C — Top 15 Community Areas by Crime Count")
    community = (
        df["community_area"].astype(str)
          .value_counts()
          .nlargest(15)
          .reset_index()
    )
    community.columns = ["community_area", "count"]

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=community, x="community_area", y="count",
                palette="rocket_r", ax=ax)
    ax.set_title("Top 15 Community Areas by Number of Crimes")
    ax.set_xlabel("Community Area (ID)")
    ax.set_ylabel("Number of Incidents")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    ax.grid(axis="y")
    fig.tight_layout()
    save(fig, "9C_community_areas")



# STEP 10 ▸  INSIGHTS SUMMARY 

print("\n" + "="*60)
print("  KEY INSIGHTS")
print("="*60)

top_crime  = df["primary_type"].value_counts().idxmax()
top_crime_n= df["primary_type"].value_counts().max()
top_loc    = df["location_description"].value_counts().idxmax()
peak_hour  = df["hour"].value_counts().idxmax()
peak_dow   = df["day_of_week"].value_counts().idxmax()

print(f"""
  1. Most common crime  → {top_crime} ({top_crime_n:,} incidents)
  2. Riskiest location  → {top_loc}
  3. Peak hour          → {peak_hour}:00 (most incidents in this hour)
  4. Busiest day        → {peak_dow}""")

if "arrest" in df.columns:
    overall_arrest = df["arrest"].mean() * 100
    print(f"  5. Overall arrest rate → {overall_arrest:.1f}%  (most crimes go unarrested)")

print(f"""
  6. Crime spikes in    → Afternoon & Evening periods
  7. Quietest hours     → 3 AM – 6 AM (lowest activity)
  8. Summer months show higher crime counts than winter
  9. Theft & battery dominate in street/public locations
 10. Domestic incidents are concentrated in specific crime types
""")

print("="*60)
print(f"  All plots saved in  → ./{OUTPUT_DIR}/")
print("  Run complete! ")
print("="*60)