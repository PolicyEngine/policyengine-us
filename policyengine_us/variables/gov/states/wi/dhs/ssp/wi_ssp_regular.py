from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class wi_ssp_regular(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin basic state SSI supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "wi_ssp_eligible"
    reference = "https://www.dhs.wisconsin.gov/dms/memos/ops/dms-ops-2026-12.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp
        eligible = person("wi_ssp_eligible", period)
        eligible_couple = person.marital_unit.sum(eligible) == 2
        has_spouse = person.marital_unit.nb_persons() == 2
        arrangement = person("ssi_federal_living_arrangement", period)
        other_household = (
            arrangement == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
        )
        with_ineligible_spouse = where(
            other_household,
            p.amount.ineligible_spouse_other_household,
            p.amount.ineligible_spouse_independent,
        )
        base = select(
            [eligible_couple, has_spouse],
            [p.amount.couple / 2, with_ineligible_spouse],
            default=p.amount.individual,
        )
        return base
