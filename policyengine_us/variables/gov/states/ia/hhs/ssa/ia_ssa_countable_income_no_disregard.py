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
        # Iowa RCF and IHHRC do not allow the SSI $20 general income disregard
        # (GL 6-B-46 pp. 36, 54-58). Reverse what _apply_ssi_exclusions
        # actually applied. The exclusion bases must mirror
        # ssi_countable_income exactly: unearned = marital unearned + parent
        # deemed + ISM; earned = marital earned − blind/disabled working
        # student exclusion (clamped at 0). The $20 falls first on the
        # unearned base; any leftover applies inside the earned flat exclusion
        # ($65 + leftover) before the 50% earned-share rule, so the
        # earned-side add-back is reduced by (1 − earned_share). Couple
        # computation halves countable per person; mirror that by dividing
        # the add-back by marital-unit size when it applies.
        p = parameters(period).gov.ssa.ssi.income.exclusions
        countable_monthly = person("ssi_countable_income", period)
        marital_unearned = person("ssi_marital_unearned_income", period)
        parent_deemed = person(
            "ssi_unearned_income_deemed_from_ineligible_parent", period
        )
        ism = person("ssi_in_kind_support_and_maintenance", period)
        unearned_basis = marital_unearned + parent_deemed + ism
        marital_earned = person("ssi_marital_earned_income", period)
        student_excl = person("ssi_blind_or_disabled_working_student_exclusion", period)
        earned_basis = max_(marital_earned - student_excl, 0)
        applied_to_unearned = min_(p.general, unearned_basis)
        leftover = p.general - applied_to_unearned
        applied_to_earned = min_(leftover, max_(earned_basis - p.earned, 0))
        addback = applied_to_unearned + applied_to_earned * (1 - p.earned_share)
        couple = person("ssi_couple_computation_applies", period.this_year)
        nb_in_unit = person.marital_unit.nb_persons()
        return countable_monthly + where(couple, addback / nb_in_unit, addback)
