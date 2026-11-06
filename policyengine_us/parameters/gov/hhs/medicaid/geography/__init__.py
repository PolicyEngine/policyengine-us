import pandas as pd
from pathlib import Path

FOLDER = Path(__file__).parent

medicaid_rating_areas = pd.read_csv(FOLDER / "medicaid_rating_areas.csv")
second_lowest_silver_plan_cost = pd.read_csv(
    FOLDER / "second_lowest_silver_plan_cost.csv"
)
aca_rating_areas = pd.read_csv(FOLDER / "aca_rating_areas.csv")
# Counties whose ACA rating area differs from aca_rating_areas.csv from start_year on,
# from CMS's state geographic rating area pages.
aca_rating_area_corrections = pd.read_csv(
    FOLDER / "aca_rating_area_corrections.csv",
    usecols=["county", "rating_area", "start_year"],
)
