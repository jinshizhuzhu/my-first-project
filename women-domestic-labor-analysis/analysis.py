import requests
import pandas as pd
import matplotlib.pyplot as plt

# ======================================
# Women's Employment Data Analysis
# Data Source: World Bank API
# ======================================

# Step 1: Connect to World Bank API

url = (
    "https://api.worldbank.org/v2/country/"
    "CAN;USA;JPN;DEU;FRA/indicator/"
    "SL.TLF.CACT.FE.ZS?format=json&per_page=1000"
)

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

# Step 2: Extract data

records = []

for item in data[1]:

    if item["value"] is not None:

        records.append({
            "Country": item["country"]["value"],
            "Year": int(item["date"]),
            "Female_Labor_Participation": item["value"]
        })

# Step 3: Create DataFrame

df = pd.DataFrame(records)

print("\n=== Women's Employment Data ===")
print(df.head(10))

# Step 4: Select latest available year for each country

df = df.sort_values("Year")

latest = df.groupby("Country").tail(1)

print("\n=== Latest Available Data ===")
print(latest)

# Step 5: Create visualization

plt.figure(figsize=(10, 6))

plt.bar(
    latest["Country"],
    latest["Female_Labor_Participation"]
)

plt.title("Female Labor Force Participation by Country")
plt.xlabel("Country")
plt.ylabel("Participation Rate (%)")

plt.xticks(rotation=20)

plt.tight_layout()

# Step 6: Save chart

plt.savefig("women_employment.png")

print("\nChart saved successfully!")

plt.show()