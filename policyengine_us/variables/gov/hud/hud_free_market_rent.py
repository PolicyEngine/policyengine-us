#free_market_rent.py

from policyengine_us.model_api import * # change to policyengine_us for US-specific functions
import pandas as pd

# Load HUD data for FMR values (Update the path to the CSV file as needed)
hud_data = pd.read_csv("path_to/FMR_data.csv")

class FMR_0_bedroom(Variable):
    label = "Free Market Rent for 0 Bedroom"
    definition_period = YEAR
    entity = Household
    value_type = float
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"
    defined_for = None
    documentation = "Free market rent for 0-bedroom housing units, based on HUD data and FIPS code."

    def formula(household, period, parameters):
        fips_code = household("fips_code", period)
        fmr = hud_data.loc[hud_data["FIPS"] == fips_code, "FMR_0"].values[0]
        return fmr

class FMR_1_bedroom(Variable):
    label = "Free Market Rent for 1 Bedroom"
    definition_period = YEAR
    entity = Household
    value_type = float
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"
    defined_for = None
    documentation = "Free market rent for 1-bedroom housing units, based on HUD data and FIPS code."

    def formula(household, period, parameters):
        fips_code = household("fips_code", period)
        fmr = hud_data.loc[hud_data["FIPS"] == fips_code, "FMR_1"].values[0]
        return fmr

class FMR_2_bedroom(Variable):
    label = "Free Market Rent for 2 Bedroom"
    definition_period = YEAR
    entity = Household
    value_type = float
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"
    defined_for = None
    documentation = "Free market rent for 2-bedroom housing units, based on HUD data and FIPS code."

    def formula(household, period, parameters):
        fips_code = household("fips_code", period)
        fmr = hud_data.loc[hud_data["FIPS"] == fips_code, "FMR_2"].values[0]
        return fmr

class FMR_3_bedroom(Variable):
    label = "Free Market Rent for 3 Bedroom"
    definition_period = YEAR
    entity = Household
    value_type = float
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"
    defined_for = None
    documentation = "Free market rent for 3-bedroom housing units, based on HUD data and FIPS code."

    def formula(household, period, parameters):
        fips_code = household("fips_code", period)
        fmr = hud_data.loc[hud_data["FIPS"] == fips_code, "FMR_3"].values[0]
        return fmr

class FMR_4_bedroom(Variable):
    label = "Free Market Rent for 4 Bedroom"
    definition_period = YEAR
    entity = Household
    value_type = float
    reference = "https://www.huduser.gov/portal/datasets/fmr.html"
    defined_for = None
    documentation = "Free market rent for 4-bedroom housing units, based on HUD data and FIPS code."

    def formula(household, period, parameters):
        fips_code = household("fips_code", period)
        fmr = hud_data.loc[hud_data["FIPS"] == fips_code, "FMR_4"].values[0]
        return fmr
