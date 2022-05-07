from openfisca_us.model_api import *


class snap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for child support payments"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    def formula(spm_unit, period, parameters):
        child_support = add(spm_unit, period, ["child_support_expense"])
        state = spm_unit.household("state_code_str", period)
        is_deductible = parameters(
            period
        ).usda.snap.income.deductions.child_support[state]
        return where(is_deductible, child_support, 0)
