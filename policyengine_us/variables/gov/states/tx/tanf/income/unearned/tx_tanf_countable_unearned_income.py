from policyengine_us.model_api import *


class tx_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-605",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Sum person-level gross unearned income
        gross_unearned = add(
            spm_unit, period, ["tx_tanf_gross_unearned_income"]
        )

        # Apply household-level child support deduction (up to $75/month per household)
        child_support_deduction = spm_unit(
            "tx_tanf_child_support_deduction", period
        )

        return max_(gross_unearned - child_support_deduction, 0)
