from policyengine_us.model_api import *


class healthcare_benefit_value(Variable):
    value_type = float
    label = "Cash equivalent of health coverage"
    entity = Household
    definition_period = YEAR
    unit = USD
    documentation = (
        "Annual canonical household resource value of health coverage. This "
        "uses annual health-value and government-cost proxy variables directly, "
        "including assigned_aca_ptc for ACA premium tax credits. CHIP is counted "
        "through `chip`, which is gated on eligibility, take-up, and enrollment."
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
