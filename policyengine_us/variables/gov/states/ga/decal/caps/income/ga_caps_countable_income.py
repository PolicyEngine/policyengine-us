from policyengine_us.model_api import *


class ga_caps_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia CAPS countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=49"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.income.countable_income
        person = spm_unit.members
        is_adult = person("is_adult", period.this_year)
        person_income = add(person, period, p.sources)
        return spm_unit.sum(person_income * is_adult)
