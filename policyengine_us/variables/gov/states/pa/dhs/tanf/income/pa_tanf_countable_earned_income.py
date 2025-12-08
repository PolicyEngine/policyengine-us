from policyengine_us.model_api import *


class pa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "http://services.dpw.state.pa.us/oimpolicymanuals/cash/160_Income_Deductions/160_2_TANF_Earned_Income_Deductions.htm",
        "https://www.law.cornell.edu/regulations/pennsylvania/55-Pa-Code-SS-183-94",
    )
    adds = ["pa_tanf_earned_income_after_deductions_person"]
