from policyengine_us.model_api import *


class medicaid_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid premium"
    unit = USD
    documentation = (
        "Annual household-paid Medicaid premium or premium-like contribution "
        "(e.g. Indiana HIP POWER Account, Michigan Healthy Michigan Plan "
        "contributions, Montana HELP premiums). Zero by default; state-level "
        "variables add their contributions. Michigan Healthy Michigan "
        "contributions were eliminated 2024-01-01 and Montana HELP premiums "
        "were eliminated 2023-01-01; Indiana HIP POWER Account contributions "
        "have been paused since 2020-03-01. Schedules are still encoded for "
        "reform analysis."
    )
    definition_period = YEAR
    reference = "https://www.medicaid.gov/medicaid/section-1115-demonstrations/"
    adds = ["in_hip_power_account_contribution"]
