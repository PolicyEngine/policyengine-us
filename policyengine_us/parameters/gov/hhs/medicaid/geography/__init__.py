from pathlib import Path

import pandas as pd

FOLDER = Path(__file__).parent

medicaid_rating_areas = pd.read_csv(FOLDER / "medicaid_rating_areas.csv")
second_lowest_silver_plan_cost = pd.read_csv(
    FOLDER / "second_lowest_silver_plan_cost.csv"
)
aca_rating_areas = pd.read_csv(FOLDER / "aca_rating_areas.csv")
