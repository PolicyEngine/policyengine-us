from policyengine_us.model_api import *


class ak_atap_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.400",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Per 7 AAC 45.400, recipients must surrender child support payments
        # to Child Support Services Agency but may retain up to $50 monthly.
        p = parameters(period).gov.states.ak.dpa.atap.income
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        # Exclude up to $50 of child support (deduction)
        child_support_exclusion = min_(
            child_support, p.deductions.child_support
        )
        return gross_unearned - child_support_exclusion
