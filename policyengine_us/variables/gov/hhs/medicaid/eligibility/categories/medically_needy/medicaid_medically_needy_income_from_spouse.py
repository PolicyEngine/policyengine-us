from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._couple_standard import (
    spouses_split_by_facility,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class medicaid_medically_needy_income_from_spouse(Variable):
    value_type = float
    entity = Person
    label = (
        "Adjustment to SSI countable income for a spouse's income in Medicaid's "
        "medically needy program"
    )
    unit = USD
    documentation = (
        "Amount added to ssi_countable_income so that the medically needy test "
        "counts a spouse's income by the state's method. A state that budgets a "
        "couple together counts the spouse's income with no deeming threshold, "
        "after SSI's allocations for ineligible children (20 CFR 416.1163(b)), in "
        "place of SSI's deemed amount. A couple split by a facility counts no "
        "spouse income, so the amount removes SSI's deemed amount and can be "
        "negative. It is zero otherwise."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.law.cornell.edu/uscode/text/42/1396r-5",
    )

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.medically_needy.limit.income
        budgets_together = p.budgets_couple_together[state].astype(bool)
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period)
        # What remains of the spouse's income after the allocations for
        # ineligible children (20 CFR 416.1163(b)), before SSI's threshold.
        # Arkansas MS O-531 deducts a living allowance for each ineligible child
        # from the spouse's income in the same way.
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        alone = _apply_ssi_exclusions(earned, unearned, parameters, period)
        combined = _apply_ssi_exclusions(
            earned + spouse_earned, unearned + spouse_unearned, parameters, period
        )
        split = spouses_split_by_facility(person, period)
        budgeted_together = budgets_together & person(
            "is_ssi_aged_blind_disabled", period
        )
        counted = where(budgeted_together & ~split, max_(combined - alone, 0), 0)
        # ssi_countable_income already holds SSI's deemed amount, which starts at
        # SSI's threshold. Subtracting it leaves one method at every income, with
        # no jump at that threshold.
        deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
        return where(budgeted_together | split, counted - deemed, 0)
