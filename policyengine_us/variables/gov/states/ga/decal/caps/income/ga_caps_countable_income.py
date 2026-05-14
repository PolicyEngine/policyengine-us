from policyengine_us.model_api import *


class ga_caps_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia CAPS countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=48"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.income.countable_income
        sources = p.sources
        person = spm_unit.members
        is_adult = person("is_adult", period.this_year)
        adult_income = sum(person(source, period) * is_adult for source in sources)
        return spm_unit.sum(adult_income)
