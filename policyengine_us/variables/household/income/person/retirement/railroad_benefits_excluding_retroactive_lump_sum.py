from policyengine_us.model_api import *


class railroad_benefits_excluding_retroactive_lump_sum(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement benefits excluding retroactive lump sums"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        gross = person("railroad_benefits", period)
        lump_sum = person("railroad_benefits_retroactive_lump_sum", period)
        return max_(gross - lump_sum, 0)
