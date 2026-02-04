from policyengine_us.model_api import *


class vt_reach_up_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per 33 V.S.A. Section 1103(a)(4)
        p = parameters(period).gov.states.vt.dcf.reach_up.income.deductions
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Child support is included in unearned income; apply disregard
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_disregard = min_(child_support, p.child_support)
        return max_(gross_unearned - child_support_disregard, 0)
