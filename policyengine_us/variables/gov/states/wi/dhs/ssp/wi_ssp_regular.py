from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class wi_ssp_regular(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin basic state SSI supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "wi_ssp_eligible"
    reference = "https://www.dhs.wisconsin.gov/dms/memos/ops/dms-ops-2026-12.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp
        eligible = person("wi_ssp_eligible", period)
        eligible_couple = (
            _ssi_couple_total(person, period.this_year, eligible.astype(int)) == 2
        )
        # The one-eligible-spouse rate requires an SSI-ineligible spouse. A spouse
        # who is SSI-eligible but excluded from the state payment leaves the
        # recipient on the individual rate.
        ineligible_spouse = person("is_ssi_ineligible_spouse", period.this_year)
        has_ineligible_spouse = (
            _ssi_couple_total(person, period.this_year, ineligible_spouse.astype(int))
            - ineligible_spouse
        ) > 0
        arrangement = person("ssi_federal_living_arrangement", period)
        other_household = (
            arrangement == arrangement.possible_values.ANOTHER_PERSONS_HOUSEHOLD
        )
        with_ineligible_spouse = where(
            other_household,
            p.amount.ineligible_spouse_other_household,
            p.amount.ineligible_spouse_independent,
        )
        return select(
            [eligible_couple, has_ineligible_spouse],
            [p.amount.couple / 2, with_ineligible_spouse],
            default=p.amount.individual,
        )
