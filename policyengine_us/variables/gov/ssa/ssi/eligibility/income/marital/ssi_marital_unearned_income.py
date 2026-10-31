from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_marital_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Total SSI unearned income for a marital unit"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1802#p-416.1802(b)(1)"
    )

    def formula(person, period, parameters):
        # 416.1802(b)(1): with an eligible spouse 'we will count your combined
        # income'. Combine the two spouses, not every member of the unit.
        couple_computation = person("ssi_couple_computation_applies", period)
        unearned_income = person("ssi_unearned_income", period)
        spouse = np.maximum(_ssi_spouse_index(person, period), 0)
        return unearned_income + where(couple_computation, unearned_income[spouse], 0)
