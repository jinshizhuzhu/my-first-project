import requests
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================
# Women's Unpaid Domestic Labor Analysis
# Source: World Bank
# =====================================

# 1. Create folders

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# 2. Countries

countries = "CAN;USA;JPN;DEU;FRA"

# 3. World Bank indicators

indicators = {
    "Female": "SG.TIM.UWRK.FE",
    "Male": "SG.TIM.UWRK.MA"
}

# 4. Download online data

records = []

for gender, indicator in indicators.items():

    url = (
        f"https://api.worldbank.org/v2/country/"
        f"{countries}/indicator/{indicator}"
        f"?format=json&per_page=20000"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Unexpected World Bank API response")

    if not isinstance(data[1], list):
        raise ValueError("No valid data returned")

    for item in data[1]:

        if item["value"] is not None:

            records.append({
                "Country": item["country"]["value"],
                "Year": int(item["date"]),
                "Gender": gender,
                "Percentage": float(item["value"])
            })

# 5. Create dataframe

df = pd.DataFrame(records)

if df.empty:
    raise ValueError("No domestic labor data available")

# 6. Convert percentage into hours

df["Hours_per_Day"] = df["Percentage"] / 100 * 24

# 7. Save original observations

df.to_csv(
    DATA_DIR / "domestic_labor_raw.csv",
    index=False
)

# 8. Match female and male observations
# Only compare observations from the same country and year

comparison = df.pivot_table(
    index=["Country", "Year"],
    columns="Gender",
    values="Hours_per_Day",
    aggfunc="mean"
).dropna(subset=["Female", "Male"])

comparison = comparison.reset_index()

# 9. Calculate gender gap

comparison["Gender_Gap"] = (
    comparison["Female"] - comparison["Male"]
)

# 10. Select latest matched year

latest = (
    comparison.sort_values("Year")
    .groupby("Country")
    .tail(1)
    .sort_values("Country")
)

if latest.empty:
    raise ValueError("No matching male and female observations")

print("\n=== Unpaid Domestic Labor ===")
print(latest.to_string(index=False))

# 11. Save results

latest.to_csv(
    RESULTS_DIR / "domestic_labor_comparison.csv",
    index=False
)

# 12. Visualization

ax = latest.plot(
    x="Country",
    y=["Female", "Male"],
    kind="bar",
    figsize=(11, 6)
)

plt.title("Unpaid Domestic and Care Work by Gender")
plt.xlabel("Country")
plt.ylabel("Hours per Day")
plt.xticks(rotation=20)
plt.legend(title="Gender")

# Add observation years beneath chart

for i, year in enumerate(latest["Year"]):
    ax.text(
        i,
        -0.4,
        str(year),
        ha="center",
        fontsize=9
    )

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "domestic_labor_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nAnalysis completed!")
print("CSV and chart saved in the results folder.")