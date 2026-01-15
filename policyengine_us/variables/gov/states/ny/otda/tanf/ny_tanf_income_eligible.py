from policyengine_us.model_api import *


class ny_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF income eligible"
    definition_period = MONTH
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        # Gross income test (only applies pre-Oct 2022)
        gross_income_eligible = spm_unit(
            "ny_tanf_gross_income_eligible", period
        )

        # Needs test (always applies)
        income = add(
            spm_unit,
            period,
            [
                "ny_tanf_countable_earned_income",
                "ny_tanf_countable_gross_unearned_income",
            ],
        )
        need_standard = spm_unit("ny_tanf_need_standard", period)
        needs_test_eligible = income < need_standard

        return gross_income_eligible & needs_test_eligible
