from policyengine_us.model_api import *


class dc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "DC TANF income eligible"
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "dc_tanf_countable_earned_income",
                "dc_tanf_countable_gross_unearned_income",
            ],
        )
        need_standard = spm_unit("dc_tanf_need_standard", period)
        return income <= need_standard
