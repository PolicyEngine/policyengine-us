from policyengine_us.model_api import *


class nv_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/TANF/TANF_State_Plan_FINAL%20_Effective_12.31.20.pdf#page=17"
    defined_for = StateCode.NV
    # Sum person-level countable earned income.
    # The work expense deduction ($90 or 20%, whichever is greater)
    # is applied per person, then summed to the household.
    adds = ["nv_tanf_earned_income_after_disregard"]
