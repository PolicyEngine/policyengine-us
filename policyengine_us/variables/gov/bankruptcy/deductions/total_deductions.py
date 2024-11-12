from policyengine_us.model_api import *


class total_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Total deductions from Income"
    unit = USD
    definition_period = YEAR

    adds = ["national_standards_deductions","local_standards_deductions",
            "other_necessary_expenses_deductions","additional_expense_deductions",
            "debt_payment_deductions","additional_expense_deductions"]
