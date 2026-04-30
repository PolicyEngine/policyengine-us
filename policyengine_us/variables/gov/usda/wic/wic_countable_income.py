from policyengine_us.model_api import *


class wic_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "WIC countable income"
    documentation = "SPM unit income counted for WIC direct income eligibility"
    reference = "https://www.law.cornell.edu/cfr/text/7/246.7#d_2_ii"

    def formula(spm_unit, period, parameters):
        sources = parameters(period).gov.usda.wic.income.sources
        person = spm_unit.members
        cash_income = add(spm_unit, period, sources)
        positive_capital_gains = spm_unit.sum(
            max_(0, person("capital_gains", period))
        )
        return cash_income + positive_capital_gains
