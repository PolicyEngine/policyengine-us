from policyengine_us.model_api import *


class ia_ssa_countable_income_no_disregard(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA monthly countable income, without the SSI $20 general income disregard"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/15607/download",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf#page=2",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/20/416.1112",
    )

    def formula(person, period, parameters):
        # Iowa RCF and IHHRC do not allow the SSI $20 general income
        # disregard (GL 6-B-46 pp. 36, 54-58). ssi_countable_income already
        # applies the disregard in _apply_ssi_exclusions, so reverse what
        # SSI actually applied per 20 CFR § 416.1112: the $20 falls first on
        # unearned, and any leftover goes inside the earned flat exclusion
        # ($65 + leftover) before the 50% earned-share rule. The earned-side
        # add-back is therefore halved by (1 − earned_share).
        #
        # When the SSI couple computation applies, _apply_ssi_exclusions runs
        # on combined marital-unit income and the result is split per spouse,
        # so size the add-back by combined income and divide by marital-unit
        # size.
        p = parameters(period).gov.ssa.ssi.income.exclusions
        countable_monthly = (
            person("ssi_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        own_unearned_monthly = (
            person("ssi_unearned_income", period.this_year) / MONTHS_IN_YEAR
        )
        own_earned_monthly = max_(
            person("ssi_earned_income", period.this_year) / MONTHS_IN_YEAR, 0
        )
        couple = person("ssi_couple_computation_applies", period.this_year)
        nb_in_unit = person.marital_unit.nb_persons()
        unearned = where(
            couple,
            person.marital_unit.sum(own_unearned_monthly),
            own_unearned_monthly,
        )
        earned = where(
            couple,
            person.marital_unit.sum(own_earned_monthly),
            own_earned_monthly,
        )
        applied_to_unearned = min_(p.general, unearned)
        leftover = p.general - applied_to_unearned
        earned_above_flat = max_(earned - p.earned, 0)
        applied_to_earned = min_(leftover, earned_above_flat)
        addback = applied_to_unearned + applied_to_earned * (1 - p.earned_share)
        return countable_monthly + where(couple, addback / nb_in_unit, addback)
