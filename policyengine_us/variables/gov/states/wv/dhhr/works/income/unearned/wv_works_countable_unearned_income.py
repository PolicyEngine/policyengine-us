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
        # Step 4-5: Child support disregard ($100 for 1 child, $200 for 2+)
        child_support = add(spm_unit, period, ["child_support_received"])
        children = spm_unit("spm_unit_count_children", period.this_year)
        max_disregard = p.child_support_disregard.calc(children)
        actual_disregard = min_(max_disregard, child_support)
        # Step 6: Gross unearned (includes child support) minus disregard
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        return max_(gross_unearned - actual_disregard, 0)
