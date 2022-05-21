from openfisca_us.model_api import *


class marital_unit_state_supplement(Variable):
    value_type = float
    entity = MaritalUnit
    label = "Marital unit's State Supplement"
    definition_period = YEAR

    def formula(marital_unit, period, parameters):
        uncapped_ssi = marital_unit("uncapped_ssi", period)
        reduction_after_ssi = max_(0, -uncapped_ssi)
        maximum_ss = add(marital_unit, period, ["maximum_state_supplement"])
        marital_unit_ss = max_(0, maximum_ss - reduction_after_ssi)
        eligible = marital_unit("ssi_eligible_people", period) > 0
        return eligible * marital_unit_ss
