import pandas as pd
import plotly.express as px

# Read the data
data = []
with open("calc_snap.py.out", "r") as f:
    next(f)  # Skip header
    for line in f:
        parts = line.strip().split(",")
        if len(parts) == 2:
            state = parts[0]
            value_part = parts[1]
            if value_part.startswith("$"):
                try:
                    value = float(value_part.replace("$", ""))
                    data.append({"State": state, "SNAP": value})
                except:
                    continue
            else:
                continue

# Create dataframe
df = pd.DataFrame(data)

# Create a US choropleth map with Plotly
fig = px.choropleth(
    df,
    locations="State",
    locationmode="USA-states",
    color="SNAP",
    scope="usa",
    color_continuous_scale="Viridis",
    labels={"SNAP": "SNAP Benefit ($)"},
    title="SNAP Benefit for Single Person with $10,000 Employment Income (2025)"
)

# Format y-axis to show dollar values
fig.update_layout(
    coloraxis_colorbar=dict(
        title="Annual SNAP Benefit",
        tickprefix="$",
        tickformat=",d"
    )
)

# Save as HTML
fig.write_html("snap_map.html")

print("Map created and saved as snap_map.html")

# Print the data in descending order for reference
sorted_df = df.sort_values("SNAP", ascending=False)
print("\nSNAP Benefits by State (Highest to Lowest):")
for _, row in sorted_df.iterrows():
    print(f"{row['State']}: ${row['SNAP']:.2f}")
