from policyengine_us.model_api import *


class al_tanf_work_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF Work Expense Deduction"
    defined_for = StateCode.AL
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Using the deduction rates defined in rate.yaml
        p = parameters(period).gov.states.al.dhs.tanf.income
        # Add the misc_deduction variable
        misc_expense = add(spm_unit, period, ["misc_deduction"])
        # Calculate and return work expense deductions
        return misc_expense * p.rate
