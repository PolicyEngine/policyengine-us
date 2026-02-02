from policyengine_us.model_api import *


class nm_works_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support_deduction = spm_unit(
            "nm_works_child_support_deduction", period
        )
        return max_(gross_unearned - child_support_deduction, 0)
