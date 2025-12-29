from policyengine_us.model_api import *


class hi_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf",
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=20",
    )
    defined_for = StateCode.HI

    adds = ["hi_tanf_countable_earned_income_person"]
