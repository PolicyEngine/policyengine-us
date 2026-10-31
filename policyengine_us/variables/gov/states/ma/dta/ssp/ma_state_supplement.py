from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class ma_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts State Supplement payment amount"
    definition_period = MONTH
    defined_for = StateCode.MA
    exhaustive_parameter_dependencies = "gov.states.ma.dta.ssp"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-327-330"

    def formula(person, period, parameters):
        uncapped_ssi = person("uncapped_ssi", period)
        reduction_after_ssi = max_(0, -uncapped_ssi)
        maximum_ss = person("ma_maximum_state_supplement", period)
        state_supplement = max_(0, maximum_ss - reduction_after_ssi)
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        meets_resource_test = person("meets_ssi_resource_test", period)
        eligible = abd & meets_resource_test
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        couple_supplement = _ssi_couple_total(
            person, period.this_year, state_supplement
        )
        return where(
            joint_claim,
            couple_supplement / 2,
            state_supplement * eligible,
        )
