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
        "including assigned_aca_ptc for ACA premium tax credits."
    )
    adds = [
        "medicaid_cost",
        "msp_cost",
        "per_capita_chip",
        "assigned_aca_ptc",
        "co_omnisalud",
        "or_healthier_oregon_cost",
    ]
