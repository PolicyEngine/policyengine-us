from policyengine_us.model_api import *


class nj_wfnj_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.wfnj.income
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        num_children = spm_unit("spm_unit_count_children", period.this_year)
        max_disregard = p.child_support_disregard.calc(num_children)
        child_support_disregard = min_(child_support, max_disregard)
        return max_(gross_unearned - child_support_disregard, 0)
