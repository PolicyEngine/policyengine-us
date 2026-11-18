from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_marital_both_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Both spouses meet SSI age, blindness, or disability criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)
        spouse = _ssi_spouse_index(person, period)
        return eligible & (spouse >= 0) & eligible[np.maximum(spouse, 0)]
