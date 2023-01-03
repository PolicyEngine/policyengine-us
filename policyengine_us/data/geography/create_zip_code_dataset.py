import pandas as pd

# Per-ZCTA population dataset
# ACS 5-year estimates, download URL: https://data.census.gov/cedsci/table?q=DP05%3A%20ACS%20DEMOGRAPHIC%20AND%20HOUSING%20ESTIMATES&g=0100000US%248600000&tid=ACSDP5Y2020.DP05

zcta = pd.read_csv(
    "zcta_2020_population.csv",
    low_memory=False,
    usecols=["DP05_0001E", "NAME"],
    skiprows=1,
    header=0,
    names=["population", "zcta"],
)
zcta.zcta = zcta.zcta.apply(lambda x: x.split(" ")[1])
zcta.zcta = zcta.zcta.astype(int)
zcta.population = zcta.population.astype(int)

# ZCTA-county dataset
# 2020 ZCTA to County Relationship File, download URL: https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html#zcta
zcta_to_county = pd.read_csv(
    "zcta_2020_to_county_2020.csv",
    delimiter="|",
    usecols=["GEOID_ZCTA5_20", "NAMELSAD_COUNTY_20"],
    names=["zcta", "county"],
)
zcta_to_county = zcta_to_county.dropna()
zcta_to_county.zcta = zcta_to_county.zcta.astype(int)
# Some ZCTAs have more than one county - select a random one
zcta_to_county = zcta_to_county.groupby("zcta").apply(lambda x: x.sample(1))

# ZIP code-ZCTA dataset
# Download URL: https://udsmapper.org/zip-code-to-zcta-crosswalk/
zip_code = pd.read_csv(
    "zip_code_to_zcta.csv",
    usecols=["ZIP_CODE", "ZCTA", "STATE"],
    names=["zip_code", "zcta", "state"],
)
zip_code.zip_code = zip_code.zip_code.astype(int)
zip_code = zip_code[zip_code.zcta != "No ZCTA"]
zip_code.zcta = zip_code.zcta.astype(int)
zip_code = zip_code[zip_code.zcta.isin(zcta.zcta)]
zip_code = zip_code[zip_code.zcta.isin(zcta_to_county.zcta)]

# ZCTAs have multiple ZIP codes - split each ZCTA population equally into its component ZIP codes
zip_code["population"] = (
    zcta.set_index("zcta").population[zip_code.zcta].values
    / zip_code.groupby("zcta").zip_code.count()[zip_code.zcta].values
)
zip_code["county"] = (
    zcta_to_county.set_index("zcta").county[zip_code.zcta].values
)
zip_code.to_csv("zip_codes.csv", compression="gzip")
