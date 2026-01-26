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
        p = parameters(period).gov.states.ny.otda.tanf

        # Needs test (always applies)
        countable_income = spm_unit("ny_tanf_countable_income", period)
        need_standard = spm_unit("ny_tanf_need_standard", period)
        needs_test_eligible = countable_income < need_standard

        # Gross income test (only applies pre-October 2022)
        gross_income_eligible = spm_unit(
            "ny_tanf_gross_income_eligible", period
        )

        return where(
            p.reform_2022.in_effect,
            needs_test_eligible,
            gross_income_eligible & needs_test_eligible,
        )
