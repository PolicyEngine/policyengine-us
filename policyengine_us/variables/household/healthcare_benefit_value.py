from policyengine_us.model_api import *


class healthcare_benefit_value(Variable):
    value_type = float
    label = "Cash equivalent of health coverage"
    entity = Household
    definition_period = YEAR
    unit = USD
    documentation = (
        "Annual household health coverage value. CHIP is counted through "
        "`chip`, which is gated on eligibility, take-up, and enrollment."
    )
    adds = [
        "medicaid_cost",
        "msp_cost",
        "chip",
        "assigned_aca_ptc",
        "basic_health_program",
        "co_omnisalud",
        "or_healthier_oregon_cost",
    ]
