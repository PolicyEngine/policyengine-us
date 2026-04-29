from policyengine_us.model_api import *


class ak_ssp(Variable):
    value_type = float
    entity = Person
    label = "Alaska Adult Public Assistance"
    unit = USD
    definition_period = YEAR
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
        return where(
            claim_type == claim_type_values.COUPLE_BOTH_ELIGIBLE,
            person.marital_unit.sum(state_supplement) / 2,
            state_supplement,
        )
