from policyengine_us.model_api import *


class il_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Illinois Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=30358"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("il_tanf_income_eligible", period)
        non_financial_eligible = spm_unit(
            "il_tanf_non_financial_eligible", period
        )
        return income_eligible & non_financial_eligible
