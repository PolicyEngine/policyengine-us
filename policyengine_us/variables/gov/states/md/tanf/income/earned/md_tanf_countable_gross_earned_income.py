from policyengine_us.model_api import *


class md_tanf_countable_gross_earned_income(Variable):
    value_type = int
    entity = SPMUnit
    label = "Maryland TANF countable gross earned income"
    unit = USD
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.tanf.income.sources
        person = spm_unit.members
        gross_earned = person("earned_income", period)
        return spm_unit.sum{gross_earned}
