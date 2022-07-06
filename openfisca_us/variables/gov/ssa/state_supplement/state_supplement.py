from openfisca_us.model_api import *


class state_supplement(Variable):
    value_type = float
    entity = Person
    label = "SSI State Supplement"
    definition_period = YEAR
    documentation = (
        "SSI State Supplement for this person (split equally between couples)."
    )

    def formula(person, period, parameters):
<<<<<<< HEAD
        marital_unit = person.marital_unit
        ssi_eligible_people = marital_unit("ssi_eligible_people", period)
        marital_unit_ssp = marital_unit(
            "marital_unit_state_supplement", period
        )
        return where(
            ssi_eligible_people > 0, marital_unit_ssp / ssi_eligible_people, 0
=======
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
>>>>>>> f909fcb9f2caa11ac0da2eccd9a37fdbbfaba246
        )
