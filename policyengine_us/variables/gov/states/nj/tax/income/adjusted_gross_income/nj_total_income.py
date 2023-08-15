from policyengine_us.model_api import *


class nj_total_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey total income by person"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/"
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        nj_additions = person("nj_agi_additions", period)
        nj_subtractions = person("nj_agi_subtractions", period)
        return max_(0, agi + nj_additions - nj_subtractions)
