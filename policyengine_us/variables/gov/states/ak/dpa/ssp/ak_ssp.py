from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class ak_ssp(Variable):
    value_type = float
    entity = Person
    label = "Alaska Adult Public Assistance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.AK
    exhaustive_parameter_dependencies = "gov.states.ak.dpa.ssp"
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=1",
        "https://www.akleg.gov/basis/statutes.asp#47.25.430",
    )

    def formula(person, period):
        # uncapped_ssi can be negative when countable income exceeds the
        # federal SSI benefit. The negative portion reduces the state supplement.
        uncapped_ssi = person("uncapped_ssi", period)
        payment_standard = person("ak_ssp_payment_standard", period)
        claim_type = person("ak_ssp_claim_type", period)
        income_excess = max_(0, -uncapped_ssi)
        state_supplement = max_(0, payment_standard - income_excess) * person(
            "ak_ssp_eligible", period
        )
        claim_type_values = claim_type.possible_values
        couple_supplement = _ssi_couple_total(
            person, period.this_year, state_supplement
        )
        return where(
            claim_type == claim_type_values.COUPLE_BOTH_ELIGIBLE,
            couple_supplement / 2,
            state_supplement,
        )
