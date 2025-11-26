from policyengine_us.model_api import *


class tx_tanf_budgetary_needs_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF budgetary needs test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Budgetary needs test applies to applicants (not receiving TANF in last 4 months)
        # Household passes if budgetary needs > income

        budgetary_needs = spm_unit("tx_tanf_budgetary_needs", period)
        income_for_test = spm_unit(
            "tx_tanf_income_for_budgetary_needs_test", period
        )

        return budgetary_needs > income_for_test
