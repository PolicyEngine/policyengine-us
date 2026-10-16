from policyengine_us.model_api import *


class ia_ssa_ihhrc_monthly_cost(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved monthly in-home health-related care cost"
    definition_period = MONTH
    unit = USD
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    documentation = "Cost of the approved full-month service plan per recipient; care costing above the monthly ceiling is ineligible rather than capped."
