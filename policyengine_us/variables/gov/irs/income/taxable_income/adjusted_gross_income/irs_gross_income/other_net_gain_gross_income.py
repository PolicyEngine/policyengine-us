from policyengine_us.model_api import *


class other_net_gain_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Allocated other net gain included in gross income"
    unit = USD
    documentation = "Positive Form 4797 other net gain allocated across primary tax-unit filers for gross-income calculations."
    definition_period = YEAR
    reference = "https://www.irs.gov/instructions/i461"

    def formula(person, period, parameters):
        # other_net_gain_person splits the tax unit's net amount equally
        # between the head and spouse, so its positive part is each one's
        # share of a positive tax-unit gain.
        return max_(0, person("other_net_gain_person", period))
