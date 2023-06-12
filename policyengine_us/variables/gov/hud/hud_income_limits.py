from policyengine_us.model_api import *
import numpy as np

class HUDIncomeLimits(Variable):
    label = "HUD Income Limits"
    definition_period = YEAR
    entity = Household
    value_type = str
    reference = "https://www.huduser.gov/portal/datasets/il.html"
    defined_for = None
    documentation = "HUD Income Limits for ELI, LI, and VLI for 1-8 member households based on FIPS code."

    def formula(household, period, parameters):
        state_fips = household("state_fips", period)
        num_members = household("household_size", period)
        income_limits = parameters(period).hud_income_limits

        # Fetching data based on FIPS code and household members
        limit_data = income_limits.loc[income_limits["fips_code"] == fips_code]

        # Use np.select to vectorize the income limit selection
        conditions = [
            (num_members == 1),
            (num_members == 2),
            (num_members == 3),
            (num_members == 4),
            (num_members == 5),
            (num_members == 6),
            (num_members == 7),
            (num_members == 8),
        ]
        income_limit_columns = [
            "hud_eli_1",
            "hud_eli_2",
            "hud_eli_3",
            "hud_eli_4",
            "hud_eli_5",
            "hud_eli_6",
            "hud_eli_7",
            "hud_eli_8",
            "hud_li_1",
            "hud_li_2",
            "hud_li_3",
            "hud_li_4",
            "hud_li_5",
            "hud_li_6",
            "hud_li_7",
            "hud_li_8",
            "hud_vli_1",
            "hud_vli_2",
            "hud_vli_3",
            "hud_vli_4",
            "hud_vli_5",
            "hud_vli_6",
            "hud_vli_7",
            "hud_vli_8",
        ]
        income_limits_vectorized = np.select(conditions, [limit_data[column] for column in income_limit_columns])

        return income_limits_vectorized