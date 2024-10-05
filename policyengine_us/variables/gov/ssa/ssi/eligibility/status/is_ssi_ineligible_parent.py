from policyengine_us.model_api import *


class is_ssi_ineligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible parent in respect of a child"
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)
        child = person("is_child", period)
        return ~eligible & ~child & (person.tax_unit.sum(eligible & child) > 0)
