from policyengine_us.model_api import *


class tx_tanf_recognizable_needs_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF recognizable needs test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Recognizable needs test applies to continuing recipients
        # Household passes if recognizable needs > countable income

        budgetary_needs = spm_unit("tx_tanf_budgetary_needs", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)
        p = parameters(period).gov.states.tx.tanf.needs_standard

        # Recognizable needs is 25% of budgetary needs
        recognizable_needs = budgetary_needs * p.recognizable_needs.rate

        return countable_income < recognizable_needs
