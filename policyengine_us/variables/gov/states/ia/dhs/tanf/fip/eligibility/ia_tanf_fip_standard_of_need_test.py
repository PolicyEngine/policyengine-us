from policyengine_us.model_api import *


class ia_tanf_fip_standard_of_need_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP Standard of Need test"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.27"
    documentation = (
        "Families pass this test if countable income is below 185% of "
        "living costs for their family size. Passing qualifies them for "
        "the 50% work incentive deduction."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Get countable income for Standard of Need test (after 20% deduction)
        countable_income = spm_unit(
            "ia_tanf_fip_countable_income_for_standard_of_need", period
        )

        # Get income limit (185% of living costs)
        income_limit = spm_unit("ia_tanf_fip_income_limit", period)

        # Pass if countable income is below the limit
        return countable_income < income_limit
