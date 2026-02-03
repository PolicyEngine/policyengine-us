from policyengine_us.model_api import *


class ny_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.tanf
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        need_standard = spm_unit("ny_tanf_need_standard", period)
        return gross_income <= need_standard * p.gross_income_test.rate
