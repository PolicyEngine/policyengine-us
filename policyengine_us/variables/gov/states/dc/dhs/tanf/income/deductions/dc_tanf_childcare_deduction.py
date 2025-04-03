from policyengine_us.model_api import *


class dc_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) child care deduction "
    unit = USD
    definition_period = MONTH
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"  # (A)(2)
    defined_for = StateCode.DC

    adds = ["dc_tanf_childcare_deduction_person"]
