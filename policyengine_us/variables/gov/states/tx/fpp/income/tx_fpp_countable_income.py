from policyengine_us.model_api import *


class tx_fpp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program countable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-382-109",
        "https://www.hhs.texas.gov/handbooks/family-planning-program-policy-manual/4100-client-eligibility-screening-process",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "tx_fpp_countable_earned_income",
                "tx_fpp_countable_unearned_income",
            ],
        )
        care_deduction = spm_unit("tx_fpp_dependent_care_deduction", period)
        # Per 1 TAC 382.109(2)(C), child support payments made by a
        # household member are deducted.
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        return max_(income - care_deduction - child_support_paid, 0)
