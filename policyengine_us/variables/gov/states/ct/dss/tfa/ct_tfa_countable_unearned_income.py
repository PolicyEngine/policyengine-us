"""
Connecticut TFA countable unearned income after exclusions.
"""

from policyengine_us.model_api import *


class ct_tfa_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA countable unearned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut TFA unearned income after applying exclusions. "
        "Unearned income is generally counted dollar-for-dollar, with the "
        "exception that the first $50 of child support is passed through and excluded."
    )
    reference = (
        "SSA POMS SI BOS00830.403 - TANF - Connecticut, Child Support Provisions; "
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830403BOS"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa

        gross_unearned = spm_unit("ct_tfa_gross_unearned_income", period)

        # Child support passthrough exclusion
        child_support = spm_unit("child_support_received", period)
        passthrough = p.income_disregards.child_support_passthrough
        child_support_exclusion = min_(child_support, passthrough)

        # Countable unearned income
        countable = max_(gross_unearned - child_support_exclusion, 0)

        return countable
