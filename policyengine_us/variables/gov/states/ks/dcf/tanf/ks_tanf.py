from policyengine_us.model_api import *


class ks_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm6220.htm",
    )
    defined_for = "ks_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-100 and KEESM 6220(4)(b):
        # Benefit = payment standard - countable income. Assigned child support
        # is retained by the state, so it is counted only for the income
        # eligibility test and excluded from the payment amount:
        # "If eligible, the support shall be excluded in determining the amount
        # of payment."
        maximum_benefit = spm_unit("ks_tanf_maximum_benefit", period)
        countable_income = spm_unit("ks_tanf_countable_income", period)
        assigned_child_support = add(spm_unit, period, ["child_support_received"])
        benefit_countable_income = countable_income - assigned_child_support
        return max_(maximum_benefit - benefit_countable_income, 0)
