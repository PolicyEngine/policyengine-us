from policyengine_us.model_api import *


class ny_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF income eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf#page=3",
        "https://otda.ny.gov/policy/directives/2022/ADM/22-ADM-11.pdf#page=2",
    )

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
