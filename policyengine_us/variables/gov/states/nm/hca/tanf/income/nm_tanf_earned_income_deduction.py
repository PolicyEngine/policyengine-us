from policyengine_us.model_api import *


class nm_tanf_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico TANF earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    adds = ["nm_tanf_earned_income_deduction_person"]
