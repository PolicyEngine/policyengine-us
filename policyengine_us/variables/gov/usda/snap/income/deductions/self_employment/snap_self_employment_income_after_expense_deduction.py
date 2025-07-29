from policyengine_us.model_api import *


class snap_self_employment_income_after_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Self-employment income after the SNAP self-employment expense deduction"
    unit = USD
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        self_employment_income = add(
            spm_unit, period, ["self_employment_income"]
        )
        expense_deduction = spm_unit(
            "snap_self_employment_expense_deduction", period
        )
        return max_(self_employment_income - expense_deduction, 0)
