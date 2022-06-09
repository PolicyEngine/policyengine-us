from openfisca_us.model_api import *


class state_supplement(Variable):
    value_type = float
    entity = Person
    label = "State Supplement"
    definition_period = YEAR

    def formula(person, period, parameters):
        uncapped_ssi = person("uncapped_ssi", period)
        reduction_after_ssi = max_(0, -uncapped_ssi)
        maximum_ss = person("maximum_state_supplement", period)
        state_supplement = max_(0, maximum_ss - reduction_after_ssi)
        eligible = person("is_ssi_aged_blind_disabled", period)
        joint_claim = person("ssi_claim_is_joint", period)
        return eligible * where(
            joint_claim,
            person.marital_unit.sum(state_supplement) / 2,
            state_supplement,
        )
