from openfisca_us.model_api import *


class state_supplement(Variable):
    value_type = float
    entity = Person
    label = "State Supplement"
    definition_period = YEAR

    def formula(person, period, parameters):
        marital_unit = person.marital_unit
        uncapped_ssi = marital_unit("uncapped_ssi", period)
        reduction_after_ssi = max_(0, -uncapped_ssi)
        maximum_ss = add(marital_unit, period, ["maximum_state_supplement"])
        marital_unit_ss = max_(0, maximum_ss - reduction_after_ssi)
        eligible = person("is_ssi_aged_blind_disabled", period)
        num_eligible = marital_unit.sum(eligible)
        return eligible * marital_unit_ss * where(num_eligible > 1, 1 / 2, 1)
