from policyengine_us.model_api import *

class al_tanf_work_expense_deduction(Variable):
    value_type = float
    entity = USD
    label = "Alabama TANF Work Expense Deduction"
    defined_for = StateCode.AL
    definition_period = YEAR

def formula(tax_unit, period, parameters):
        # Using the deduction rates defined in rate.yaml
        p = parameters(period).dhs.income.rate.values.deduction_percentage
        # Add the misc_deduction variable
        misc_expense = add(tax_unit, period, ["misc_deduction"])
        # Calculate work expense deductions
        work_expense_deduction = misc_expense * p
        
        return work_expense_deduction