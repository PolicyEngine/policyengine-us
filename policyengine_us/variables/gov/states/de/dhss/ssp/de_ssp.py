from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class de_ssp(Variable):
    value_type = float
    entity = Person
    label = "Delaware State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "de_ssp_eligible"
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415008PHI",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dhss.ssp.amount
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("de_ssp_eligible", period)
        is_couple = joint_claim & (
            _ssi_couple_total(person, period.this_year, eligible.astype(int)) == 2
        )
        per_person_amount = where(is_couple, p.couple / 2, p.individual)
        uncapped_ssi = person("uncapped_ssi", period)
        reduction = max_(0, -uncapped_ssi)
        supplement = max_(0, per_person_amount - reduction)
        return where(
            is_couple,
            _ssi_couple_total(person, period.this_year, supplement) / 2,
            supplement,
        )
