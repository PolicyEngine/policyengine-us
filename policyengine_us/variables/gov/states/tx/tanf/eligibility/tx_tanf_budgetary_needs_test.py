from policyengine_us.model_api import *


class tx_tanf_budgetary_needs_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Passes Texas TANF budgetary needs test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Applies to households not receiving TANF in last 4 months (applicants)
        # For simplicity, assuming all are applicants

        size = spm_unit("tx_tanf_assistance_unit_size", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)
        p = parameters(period).gov.states.tx.tanf.payment_standard

        budgetary_needs = p.budgetary_needs.calc(size)

        # Calculate unmet need
        unmet_need = budgetary_needs - countable_income

        # Ineligible if unmet need is less than 50 cents
        return unmet_need >= 0.50
