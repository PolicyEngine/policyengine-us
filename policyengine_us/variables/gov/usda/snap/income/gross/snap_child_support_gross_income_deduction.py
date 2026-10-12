from policyengine_us.model_api import *


class snap_child_support_gross_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction from gross income"
    unit = USD
    documentation = (
        "Legally obligated child support payments excluded from SNAP gross "
        "income in states that take the child support exclusion option"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#e_4",
        "https://www.law.cornell.edu/cfr/text/7/273.9#c_17",
    )

    def formula(spm_unit, period, parameters):
        child_support = spm_unit("snap_countable_child_support_expense", period)
        state = spm_unit.household("state_code_str", period)
        is_deductible = parameters(
            period
        ).gov.usda.snap.income.deductions.child_support[state]
        return is_deductible * child_support
