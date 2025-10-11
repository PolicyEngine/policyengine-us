from policyengine_us.model_api import *


class md_tanf_countable_gross_earned_income(Variable):
    value_type = int
    entity = SPMUnit
    label = "Maryland TANF countable gross earned income"
    unit = USD
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.tanf.income.sources
        gross_earned = add(spm_unit, period, p.earned)
        return gross_earned
