from policyengine_us.model_api import *


class household_benefits(Variable):
    value_type = float
    entity = Household
    label = "benefits"
    unit = USD
    definition_period = YEAR
    adds = [
        "social_security",
        "ssi",
        "ca_cvrp",  # California Clean Vehicle Rebate Project.
        "snap",
        "wic",
        "free_school_meals",
        "reduced_price_school_meals",
        "lifeline",
        "acp",
        "ebb",
        "tanf",
        "high_efficiency_electric_home_rebate",
        "residential_efficiency_electrification_rebate",
        # Contributed.
        "basic_income",
        "spm_unit_capped_housing_subsidy",
    ]
