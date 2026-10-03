from policyengine_us.model_api import *


class id_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP countable annual income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=5,6,7"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.income
        person = spm_unit.members
        # Annual income approximates a stable prior-month assessment. Existing
        # net business inputs are used without another expense deduction; losses
        # do not offset other income under this common modeling approximation.
        earned = sum(max_(person(source, period), 0) for source in p.sources.earned)
        adult = person("age", period) >= p.earned_income_min_age
        earned = spm_unit.sum(where(adult, earned, 0))
        unearned = add(spm_unit, period, p.sources.unearned)
        # Income of nonqualified members counts. The plan excludes child support,
        # VA and general assistance. Jury duty, WIA, mortgage/royalty receipts and
        # irregular gifts/lottery winnings over $30 in the prior month lack
        # separately identified inputs; they are unmodeled, not legal exclusions.
        return max_(earned + unearned, 0)
