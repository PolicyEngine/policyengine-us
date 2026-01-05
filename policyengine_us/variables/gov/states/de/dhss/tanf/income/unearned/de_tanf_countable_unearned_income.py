from policyengine_us.model_api import *


class de_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf#page=6",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Gross unearned income minus $50 child support disregard
        p = parameters(period).gov.states.de.dhss.tanf.income
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_disregard = min_(
            child_support, p.deductions.child_support
        )
        return max_(gross_unearned - child_support_disregard, 0)
