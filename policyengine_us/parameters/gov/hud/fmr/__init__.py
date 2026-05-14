import pandas as pd
from pathlib import Path

FOLDER = Path(__file__).parent

fair_market_rents = pd.read_csv(
    FOLDER / "fair_market_rents.csv",
    dtype={"county_fips": str},
)
fair_market_rents["county_fips"] = fair_market_rents["county_fips"].str.zfill(5)
