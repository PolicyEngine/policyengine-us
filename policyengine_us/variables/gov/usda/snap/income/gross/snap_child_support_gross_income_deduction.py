from policyengine_us.model_api import *


class snap_child_support_gross_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction from gross income"
    unit = USD
    documentation = (
        "Deduction for child support payments when computing SNAP gross income"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    def formula(spm_unit, period, parameters):
        child_support = add(spm_unit, period, ["child_support_expense"])
        state = spm_unit.household("state_code_str", period)
        is_deductible = parameters(
            period
        ).gov.usda.snap.income.deductions.child_support[state]
        return is_deductible * child_support
