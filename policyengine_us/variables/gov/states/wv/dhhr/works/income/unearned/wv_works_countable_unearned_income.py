from policyengine_us.model_api import *


class wv_works_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://bfa.wv.gov/media/2766/download?inline#page=587"
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.works.income
        # Step 4: Total all child support received
        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )
        # Step 5: Subtract child support pass-through ($100 for 1 child, $200 for 2+)
        dependent_children = spm_unit(
            "spm_unit_count_children", period.this_year
        )
        # Use select instead of bracket calc for clarity
        child_support_disregard = select(
            [dependent_children >= 2, dependent_children >= 1],
            [
                p.child_support_disregard.calc(2),
                p.child_support_disregard.calc(1),
            ],
            default=0,
        )
        actual_disregard = min_(
            child_support_disregard, child_support_received
        )
        countable_child_support = child_support_received - actual_disregard
        # Step 6: Add all other countable unearned income
        other_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Subtract child support since it's already counted above
        other_unearned_without_cs = other_unearned - child_support_received
        return max_(countable_child_support + other_unearned_without_cs, 0)
