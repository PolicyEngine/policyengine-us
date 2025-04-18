from policyengine_us.model_api import *


class ma_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts State Supplement payment amount"
    definition_period = YEAR
    exhaustive_parameter_dependencies = "gov.states.ma.dta.ssp"
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-327-330"
    )

    def formula(person, period, parameters):
        uncapped_ssi = person("uncapped_ssi", period)
        reduction_after_ssi = max_(0, -uncapped_ssi)
        maximum_ss = person("ma_maximum_state_supplement", period)
        state_supplement = max_(0, maximum_ss - reduction_after_ssi)
        abd = person("is_ssi_aged_blind_disabled", period)
        meets_resource_test = person("meets_ssi_resource_test", period)
        eligible = abd & meets_resource_test
        joint_claim = person("ssi_claim_is_joint", period)
        return where(
            joint_claim,
            person.marital_unit.sum(state_supplement) / 2,
            state_supplement * eligible,
        )
