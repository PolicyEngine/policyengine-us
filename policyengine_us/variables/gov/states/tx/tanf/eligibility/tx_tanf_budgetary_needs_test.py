from policyengine_us.model_api import *


class tx_tanf_budgetary_needs_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Passes Texas TANF budgetary needs test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Budgetary needs test applies to applicants (not receiving TANF in last 4 months)
        # Household passes if budgetary needs > countable income

        budgetary_needs = spm_unit("tx_tanf_budgetary_needs", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)

        return budgetary_needs > countable_income
