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

        # Child support passthrough: first $50 is excluded
        countable_child_support = max_(
            child_support - p.child_support_passthrough, 0
        )

        # Unearned income minus child support already counted,
        # plus countable portion of child support
        other_unearned = gross_unearned - child_support
        return other_unearned + countable_child_support
