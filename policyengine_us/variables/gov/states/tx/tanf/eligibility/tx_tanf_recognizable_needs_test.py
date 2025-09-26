from policyengine_us.model_api import *


class tx_tanf_recognizable_needs_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Passes Texas TANF recognizable needs test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Part B test for all households
        size = spm_unit("tx_tanf_assistance_unit_size", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)
        p = parameters(period).gov.states.tx.tanf.payment_standard

        recognizable_needs = p.recognizable_needs.calc(size)

        # Calculate unmet need
        unmet_need = recognizable_needs - countable_income

        # Eligible if unmet need is one cent or more
        return unmet_need >= 0.01
